# Methodology

## 1. Returns and data

Adjusted-close percentage changes produce daily simple total-return approximations. Missing prices fail validation; they are not silently forward-filled. French daily factors are parsed from the provider's ZIP files and converted from percentages to decimals. RF is a realized daily cash return. Factors and prices must have complete aligned observations inside the common date range. Source hashes and the effective sample are recorded.

The classroom exercise uses weighted stock log returns. The backtest uses **simple returns**, because the simple return of held portfolio weights is exactly `w @ asset_returns`. Weighting log returns would not give exact portfolio wealth changes. The original homework and this backtest therefore use explicitly different conventions.

Adjusted prices and French factors can be revised retrospectively. Cached downloads preserve one reproducible data snapshot, not a guarantee of point-in-time data availability.

## 2. Timing and accounting

At a month-end close, use the preceding 504 daily returns, including that close, to estimate target weights. Execute at the next observed trading day's close. The old holdings first earn that day's return; the new target earns returns starting with the following interval. Initial capital earns the supplied RF before entry. This avoids using the signal-day close as both a newly observed signal and an assumed fill.

Weights drift daily with asset returns. The position cap applies at rebalances; passive drift may temporarily exceed it. Every strategy uses the same rebalance schedule, long-only constraint, and cap. Benchmark SPY is bought once at the initial entry date with the same per-dollar cost and then held.

Trades are self-financing. Let `u` be the risky weights after that day's return but before the trade, `w` the target weights, `k` the cost per dollar traded, and `q` the fraction of wealth left after costs. Solve:

`q + k * sum(abs(q*w - u)) = 1`.

Then net daily growth is `(1 + gross_return) * q`. Turnover is total dollars bought plus sold divided by pre-trade wealth. It is **not** the half-sum convention. Initial entry costs count; terminal liquidation is not assumed. Cash interest, adjusted-close dividends, and proportional costs are modeled; taxes, price impact, and exact close fills are not.

## 3. Construction rules

All optimization uses the same training window. Sample covariance uses pandas' sample estimate. Ledoit–Wolf covariance combines a sample estimate with a scaled-identity target to reduce estimation noise. The factor covariance model regresses each stock's excess returns on market, SMB, HML, and MOM with an intercept, then uses:

`Sigma = B @ factor_covariance @ B.T + diag(specific_variances)`.

Residual variances use regression degrees of freedom. Diagonal residual covariance is an explicit simplifying assumption, which can miss industry or correlated residual risk. This is a time-series factor model, not the fundamental cross-sectional BARRA estimation procedure.

Rules: equal weight; minimum variance with sample covariance; minimum variance with shrinkage; minimum variance with factor covariance; maximum estimated Sharpe with shrinkage. Maximum Sharpe uses historical mean excess returns and two deterministic optimizer starts; it is a numerical estimate, with no universal global-optimality claim when all expected excess returns are negative. Solver failures are raised, not replaced silently by equal weights.

The report's frontier is a final training-window snapshot computed under the same long-only cap using shrinkage covariance. It is an expected-return illustration and not an out-of-sample performance result.

## 4. Performance

- CAGR: compound net growth raised to `252 / number_of_days`, minus one.
- Arithmetic annual return: mean daily return times 252.
- Excess volatility: sample standard deviation of daily net return minus RF, times square root of 252.
- Sharpe: mean daily excess return divided by its standard deviation, times square root of 252.
- Sortino: annualized mean excess return divided by the annualized root mean square of negative excess returns, including zeros on other days; RF is the daily threshold.
- Drawdown: wealth divided by its running maximum, minus one. The running maximum includes initial capital. Maximum drawdown is reported as a negative number.
- Active return: mean portfolio-minus-benchmark daily return times 252.
- Tracking error: sample standard deviation of daily active returns times square root of 252.
- Information ratio: active return divided by tracking error; undefined for the benchmark against itself.
- Daily 95% expected shortfall: negative mean return among observations at or below the empirical 5% quantile; a daily loss measure, not annualized.
- Annual traded notional: total traded fractions times `252 / number_of_days`.

