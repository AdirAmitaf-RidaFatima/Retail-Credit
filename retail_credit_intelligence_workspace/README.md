# Retail Credit Intelligence Workspace

A light-theme, single-dashboard Streamlit application that converts retail credit risk modelling outputs into a premium analyst workspace for borrower decisions, facility strategy, expected credit loss, expected profit after credit loss, model assurance, and exportable credit evidence.

## Why this version exists

The original application contained all required analytics but was split into several pages. This version consolidates the same intelligence into one unified dashboard so an examiner or supervisor can immediately see the full story without clicking through many pages.

## What the dashboard answers

- Is the selected retail credit portfolio healthy?
- How much exposure is at risk?
- What is the average predicted default probability?
- What is the expected credit loss?
- Is the portfolio profitable after credit losses?
- Which facilities create the largest loss or strongest return?
- Which loan tenors are riskier?
- Which borrowers require approval, conditions, manual review, or decline?
- Why did the system make a recommendation?
- Is the model explainable and validated enough for an educational prototype?

## Main workflow

`Borrower and facility data → Predicted default probability → Risk category → Expected credit loss → Expected profit after credit loss → Lending recommendation → Portfolio action`

## Folder structure

```text
retail_credit_intelligence_workspace/
├── app.py
├── components/
├── services/
├── data/
├── reports/
├── plots/
├── models/
├── assets/
├── docs/
├── legacy_pages_archive/
├── .streamlit/
└── requirements.txt
```

## Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Required file

```text
data/scored_portfolio.csv
```

This package already includes a dashboard-ready scored portfolio sample.

## Design changes from previous version

- Replaced dark theme with light enterprise theme for better readability.
- Consolidated multiple dashboard pages into one workspace.
- Replaced abbreviations with full banking wording.
- Moved long explanations into documentation and expandable evidence panels.
- Added slicers so one dashboard can analyze facility, tenor, grade, geography, risk category, and lending recommendation.
- Added borrower decision desk, scenario simulator, model assurance panel, and report exports in the same flow.

## Governance note

This is a production-style educational prototype. A real bank would require live bureau data, rejected application data, KYC/AML controls, override logging, access controls, audit trails, and formal model validation approval before production use.
