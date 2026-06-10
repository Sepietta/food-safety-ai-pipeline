# Food Safety AI Pipeline

> Automated microbiological report generation for food safety labs: Claude AI interpretation, FDA/FSMA validation, live recall intelligence, audit-ready PDF output.

---

## What it does

Food safety labs generate dozens of microbiological reports per week. Each one requires a trained microbiologist to manually interpret raw counts, cross-reference regulatory limits, write corrective actions, and format a compliance document. That process takes 45 to 60 minutes per report.

This pipeline does it in 30 seconds.

A lab submits a CSV of raw results. The pipeline validates each result against FSMA and FDA limits, calls the Claude API to generate a plain-language interpretation, pulls live recall data from the FDA Recall Enterprise System, and outputs a professional audit-ready PDF with risk classification, corrective actions, CCP recommendations, and official FDA recall citations.

---

## Sample output

**[Download sample report](demo_results_Demo_Foods_Inc._20260609_192537_report.pdf)**

Generated from anonymous demo data. Includes:
- Overall risk classification (LOW / MODERATE / HIGH / CRITICAL)
- Per-sample compliance status against FSMA limits
- AI-generated interpretation and root cause hypothesis
- Required corrective actions per non-conformance
- Critical Control Point (CCP) recommendations
- FDA Recall Intelligence: live recall counts, most recent recall, official FDA recall number, and average recall cost by pathogen

---

## Pipeline architecture
Raw lab CSV -> Parser + FSMA validator -> Claude API interpreter -> FDA Recall API -> PDF report

**Input:** CSV with columns `sample_id`, `pathogen`, `count`, `unit`

**Output:** Audit-ready PDF report

---

## Tech stack

| Component | Technology |
|---|---|
| Language | Python 3.13 |
| AI interpretation | Anthropic Claude API (claude-sonnet-4-6) |
| FDA recall data | openFDA Food Enforcement API |
| PDF generation | ReportLab |
| Data processing | pandas |
| Pathogen validation | Custom FSMA/FDA limit engine |

---

## Key features

**FSMA compliance engine** validates results against FDA Food Safety Modernization Act limits for E. coli O157:H7, Salmonella, Listeria monocytogenes, coliforms, aerobic mesophiles, molds and yeasts. Zero-tolerance pathogens trigger immediate rejection flags.

**AI-powered interpretation:** Claude API generates plain-language executive summaries, root cause hypotheses, and prioritized corrective actions. Output is structured JSON parsed into the report automatically.

**Live FDA recall intelligence:** for each pathogen detected, the report shows total recalls on record, recalls in the last 24 months, most recent recall with product description and date, recall classification, average recall cost, and official FDA recall number for verification.

**Audit-ready PDF:** formatted for direct submission to SQF, FSSC 22000, and FDA inspection reviewers. Includes analyst signature, generation timestamp, and data privacy statement.

---

## Files in this repo
food-safety-ai-pipeline/
├── parser.py              # FSMA validation engine + CSV ingestion
├── fda_recalls.py         # openFDA API client + recall intelligence
├── demo_results.csv       # Anonymous demo input
├── demo_results_report.pdf
└── requirements.txt

> `interpreter.py`, `report_generator.py`, and `main.py` are kept private as they contain proprietary prompt engineering and report formatting logic.

---

## Background

Built as a side project during my PhD in Microbiology at UC Merced (expected graduation 2026). The Central Valley produces roughly 25% of US food supply. FSMA compliance and microbiological testing are daily realities for hundreds of facilities within 60 miles of campus.

Three constraints shaped the design: no certification required to use it, no client data stored or retained, and output that a non-technical manager can understand in 30 seconds.

---

## Dependencies
anthropic>=0.40.0
pandas>=2.0.0
reportlab>=4.0.0
python-dotenv>=1.0.0
openpyxl>=3.1.0
requests>=2.31.0

---

## Contact

**Pedro Antonio Pérez Ferrer**
PhD Candidate, Microbiology, UC Merced
pperez40@ucmerced.edu
[LinkedIn](https://linkedin.com/in/pedroantonioperezferrer/)

---

*This tool is a decision-support aid. All reports should be reviewed by a qualified microbiologist before regulatory action. Input data is processed locally and not stored or retained.*
