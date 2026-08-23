# Job Scraping Pipeline

Python pipeline for collecting, normalizing, testing, and exporting job listings from multiple public job-board sources for downstream TalentBliss ingestion.

## Overview

The repository contains source-specific scrapers plus normalization and combining utilities. The current workflow supports JOIN-based job discovery and Greenhouse's public Job Board API, producing a common job-feed shape for downstream validation and import.

## Data flow

```text
JOIN / Greenhouse
      ↓
source-specific discovery
      ↓
job detail extraction
      ↓
normalization + filtering
      ↓
combined job feed
      ↓
Google Drive / downstream ingestion
```

## Key features

- JOIN company/job discovery workflow
- Greenhouse Job Board API integration
- Config-driven Greenhouse employer list
- Common TalentBliss-compatible output fields
- Deterministic student-role tagging
- Job-summary splitting and combining utilities
- Shell helpers for batch processing
- Google Drive upload support
- Unit tests for Greenhouse parsing/classification behavior

## Tech stack

- Python
- Requests / HTTP job-board APIs
- HTML parsing/scraping utilities
- Shell scripting
- Google Drive integration
- GitHub Actions

## Repository structure

```text
.
├── greenhouse-scraper.py        # Greenhouse API scraper
├── greenhouse_boards.json       # Configured Greenhouse boards
├── job-details-scraper.py       # Job-detail extraction
├── job-summary-splitter.py      # Feed partitioning helper
├── combine-job-summaries.py     # Feed merge helper
├── script.py                    # JOIN workflow logic
├── upload-to-gdrive.py          # Feed publishing helper
├── *.sh                         # Batch/update shell helpers
├── tests/                       # Unit tests
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the Greenhouse scraper with:

```bash
python greenhouse-scraper.py
```

Configured employers are stored in `greenhouse_boards.json`:

```json
{
  "board_token": "company-token",
  "company_name": "Company Name"
}
```

The board token is the final segment of a Greenhouse board URL such as `https://job-boards.greenhouse.io/company-token`.

## Student-role classification

Listings can be tagged deterministically using German and English title/description rules for categories including:

- internship
- working student
- graduate
- thesis
- apprenticeship

## Tests

```bash
python -m unittest discover -s tests -v
```

## Operational notes

Scraping logic depends on third-party page/API behavior and may need maintenance when providers change their markup, endpoints, or access rules. Respect the terms, rate limits, and robots policies of each source.

Do not commit API keys, Drive credentials, cookies, or other secrets.
