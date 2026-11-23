# Northwind-Autonomous-CFO — AI-Assisted Quarterly Close & FP&A Reporting

> **Status:** work in progress. Personal project built for an *AI in Finance* challenge, using a fictional company (Northwind Financial Co.) and a sample dataset.

A Python workflow that automates the analyst-judgment part of a quarterly close: it validates the numbers, flags anomalies, matches the controller's explanations to them, and only then drafts executive commentary. A human approval step sits in the middle, so nothing reaches an executive audience without sign-off.

## What it does

- **Close validation:** compares the current close with the last approved one, detects changes to closed periods, and flags implausible quarter-on-quarter movements (`close_validation.py`).
- **Close history:** stores every approved close version, and supports reopening and correcting a period (`close_history.py`, `period_lifecycle.py`).
- **FP&A rollups:** revenue by region and product line, expenses by department and cost type, headcount, budget vs. actual, a salaries volume/rate bridge, and 16 automated tie-out checks (`rollups.py`).
- **Commentary workflow:** matches the controller's free-text explanations to the flagged items and checks whether each one is supported by the data (`commentary_workflow.py`).
- **AI-drafted narrative:** Claude turns the approved figures and explanations into executive commentary. Every number in that text is then checked against the source data.
- **Dashboard:** a Streamlit app with revenue, expenses, headcount, budget vs. actual, close status and narrative views (`Northwind_Financial_Dashboard.py`).

## Design principles

- **Calculations stay deterministic.** Every figure comes from code, never from the AI.
- **The AI explains, it doesn't decide.** It may match commentary and write the narrative, but it can't invent figures or causes, and it never approves a close.
- **Nothing publishes without a human.** A human approval gate sits between validation and executive output.
- **Assumptions are written down.** Limitations are documented in `assumptions_and_limitations.md`.

## Run it

```bash
pip install -r requirements.txt anthropic
streamlit run Northwind_Financial_Dashboard.py
```

AI narrative generation needs an `ANTHROPIC_API_KEY`. Without one, the app offers the prompt as a download, so you can paste it into Claude yourself.

## Built with

Python, pandas, Streamlit, Excel (sample dataset), and Claude (Anthropic API and Claude Code).
