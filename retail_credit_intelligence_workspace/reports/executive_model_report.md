# Executive Model Development Report

## Project Context
This phase develops a leakage-controlled Probability of Default model for a retail credit intelligence prototype. The modelling strategy follows the approved Phase 1 methodology: scorecard-first design, machine-learning challenger second, and no use of repayment, recovery, hardship, settlement, or final-status fields as origination model inputs.

## Modelling Universe
- Rows loaded for this run: 2,260,668
- Split strategy: time-aware split using issue_d
- Primary target: binary default flag from finalized Lending Club outcomes.
- Unresolved loans are excluded from model training and validation.

## Models Developed
- Policy-rule baseline: transparent underwriting benchmark.
- Logistic Regression: interpretable champion candidate.
- WOE + Logistic Regression: scorecard-style candidate.
- Decision Tree and Random Forest: explainable/nonlinear benchmarks.
- XGBoost/LightGBM/CatBoost: optional advanced challengers depending on runtime availability.

## Best Statistical Performer
- Model: logistic_regression
- ROC-AUC: 0.6824
- PR-AUC: 0.4092
- KS: 0.2642
- Brier Score: 0.2183

## Recommended Production-Style Model
- Selected model: scorecard_woe_logistic
- ROC-AUC: 0.6737
- PR-AUC: 0.4109
- KS: 0.2493
- Average PD: 0.4443
- Expected loss rate: 0.3105
- Expected return: -0.0538

## Calibration Result
Calibration is required because a bank uses PD for expected loss, IFRS 9, pricing, portfolio monitoring, and risk bands. A model can rank borrowers well but still produce poorly calibrated PD values. The calibration comparison is saved in `calibration_comparison.csv`.

## Model Risk Management View
The model is appropriate as a production-style educational prototype if used with the documented limitations. It would not yet pass a full bank production validation because the source data lacks rejected applications, internal bank cash-flow, Pakistan eCIB data, KYC/fraud controls, collateral information, approved policy overrides, and a formally defined observation/performance window.

## Dashboard Outputs Produced
- Probability of Default
- Risk Band
- Recommended Decision
- Expected Loss
- Expected Profit
- Expected Return
- Feature Importance
- SHAP plot for selected challenger where available

## Recommended Next Steps
1. Freeze final feature list and treatment rules.
2. Convert scorecard model into points/risk bands.
3. Define approval thresholds by risk appetite.
4. Build model monitoring dashboard with AUC, KS, PSI, calibration, approval rate, and bad rate by decile.
5. Prepare model card, validation pack, and challenger-model governance documentation.
