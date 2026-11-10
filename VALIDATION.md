# Validation record

## Current checkout limitation — November 9, 2026

The tracked tree does not contain the `frontier_lab/` package imported by the research launchers and `tests/test_research.py`. Full pytest collection fails with `ModuleNotFoundError`. This is a missing-source problem, not evidence that the historical tests below passed in the current checkout. Restore the original research package from a complete revision before claiming reproducibility or rerunning a study.

The standalone publisher's fixture tests run independently with `python3 -m pytest -q tests/test_publication.py`. Their success establishes publication-path behavior only. No historical market-data backtest has been regenerated as part of this correction; the earlier validation entries are retained as historical records.

## Version 0.4 publication work — October 7, 2026

- Added a historical-results publisher that rejects synthetic runs and verifies exported CAGR against daily net return CSVs before writing a GitHub summary and charts.
- Verified its output on a small constructed fixture and confirmed that it rejects the bundled synthetic report. Python compilation passed for all modules and tests.
- Historical Yahoo performance has not been rerun in this workspace. The current environment lacks the full project dependencies and network access for installation; the 25-test suite from version 0.3 was not rerun here. Run `python3 -m pip install -e '.[dev]'`, `python3 -m pytest -q`, `python3 run_research.py`, and `python3 publish_results.py` on the Mac before posting a results page.
- The main Yahoo download now stores vendor volume with adjusted closes for the separate signal study, avoiding a second download for a fresh cached snapshot.

Version 0.3 validated on September 28, 2026 UTC (September 27 in New York), in a Linux Python 3.12 environment.

## Completed

- Installed the package and its declared dependencies.
- Ran `python -m pytest -q`: **25 tests passed**.
- Ran `python -m frontier_lab.cli --demo --study --etf-study`: completed both universes,
  all six robustness cases per universe, paired bootstrap inference, prospective risk scores,
  rolling optimization, execution accounting, factor regressions, cost sensitivity,
  CSV export, and HTML/PNG report generation.
- Downloaded and parsed the actual Kenneth French daily three-factor and momentum ZIP files;
  both included observations through August 31, 2026. Verified date parsing and percent-to-decimal conversion.
- Inspected the generated wealth/drawdown and target-weight charts.

The tests cover self-financing costs, initial entry, execution delay, drifting holdings,
initial-capital drawdowns, covariance decomposition, allocation constraints, future-data
independence, missing-data rejection, factor-unit parsing, regression coefficient recovery,
benchmark-relative metrics, the efficient branch of the constrained frontier,
turnover-penalty behavior, forecast/realization alignment, paired contiguous resampling,
Holm adjustment, frozen-plan integrity, and quarterly timing.

## Not completed here

Yahoo Finance returned HTTP 429 rate-limit errors for AAPL and SPY. A complete market-data
backtest was therefore **not executed in this environment**. The user subsequently reported a
successful version-0.1 historical run on their Mac; its raw outputs have not been supplied here.
There are no claimed real-market
performance results in the bundled example. Run `python3 run_project.py` locally to download
prices and generate the historical analysis, or use `run_research.py` for the full upgraded study.
Adjusted-price and factor CSV files are also supported for a single-universe run.

The synthetic demo checks software functionality; it does not validate the economic model,
predict future returns, establish alpha, or resolve bias in the stock universe.

## Reproduction

The generated `manifest.json` records installed package versions, configuration, and hashes
of the data used. `requirements-tested.txt` records versions of the direct dependencies in
the successful validation environment. Full cross-platform bit-for-bit identity is not
guaranteed because optimizer and floating-point implementations can differ.

The prospective paper-evaluation path was tested with synthetic inputs to confirm that pre-freeze decisions are excluded. No real prospective performance is claimed.

Version 0.3 also ran `python -m frontier_lab.signal_cli --demo` end to end: signal ranks,
long-only and dollar-neutral trading paths, explicit borrowing assumptions, cost accounting,
forward rank IC, factor regressions, bootstrap intervals, CSVs, PNG, and HTML report.
The synthetic long-only daily signal underperformed its equal-weight reference after
costs and its daily trading exceeded 100 times capital annualized in that example.
These are synthetic diagnostic figures, not findings about historical market performance.
The Yahoo volume download and real-market signal results remain unverified here because
Yahoo rate-limited this workspace; run `run_signal.py` locally to obtain them.