Conventional square-root annualization assumes sufficiently weak serial dependence. Autocorrelation is reported and discussed; it is not automatically removed from Sharpe. Subperiod drawdown restarts wealth at the beginning of that subperiod, so it is not the same as a full-sample drawdown cutout. Short stress-window annualized metrics are not long-run forecasts; total return and drawdown are the useful quantities there.

## 5. Attribution and uncertainty

Regress daily realized **net excess returns** on (a) market excess return and (b) market, SMB, HML, and MOM, including an intercept. Attribution uses contemporaneous realized factors only for explanatory regressions; those full-sample coefficients never feed portfolio decisions.

Report daily alpha, arithmetic annual alpha (`daily alpha * 252`), OLS and HAC alpha t-statistics, HAC 95% confidence intervals, adjusted R-squared, annual residual volatility, and appraisal ratio. HAC uses five daily lags by default. Intervals are model-conditional and unadjusted for multiple comparisons; positive alpha does not establish repeatable skill. A research extension can add block-bootstrap uncertainty and precommitted parameter comparisons.

At each decision date, record portfolio factor exposures and estimated common-factor and specific variances. Their sum equals total modeled portfolio variance. This is a risk decomposition, not an additive decomposition of compounded return.

## 6. Interpretation and limitations

The fixed universe is retrospectively selected and excludes delisted firms. The test evaluates allocation conditional on these selected survivors. Do not present it as an unbiased universe-selection strategy. A historical before/after-2021 split illustrates robustness, but it cannot become a genuine untouched holdout once inspected.

The report makes descriptive comparisons and does not assert alpha or an optimal future strategy. Study concentration, costs, factor exposure, changes across periods, and covariance estimation error together. Robustness extensions should be planned before examining their performance; record every tested variation.

## 7. Turnover-aware optimization

The sixth construction rule minimizes
`0.5 * gamma * H * w' Sigma_daily w + k * sum(abs(w - u))`,
where gamma defaults to 5, H is 21 days for monthly rebalancing and 63 for quarterly,
k is configured proportional cost, and u is this strategy's drifted risky holdings at
the decision close. Introduce epigraph variables to implement the absolute value as
linear inequalities. All original weight constraints remain in force.

The objective trades expected variance reduction against anticipated trading expense.
It does not include expected alpha. Holdings at the next day's execution price are unknown
at the decision; actual traded notional can therefore differ from the penalty's estimate.
At initial entry all risky pre-trade weights are zero, making the L1 term constant for
fully invested nonnegative weights. The actual engine charges costs exactly as before.
The existing 0/10/25-bp sensitivity reprices fixed weights; it does not refit the cost penalty.

## 8. Forecast evaluation

At every signal, each of the three covariance estimators predicts daily portfolio variance
for each target allocation. Compare it with the sample variance of realized gross returns
over the next complete holding interval: strictly after execution through the following
execution day, when the previous holdings still earn that day's return. Exclude the terminal
incomplete holding period and intervals with fewer than ten returns.

Score QLIKE as `realized / predicted - log(realized / predicted) - 1`, plus annualized
volatility MAE, volatility bias, and daily-variance MSE. Smaller QLIKE is better; it is
not a hypothesis-test statistic here. A realized variance from 20 trading days is a noisy
estimate of latent risk. Holdings drift during the interval; the fixed target-weight
forecast is therefore an approximation to realized portfolio risk.

The primary chart holds the portfolio fixed to equal weighting across estimators, avoiding
confounding estimator quality with differences in target weights. All other strategy
scores are also exported. No future observation enters the forecast or weights.

## 9. Uncertainty and robustness

