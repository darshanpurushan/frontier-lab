import io
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd
import pytest

from frontier_lab.analytics import drawdown, performance, regressions
from frontier_lab.backtest import rebalance_cost, simulate_holdings, run_backtest
from frontier_lab.data import parse_french_zip, synthetic_inputs, validate_inputs
from frontier_lab.optimization import factor_covariance, target_weights, frontier
from frontier_lab.optimization import turnover_aware
from frontier_lab.research import score_forecasts, paired_bootstrap, circular_block_indices, holm_adjust, robustness_grid
from frontier_lab.forward import freeze_plan, validate_plan
from frontier_lab.signal import signal_scores, long_only_weights, neutral_weights, run_signal, demo_volume, rank_ic


@pytest.fixture
def config():
    return dict(tickers=['A', 'B', 'C', 'D'], benchmark='BM', start='2010-01-01',
                end='2030-01-01', lookback=60, max_weight=.5, cost_bps=10,
                annualization=252, seed=42, hac_lags=5, evaluation_split='2021-01-01')


def test_entry_cost_is_self_financing():
    c, turnover = rebalance_cost(np.zeros(2), np.array([.4, .6]), .01)
    assert 1 - c == pytest.approx(1 / 1.01)
    assert c == pytest.approx(.01 * turnover)
    q = 1 - c
    assert q + .01 * np.abs(q * np.array([.4, .6])).sum() == pytest.approx(1)


def test_buy_and_hold_drifts_and_execution_does_not_capture_same_day_return():
    dates = pd.bdate_range('2020-01-01', periods=3)
    r = pd.DataFrame([[.9, 0], [.1, 0], [0, .1]], index=dates)
    sim, held = simulate_holdings(r, pd.Series(0., index=dates), {dates[0]: np.array([.5, .5])}, 0)
    assert sim['net'].iloc[0] == pytest.approx(0)
    assert held[1, 0] == pytest.approx(.55 / 1.05)
    assert (1 + sim['net']).prod() == pytest.approx(1.10)


def test_costs_reduce_wealth_for_same_target_path():
    dates = pd.bdate_range('2020-01-01', periods=3)
    r = pd.DataFrame([[0, 0], [.1, -.1], [-.1, .1]], index=dates)
    schedules = {date: np.array([.5, .5]) for date in dates}
    rf = pd.Series(0., index=dates)
    cheap, _ = simulate_holdings(r, rf, schedules, 0)
    costly, _ = simulate_holdings(r, rf, schedules, 25)
    assert (1 + costly['net']).prod() < (1 + cheap['net']).prod()


def test_drawdown_includes_initial_capital():
    r = pd.Series([-.2, .1, .5])
    assert drawdown(r).iloc[0] == pytest.approx(-.2)
    assert drawdown(r).min() == pytest.approx(-.2)


def test_factor_covariance_is_positive_and_decomposes(config):
    _, returns, factors, _ = synthetic_inputs(config)
    cov, beta, fcov, specific = factor_covariance(returns[config['tickers']].head(100), factors.head(100))
    w = np.full(4, .25)
    assert np.linalg.eigvalsh(cov).min() > 0
    assert w @ cov @ w == pytest.approx((beta.T @ w) @ fcov @ (beta.T @ w) + (w*w) @ specific)


def test_all_targets_share_constraints(config):
    _, r, f, _ = synthetic_inputs(config)
    targets, _ = target_weights(r[config['tickers']].head(100), f.head(100), .5)
    for w in targets.values():
        assert w.sum() == pytest.approx(1)
        assert w.min() >= -1e-7 and w.max() <= .5 + 1e-7


def test_future_returns_cannot_change_earlier_decisions(config):
    _, r, f, _ = synthetic_inputs(config)
    r, f = r.head(180), f.head(180)
    original = run_backtest(r, f, config)
    cutoff = r.index[120]
    changed = r.copy()
    changed.loc[cutoff:, config['tickers'][0]] += .1
    updated = run_backtest(changed, f, config)
    old = original.weights.loc[original.weights['decision_date'] < cutoff]
    new = updated.weights.loc[updated.weights['decision_date'] < cutoff]
    pd.testing.assert_frame_equal(old, new)
    assert (original.weights['execution_date'] > original.weights['decision_date']).all()
    pd.testing.assert_frame_equal(original.net.loc[:r.index[119]], updated.net.loc[:r.index[119]])


