# Changes

## 0.4.0

- Reorganized the GitHub README around the observed-data research question and reproducible run.
- Added `publish_results.py` to turn verified historical runs into a small GitHub results page and figures; demo data are explicitly refused.
- Cached Yahoo volume during the primary price download for use by the separate signal study.
- Added publisher acceptance/rejection checks and a results-page placeholder.

## 0.3.0

- Added a separate price/volume rank experiment using the supplied WorldQuant-style formula.
- Added volume downloads, daily and monthly long-only portfolios, dollar-neutral daily
  portfolio with an assumed short borrow charge, aligned equal-weight references,
  delayed execution, rank IC, factor attribution, cost/turnover reporting, and a report.
- Existing portfolio and ETF backtests remain unchanged.
- Expanded numerical tests to 25 and executed the full synthetic signal report.

## 0.2.0

- Added turnover-aware minimum variance using decision-time drifted holdings.
- Added complete-period risk forecast scoring on common allocations.
- Added paired block-bootstrap inference and explicitly scoped Holm adjustment.
- Added a fixed common-entry robustness grid and separate sector-ETF study.
- Added frozen research plans and subsequent paper evaluation.
- Added research evidence charts and explicit experiment/interpretation rules.
- Outputs now go to `research_v2` / `etf_research_v2`, preserving earlier reports.
- Expanded numerical tests from 12 to 20.

## 0.1.1

- Explicit certifi trust roots for factor downloads on macOS, retaining certificate validation.

## 0.1.0

- Initial five-rule rolling backtest with costs, attribution, and report generation.
