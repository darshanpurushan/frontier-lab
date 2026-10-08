# Experiment plan and interpretation rules

## Research question

Do improved covariance estimates and explicit trading penalties improve realized portfolio
risk and net performance relative to simple equal weighting?

The original historical stock result has already been inspected. This document specifies
the next comparisons but does not retroactively preregister the original sample.

## Fixed comparisons

1. Compare sample, Ledoit–Wolf, and four-factor risk forecasts on the same equal-weight
   allocation using mean QLIKE and annualized volatility MAE. Keep other portfolio forecasts
   as secondary diagnostics.
2. Compare turnover-aware minimum variance with shrinkage minimum variance: turnover,
   net return, Sharpe, realized volatility, and drawdown. Report the trade-off even if
   turnover falls but risk rises.
3. Compare every construction rule with equal weight using paired block-bootstrap intervals
   for Sharpe and CAGR differences. Report negative as well as positive results.
4. Repeat the specified six estimation/rebalance cases from a common entry date; do not
   select the final configuration using the best historical validation Sharpe.
5. Repeat the whole experiment on the separately specified nine-sector-ETF basket. Do not
   splice its history with stock results or call it a survivorship-bias-free universe.

## Fixed settings for this version

- Estimation windows: 252, 504, 756 trading observations.
- Rebalancing: monthly and quarterly.
- Target weight cap: 20%; fully invested; no short selling.
- Cost in construction and baseline accounting: 10 bps per dollar traded.
- Risk-aversion coefficient: 5; variance horizon: 21 or 63 sessions.
- Cost repricing: 0, 10, and 25 bps with fixed target paths.
- Bootstrap: 2,000 circular-block replicates, 21-observation blocks, seed 42.
- Chronological comparison split: January 1, 2021.
- Factor attribution: market, SMB, HML, MOM; five-lag HAC errors.

These settings are research choices, not estimated optimal values. Any added variant belongs
in a new version of this plan and should be disclosed in the results memo. Bootstrap p-values
are approximate and do not correct for the complete research search process.

## What counts as a useful finding

Better forecast scores without higher Sharpe suggest risk estimation and return prediction
are different problems. Lower turnover with comparable risk supports an implementation benefit.
Results that reverse across universes or windows indicate fragility. No improvement over
equal weighting is a valid conclusion; it must not be hidden by reporting only the best run.

## Before presenting numerical findings

Review the actual historical reports, missing-data checks, date ranges, and configuration.
Retain the manifests. Quote the relevant metric and period, include a benchmark, and explain
uncertainty and the retrospective universe. Never use synthetic numbers on a resume.

## Prospective phase

Choose one rule, freeze its configuration and code hash, and commit it before the next eligible
rebalance. Later evaluate only that frozen choice against the stated references. Data revisions
and simulated fills still limit this paper track record; no real orders are executed.
