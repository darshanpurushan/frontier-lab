# Frontier Lab

**Walk-forward portfolio construction, risk forecasting, and factor attribution in Python.**

Can portfolio optimization beat a simple equal-weight portfolio after estimation error and trading costs? This project tests that question on observed Yahoo Finance prices and Kenneth French factors. It compares six allocation rules, evaluates risk forecasts against later returns, and reports uncertainty in performance differences. A separate price/volume reversal experiment tests a supplied rank signal.

## Run the historical study

From the project folder on a Mac with Python 3.11 or newer:

```bash
python3 -m pip install -e '.[dev]'
python3 run_research.py
python3 publish_results.py
```

Open `outputs/research_v2/report.html` and `outputs/etf_research_v2/report.html` for the full HTML reports. `publish_results.py` creates [`docs/HISTORICAL_RESULTS.md`](docs/HISTORICAL_RESULTS.md) and two GitHub-friendly figures from **observed** results only. Review them, then commit. It refuses synthetic runs and checks that published CAGR matches the daily net returns. If Yahoo rate limits you, rerun later; cached downloads are reused. `python3 run_project.py` runs just the main stock study and is suitable for Spyder (F5).

The repository ships with source code and tests. Historical performance is not hard-coded: the local historical results page is created only after a real-data run. [Research evidence and status](VALIDATION.md) explains what has been executed. No Sharpe target is imposed.

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

## Put it on GitHub

After running the historical study and checking the generated research page, create an empty `frontier-lab` repository on your GitHub account and run:

```bash
git init
git add .
git commit -m "Publish portfolio research framework and verified results"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/frontier-lab.git
git push -u origin main
```

The [GitHub Actions workflow](.github/workflows/tests.yml) runs numerical tests without downloading market data. The checked-in `docs/HISTORICAL_RESULTS.md` starter page contains no synthetic performance; regenerate it locally after historical runs. Publish only market-data summaries you are allowed to redistribute.

## Resume description

- Built a Python walk-forward research engine comparing six constrained allocation methods across 12 stocks and a separate nine-sector-ETF universe, with next-session execution and self-financing trading costs.
- Evaluated covariance estimators using subsequent realized risk, and assessed performance through factor attribution, paired block bootstrap intervals, and a fixed six-case robustness grid.
- Implemented a distinct volume-conditioned reversal signal experiment, with cross-sectional rank IC, daily versus monthly turnover, and gross/net performance diagnostics.

Add numerical findings only after reviewing the generated [historical results](docs/HISTORICAL_RESULTS.md). See [validation](VALIDATION.md) for execution status and [changes](CHANGELOG.md) for version history.
