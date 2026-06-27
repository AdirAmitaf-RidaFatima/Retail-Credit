# Retail Credit Intelligence Workspace — Dashboard Story and Examiner Mapping

## What story the dashboard tells

The dashboard tells the story of how a bank converts retail lending data into credit decisions.

1. **Portfolio size and exposure** — how many borrower accounts exist and how much money is at risk.
2. **Borrower default risk** — the model-estimated probability that borrowers may fail to repay.
3. **Expected credit loss** — the estimated loss after default probability, exposure amount, and loss severity.
4. **Expected profit after credit loss** — whether the bank is still earning after funding cost, operating cost, and modelled credit loss.
5. **Facility and tenor performance** — which loan products and loan tenors are safer, riskier, profitable, or loss-making.
6. **Borrower decision support** — which borrower should be approved, approved with conditions, reviewed manually, or declined.
7. **Risk explanation** — why a borrower is considered risky or acceptable.
8. **Model assurance** — evidence that the model has been evaluated, calibrated, and made explainable.
9. **Exportable evidence** — portfolio summary, Excel evidence pack, and borrower credit memo for committee-style review.

## Why the redesign is stronger than the old multi-page app

The previous app had the right information but divided it across many pages. The new design keeps the information while converting it into one analyst workspace. This makes the result look more like an internal banking analytics product and less like a classroom Streamlit demo.

## Examiner requirement mapping

| Examiner expectation | Where it appears in the dashboard |
|---|---|
| Understand retail credit as a business | Story strip, portfolio cards, facility and tenor analysis, borrower decision desk |
| Understand how banks evaluate borrowers | Borrower profile, debt burden, income, utilization, delinquencies, inquiries, recommendation logic |
| Understand facilities | Facility slicer, facility expected loss chart, facility risk-return analysis |
| Understand tenor decisions | Tenor slicer, tenor profitability chart, simulator tenor sensitivity |
| Understand pricing and return | Portfolio yield, expected profit after credit loss, risk-adjusted return, simulator portfolio yield |
| Predict default and non-default | Predicted default probability and risk categories |
| Show probability of default | Full label: Predicted Default Probability |
| Analyze expected loss | Expected Credit Loss cards and segment charts |
| Analyze potential return | Expected Profit After Credit Loss cards and charts |
| Show portfolio analytics | Segment selector, risk-return map, management alerts, borrower queue |
| Show borrower-level intelligence | Borrower decision desk and credit memo export |
| Explain model reasoning | Main risk drivers, mitigants, model assurance, feature importance and SHAP plot |
| Demonstrate technical soundness | Model comparison, calibration, reports, data pipeline outputs |
| Demonstrate product thinking | One-dashboard workflow, slicers, exports, decision-focused layout |
| Avoid clutter | Long paragraphs removed; filters and expanders used instead |
| Make it beginner-friendly | Abbreviations replaced with full wording and plain-language labels |

## What makes the weeks of effort visible

The top evidence trail shows the full project journey: business research, dataset audit, leakage control, portfolio analysis, model validation, explainability, and dashboard delivery. The dashboard therefore makes it clear that this is not just a model output. It is an end-to-end retail credit risk system.

## Presentation script

"This dashboard is designed as a Retail Credit Intelligence Workspace. It starts from the exact business question a bank asks: who should we lend to, under what facility and tenor, what is the probability of non-repayment, how much could we lose, and whether the return is enough for the risk. The top cards answer portfolio health in 30 seconds. The middle explains risk and profit by facility, tenor, grade, geography, and borrower segment. The borrower desk converts model outputs into credit-officer decisions. The model assurance section shows that the model was not treated like a black box: it has comparison metrics, calibration evidence, feature importance, and explainability."