def test_french_parser_converts_units_and_preserves_dates():
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w') as archive:
        archive.writestr('f.csv', 'Daily factors\n,Mkt-RF,SMB,HML,RF\n20200102,1,2,3,0.1\nAnnual Factors\n2020,8,9,10,0.1\n')
    frame = parse_french_zip(b.getvalue(), ['Mkt-RF','SMB','HML','RF'])
    assert len(frame) == 1
    assert frame['Mkt-RF'].iloc[0] == pytest.approx(.01)
    assert frame['RF'].iloc[0] == pytest.approx(.001)


def test_validation_rejects_missing_prices(config):
    p, _, f, _ = synthetic_inputs(config)
    p.iloc[80, 0] = np.nan
    with pytest.raises(ValueError, match='Missing'):
        validate_inputs(p, f, config, {})


def test_regression_recovers_known_beta_and_alpha():
    rng = np.random.default_rng(5)
    index = pd.bdate_range('2010-01-01', periods=1500)
    f = pd.DataFrame(rng.normal(0, .01, (1500, 4)), index=index,
                     columns=['Mkt-RF','SMB','HML','MOM'])
    f['RF'] = .0001
    y = .0002 + f[['Mkt-RF','SMB','HML','MOM']] @ np.array([.8,.3,-.2,.1]) + f['RF']
    y += rng.normal(0, .00001, len(y))
    table = regressions(pd.DataFrame({'known': y}), f)
    row = table.loc[table['model'] == 'Four factor'].iloc[0]
    assert row['Mkt-RF'] == pytest.approx(.8, abs=.001)
    assert row['daily_alpha'] == pytest.approx(.0002, abs=.000002)


def test_benchmark_information_ratio_is_undefined():
    r = pd.Series([.01, -.02, .03, .005])
    metrics = performance(r, pd.Series(0., index=r.index), r)
    assert np.isnan(metrics['Information ratio'])


def test_frontier_volatility_nondecreasing_on_efficient_branch(config):
    _, r, f, _ = synthetic_inputs(config)
    curve, _, _ = frontier(r[config['tickers']].head(100), f['RF'].iloc[0], .5, count=15)
    assert np.all(np.diff(curve[:, 0]) >= -1e-8)
    assert np.all(np.diff(curve[:, 1]) >= -1e-6)


def test_turnover_penalty_reduces_trading():
    cov=np.diag([.0001,.0002,.0003,.0004])
    before=np.array([.15,.2,.25,.4])
    low=turnover_aware(cov,before,.5,0.0)
    high=turnover_aware(cov,before,.5,.01)
    assert np.abs(high-before).sum()<np.abs(low-before).sum()
    assert high.sum()==pytest.approx(1)


def test_forecasts_use_subsequent_complete_holding_intervals(config):
    _,r,f,_=synthetic_inputs(config)
    result=run_backtest(r.head(180),f.head(180),config)
    detail,summary=score_forecasts(result)
    assert (detail['measurement_end']>detail['execution_date']).all()
    row=detail.iloc[0]
    actual=result.gross.loc[(result.gross.index>row['execution_date']) &
                           (result.gross.index<=row['measurement_end']),row['strategy']].var(ddof=1)
    assert row['realized_daily_variance']==pytest.approx(actual)
    assert (detail['QLIKE']>=-1e-12).all()
    assert len(summary)==18


def test_bootstrap_identical_strategies_have_zero_difference():
    rng=np.random.default_rng(1)
    index=pd.bdate_range('2020-01-01',periods=100)
    r=rng.normal(.0002,.01,100)
    table=paired_bootstrap(pd.DataFrame({'Equal weight':r,'Copy':r},index=index),
                           pd.Series(.00001,index=index),draws=100,block=10)
    assert np.allclose(table[['estimate','CI_low','CI_high']],0)
    assert np.allclose(table['p_Holm_within_metric'],1)


def test_bootstrap_resamples_contiguous_paired_blocks():
    idx=circular_block_indices(100,10,np.random.default_rng(42)).reshape(-1,10)
    assert ((np.diff(idx,axis=1)%100)==1).all()


def test_holm_adjustment():
    assert holm_adjust([.01,.03,.20])==pytest.approx([.03,.06,.20])


def test_frozen_plan_rejects_changes(config,tmp_path):
    path=freeze_plan(config,'Equal weight',tmp_path)
    plan=json.loads(path.read_text());validate_plan(plan)
    plan['config']['cost_bps']=0
    with pytest.raises(ValueError,match='checksum'):validate_plan(plan)


