# Capstone

Capstone is a University of Michigan MADS (Spring/Summer 2026) project that studies how voter outreach and state voter ID laws relate to validated 2024 turnout in the Cooperative Election Study (CES).

---

## Data Story

> **Coming soon.** This section will hold the project's data story — the narrative walkthrough of the research question, findings, and figures.

Until then, exploratory figures from the analysis pipeline are below.

![Turnout by voter ID strictness](assets/report_fig1_turnout_by_strictness.png)

![Turnout by contact status](assets/report_fig2_turnout_by_contacted.png)

![Turnout by contact channel](assets/report_fig3_turnout_by_contacted.png)

![Logistic marginal effects](assets/report_fig4_logistic_marginal_effects.png)

---

## Install and run

Requires **Python 3.13+**.

```bash
pip install git+https://github.com/atunison3/capstone.git
capstone
```

What `capstone` does:

1. Guides you through obtaining CES data (manual download from Harvard Dataverse).
2. Downloads Census FIPS state codes and NCSL voter ID classifications into `.data/`.
3. Cleans and merges the datasets using settings from `capstone/config.py`.
4. Fits a logistic regression of validated turnout and prints the model summary.

Configuration ships inside the package (`capstone.config`). Override paths or column maps by editing that module (use an editable install while developing).

CES data cannot be fully automated (Harvard Dataverse WAF). When prompted, download the CES CSV into your user `Downloads` folder; the tool moves it into `.data/ces_data.csv`.

---

## What this project does

| Area | Role |
| --- | --- |
| Data setup | Obtain CES, FIPS, and NCSL inputs |
| Cleaning | Rename, map, and merge survey + state policy data |
| Modeling | Logistic regression of validated turnout |
| Visualization | Report figures for outreach and voter ID effects |

## Next steps

- [Installation](getting-started/installation.md) — prerequisites and install options
- [Usage](getting-started/usage.md) — CLI and Python API examples
- [Full documentation](documentation/README.md) — package and module reference
- [Contributing](contributing/README.md) — developer setup
