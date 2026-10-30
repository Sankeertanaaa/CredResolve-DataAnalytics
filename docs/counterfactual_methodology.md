# Counterfactual Methodology

The targeting strategy should be evaluated as a causal intervention rather than by comparing raw recovery across strategy labels.

Treatment is an account first exposed to the new targeting strategy after the change date. Control is an otherwise comparable account exposed to the legacy strategy in the same calendar period.

The preferred identification strategy is a matched difference-in-differences design. Match or weight accounts on pre-treatment DPD, risk segment, outstanding balance, loan type, geography, prior contact rate, prior recovery, and prior attempt frequency. Use calendar-period fixed effects and account-level pre-period outcomes.

The outcome is 14-day successful payment amount and conversion to any successful payment.

The key assumptions are parallel pre-treatment trends, no major unmeasured targeting change that is correlated with treatment, stable outcome measurement, and no interference between treatment and control accounts.

Confounders include campaign capacity, agent allocation, channel availability, vendor health, seasonality, and portfolio mix.

The supplied data is suitable for designing this analysis but not for claiming a causal uplift without a clearly observed treatment start and a clean control group.
