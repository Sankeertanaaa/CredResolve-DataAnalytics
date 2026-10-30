# Executive Memo — Collections Performance

## Executive conclusion

The reported statement that “recovery has improved by 11% month-on-month” is **not supported as a sustained business trend**.

The supplied data covers January through 8 August 2026, not a full 12 months. August is partial, so the main trend uses January–July. Successful cash recovery is ₹126.8 Cr across those seven full months. January recovery was ₹18.72 Cr and July was ₹18.72 Cr, a change of only 0.01%.

March did show an 11.03% month-on-month increase, but April immediately fell 7.29%. The pattern alternates rather than showing a persistent 11% improvement.

## What happened

**Fact:** Recovery is volatile around ₹17–19 Cr per full month. The largest full-month increase is March (+11.03%), followed by a decline in April.

**Fact:** Recovery per recovered account increased only 1.7% from January to July.

**Strong evidence:** Outbound contact rate moved from 23.3% in January to 22.6% in July. This does not support a broad operational improvement in reach.

**Strong evidence:** First-target 14-day conversion increased from 3.72% to 4.26%, while first-target accounts fell from 5,732 to 1,643. The business appears to be targeting fewer accounts with slightly better observed conversion.

**Data limitation:** The supplied data has no client dimension and no language field, so those requested cuts cannot be reliably produced.

## Why it happened

The strongest observable differences are in **targeting mix**, risk segment, and channel.

For first-target accounts, the observed 14-day conversion is highest for SMS at 3.87% and FIELD at 3.83%, versus 3.50% for VOICE. High-risk accounts also have higher observed 14-day conversion than low-risk accounts: 3.90% versus 3.48%.

Priority variation is material: the best observed priority group has 4.63% conversion and ₹3,510 average 14-day recovery per targeted account, while the weakest has 3.12% conversion and ₹2,414 average recovery. This is **correlation, not proof of causal uplift**.

Telephony data also has quality problems: 60,028 cleaned call records have a timezone mismatch versus the vendor mapping. This makes hour-of-day analysis less reliable until timezone semantics are corrected.

## Is the 11% claim real?

**No, as a sustained month-on-month claim.**

A defensible independent recovery metric is successful payment cash collected divided by the fixed portfolio outstanding amount, supplemented by recovery per recovered account and operational funnel metrics.

The March +11.03% movement is real in the cleaned payment data, but it is an isolated monthly movement. It is not evidence that recovery is improving 11% every month.

## ₹10 Cr recommendation

### Recommend: Better borrower targeting

Jan–Jul recovery totals approximately ₹126.8 Cr across seven full months, implying an annualized recovery run-rate of approximately ₹217.5 Cr if the observed seven-month average continues.

For the investment case, I use a 5% sustained recovery uplift as a scenario assumption rather than an observed causal effect.

- Expected incremental recovery: approximately ₹10.9 Cr per year
- Investment: ₹10 Cr
- Base-case net benefit: approximately ₹0.9 Cr
- Base-case ROI: approximately 9%
- Break-even: approximately 11 months
- Downside at 2% uplift: approximately ₹4.4 Cr incremental recovery, resulting in negative ROI
- Upside at 8% uplift: approximately ₹17.4 Cr incremental recovery

Confidence is **low-to-medium**. The dataset provides strong descriptive evidence about targeting performance, but it does not establish that improved targeting itself causes a 5% recovery uplift.

I would therefore not commit the full ₹10 Cr immediately. I would release the investment through a controlled targeting experiment. The experiment should randomize comparable accounts where operationally feasible, hold agent and channel capacity constant where possible, and measure 14-day recovery, recovery per targeted account, cost per ₹ recovered, complaints, and PTP kept rate.

The decision to scale should be based on the incremental recovery observed in the experiment rather than the 5% scenario assumption.

## Data quality and trust

The analysis found duplicate payments, duplicate calls, borrower-ID inconsistencies between event tables and accounts, unstable employee codes, timezone mismatches, and late-arriving account status records.

The golden layer resolves these issues explicitly rather than silently overwriting them. The full data-quality report is included with the submission.

## Final decision

**Do not accept the 11% improvement claim as a business KPI.**

**Invest in better borrower targeting, but validate the expected uplift through a controlled experiment before deploying the full ₹10 Cr.**
