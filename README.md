# Frontier Lab

**Walk-forward portfolio construction, risk forecasting, and factor attribution in Python.**

Can portfolio optimization beat a simple equal-weight portfolio after estimation error and trading costs? This project tests that question on observed Yahoo Finance prices and Kenneth French factors. It compares six allocation rules, evaluates risk forecasts against later returns, and reports uncertainty in performance differences. A separate price/volume reversal experiment tests a supplied rank signal.


Open `outputs/research_v2/report.html` and `outputs/etf_research_v2/report.html` for the full HTML reports. `publish_results.py` creates [`docs/HISTORICAL_RESULTS.md`](docs/HISTORICAL_RESULTS.md) and two GitHub-friendly figures from **observed** results only. Review them, then commit. It refuses synthetic runs and checks that published CAGR matches the daily net returns. If Yahoo rate limits you, rerun later; cached downloads are reused. `python3 run_project.py` runs just the main stock study and is suitable for Spyder (F5).

The checked-in snapshot contains launchers, publication code, and tests, but the `frontier_lab/` research package is missing. A fresh checkout therefore cannot run the study, synthetic demo, or full research test suite: they fail with `ModuleNotFoundError: No module named 'frontier_lab'`. Installing dependencies alone does not restore that project source. Recover the original package from a complete project revision before following the study commands below.

The standalone publication checks can be run with `python3 -m pytest -q tests/test_publication.py`. They validate local fixtures, not observed strategy performance. Earlier validation records describe historical environments and do not establish that this incomplete snapshot reproduces those runs. [Research evidence and status](VALIDATION.md) separates those records from the current checkout status.

## Research design

| Component | Specification |
| --- | --- |
| Stocks | GOOGL, AMZN, MSFT, AAPL, JPM, XOM, JNJ, PG, CAT, NEE, UNH, WMT |
| Independent universe check | Nine U.S. sector ETFs (`config_etf.json`) |
| Data window | 2010-01-01 to 2025-12-31, with the first 504 return observations reserved for estimation |
| Benchmark | SPY buy and hold from the same entry date |
| Rules | Equal weight; minimum variance with sample, Ledoit–Wolf, or four-factor covariance; maximum estimated Sharpe with shrinkage; turnover-aware minimum variance |
| Portfolio | Long only, fully invested, maximum 20% target weight per holding |
| Decisions and fills | Trailing-window month-end decisions, next-session-close execution, weight drift between rebalances |
| Costs | 10 bps per dollar bought or sold, including first entry; cost sensitivity at 0/10/25 bps |
| Evidence | Prospective risk forecast errors, factor regression with HAC intervals, paired block bootstrap, three training windows × two rebalance schedules, subperiod analysis |

`config.json` holds every core assumption. Prices use adjusted closes and simple daily returns; RF is the daily French risk-free rate. The model does not simulate market impact, bid-ask spreads, taxes, exact fills at the close, borrow availability, or historical index membership. The handpicked stock universe contains surviving firms, and the historical split is exploratory. See [METHODOLOGY.md](METHODOLOGY.md) and [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md).

## Outputs and reproducibility

`outputs/research_v2/` contains the portable HTML report, figures, daily gross and net returns, target weights with decision/execution dates, trading costs, factor attribution, risk forecasts, bootstrap intervals, robustness grid, and `manifest.json`. The manifest stores configuration, source date, input hashes, code hash, and package versions. Reports for the ETF study live under `outputs/etf_research_v2/`.

Downloaded data and full local outputs are intentionally excluded from Git. A checked-in historical summary is generated explicitly by `publish_results.py`, with source hashes for traceability. Do not claim that these are point-in-time reconstructed holdings; Yahoo adjusted prices can be revised.

For the price/volume signal experiment:

```bash
python3 run_signal.py
```

Open `outputs/signal_research/signal_report.html`. It evaluates `rank(ts_decay_linear(-ts_delta(close, 2) * (volume / ts_mean(volume, 100)), 5))` in a distinct experiment with rank IC, net/gross returns, transaction costs, turnover, and a dollar-neutral alternative with an assumed short-borrow charge. The operator translation and Yahoo data differ from WorldQuant BRAIN; details and limits appear in the generated report. Adjusted closes and Yahoo volume are cached together on new downloads.

For offline software checks, run `python3 -m pytest -q` and `python3 run_demo.py`. The demo uses **synthetic data**; its returns are never presented as observed performance.



## Resume description

- Built a Python walk-forward research engine comparing six constrained allocation methods across 12 stocks and a separate nine-sector-ETF universe, with next-session execution and self-financing trading costs.
- Evaluated covariance estimators using subsequent realized risk, and assessed performance through factor attribution, paired block bootstrap intervals, and a fixed six-case robustness grid.
- Implemented a distinct volume-conditioned reversal signal experiment, with cross-sectional rank IC, daily versus monthly turnover, and gross/net performance diagnostics.