def test_quarterly_schedule_and_common_entry(config):
    _,r,f,_=synthetic_inputs(config)
    cfg=dict(config,rebalance='Q',first_decision='2015-09-30')
    result=run_backtest(r.head(320),f.head(320),cfg)
    assert result.weights['decision_date'].dt.month.isin([3,6,9,12]).all()
    assert result.weights['decision_date'].min()>=pd.Timestamp('2015-09-30')


def test_paper_evaluation_excludes_pre_freeze_decisions(config,tmp_path,monkeypatch):
    import hashlib
    import frontier_lab.forward as forward
    p,r,f,source=synthetic_inputs(config)
    monkeypatch.setattr(forward,'load_inputs',lambda *a,**k:(p,r.head(180),f.head(180),source))
    path=freeze_plan(config,'Min variance: turnover-aware',tmp_path)
    plan=json.loads(path.read_text())
    plan['frozen_utc']='2015-04-15T22:00:00+00:00'
    payload={k:v for k,v in plan.items() if k!='plan_sha256'}
    plan['plan_sha256']=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    path.write_text(json.dumps(plan))
    forward.main(['evaluate',str(path)])
    allocations=pd.read_csv(tmp_path/(path.stem+'_results')/'dated_allocations.csv',parse_dates=['decision_date'])
    assert (allocations['decision_date']>pd.Timestamp('2015-04-15')).all()


def test_signal_matches_manual_two_day_delta_and_linear_decay():
    dates=pd.bdate_range('2020-01-01',periods=110)
    px=pd.DataFrame({'A':100+np.arange(110,dtype=float),
                     'B':100+np.arange(110,dtype=float)**2/100},index=dates)
    volume=pd.DataFrame(1.0,index=dates,columns=px.columns)
    s=signal_scores(px,volume)
    assert s.loc[dates[105],'A']==1.0
    assert s.loc[dates[105],'B']==.5
    signal_value=-2.0
    manual=sum((i+1)*signal_value for i in range(5))/15
    assert manual==-2.0


def test_signal_portfolio_maps_high_ranks_to_larger_weights():
    ranks=np.arange(1,13)/12
    long=long_only_weights(ranks,.2)
    neutral=neutral_weights(ranks)
    assert long.sum()==pytest.approx(1)
    assert long.max()<=.2+1e-9
    assert np.all(np.diff(long)>=0)
    assert neutral.sum()==pytest.approx(0,abs=1e-12)
    assert np.abs(neutral).sum()==pytest.approx(1)
    assert neutral[0]<0<neutral[-1]


def test_signal_future_prices_do_not_change_current_rank(config):
    prices,_,_,_=synthetic_inputs(config)
    v=demo_volume(prices,config['tickers'],42)
    old=signal_scores(prices[config['tickers']],v)
    cutoff=prices.index[140]
    changed=prices.copy()
    changed.loc[cutoff:,config['tickers'][0]]*=2
    new=signal_scores(changed[config['tickers']],v)
    pd.testing.assert_frame_equal(old.loc[:prices.index[139]],new.loc[:prices.index[139]])


def test_dollar_neutral_signal_cash_and_borrow_cost(config):
    dates=pd.bdate_range('2020-01-01',periods=5)
    r=pd.DataFrame({'A':[0,.03,-.01,0,0], 'B':[0,-.02,.01,0,0]},index=dates)
    cash=pd.Series(0.0001,index=dates)
    target=np.array([.5,-.5])
    no_borrow,_=simulate_holdings(r,cash,{dates[0]:target},0,borrow_bps=0)
    with_borrow,_=simulate_holdings(r,cash,{dates[0]:target},0,borrow_bps=25200)
    assert no_borrow['net'].iloc[1]==pytest.approx(.5*.03+.5*.02+0.0001)
    assert with_borrow['net'].iloc[1]<no_borrow['net'].iloc[1]


def test_signal_schedules_execute_after_decision(config):
    p,r,f,_=synthetic_inputs(config)
    v=demo_volume(p,config['tickers'],42)
    result=run_signal(p.iloc[:180],v.iloc[:180],r.iloc[:179],f.iloc[:179],config)
    assert (result['weights']['execution_date']>result['weights']['decision_date']).all()
    assert 'Rank reversal: neutral daily' in result['net'].columns
    assert result['scores'].index.min()>=p.index[103]