The circular block bootstrap samples contiguous blocks of 21 daily observations by default,
wrapping at the end. Every strategy and RF uses the same resampled indices. With 2,000 draws,
report percentile 95% intervals for differences in Sharpe and CAGR versus equal weight.
Approximate two-sided p-values compare the centered bootstrap difference with the observed
absolute difference; Holm adjustment applies separately within each metric's strategy
comparisons. It does not correct all experiments across grids, universes, or researcher choices.
Marginal intervals are not simultaneous intervals.

This resamples realized strategy paths rather than refitting optimizers in bootstrap samples.
Inference is conditional on those paths, the universe, and a dependence/stationarity approximation.
It does not capture all model-selection uncertainty. Block length matters; investigating
different lengths is an additional robustness experiment to document explicitly.

The fixed grid is 252/504/756 days crossed with monthly/quarterly rebalancing. All cases
wait for a common first decision: the earliest quarter-end after the longest training window
is available. They enter on the same next-session close and pay initial costs on that date.
Report both the common full period and chronological pre/post-2021 periods. No winner is
automatically selected on validation performance. Historical validation has already been
viewed and is not an untouched test sample.

The separate sector experiment uses nine original sector ETFs, not a changing set of
historical constituents. Selection, fund construction, and data revision biases remain;
ETF results are not merged with stock returns. Compare conclusions across the two reports.

## 10. Price/volume reversal rank

The additional isolated experiment implements the user's supplied sequence:
`rank(ts_decay_linear(-ts_delta(close,2)*(volume/ts_mean(volume,100)),5))`.
The two-day **price difference** uses adjusted close in dollars, not percentage returns.
Relative volume divides today's volume by its trailing 100-session mean including today.
Apply linear weights 1, 2, 3, 4, 5 to five historical observations, oldest first,
divide by 15, and rank each date across the fixed universe in percent ranks.
The signal is undefined until all windows are complete. Missing volume fails validation.

The signal is observed at close t. Old positions earn t-to-t+1; the new weights execute at
close t+1, paying traded-dollar costs. Portfolio profits start with t+1-to-t+2. This
close-to-close convention avoids using a just-observed close for a fill at that same close.
It does not imply actual market-on-close or next-day-open execution quality.

Two separate translations make the rank tradable. Long-only uses fourth-power rank scores,
proportional normalization and capped redistribution into the original 20% target limit.
Dollar neutral subtracts the daily cross-sectional mean rank and scales absolute weights
to one, with 50% long and 50% short gross when ranks differ. Cash equals one less the sum
of risky weights; a zero-net risky book therefore earns RF on its unit cash balance, and
borrowing costs of 50 bps/year default on gross short exposure are subtracted daily.
Trades are self-financing under the existing cost equation. Borrow availability, margin,
interest on actual short proceeds, slippage, and liquidations are not modeled. The original
long-only project's rebalance frequency and no-short assumptions do not describe the neutral test.

Compare long-only ranks at daily and monthly frequency, equal weight at the same two
frequencies, neutral ranks daily, and SPY bought once. The evaluation starts on the same
first eligible execution date for all six paths. Monthly ranks only refresh on month-end,
which may miss the short-term reversal horizon. Report gross/net returns and annualized
total traded notional; high turnover can swamp gross alpha.

For signal quality, Spearman rank IC compares decision-time ranks at t with adjusted-price
returns from the t+1 close through t+1+h closes for h=1,2,5. This is aligned with
the assumed fill but conditional on the cross-sectional universe. A five-lag HAC t-stat
accounts partially for overlapping horizons; it does not correct universe selection or
searching many candidate formulas. Paired bootstrap intervals compare realized net paths
with the daily equal-weight path. They do not account for formula selection.

Yahoo adjusted close and Yahoo volume do not guarantee identical corporate-action
treatment to WorldQuant close and volume. Raw dollar differences introduce price-level
bias, especially across split histories. This is a transparent approximation of the
expression, not a reproduction or validation of a WorldQuant BRAIN alpha.
