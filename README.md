# Personal Dashboard Tracker

A polished Streamlit dashboard for organizing sample personal records, viewing category summaries, checking monthly totals, and exporting simple reports.

This is a portfolio project focused on dashboard UI, data handling, Python calculations, and clean GitHub structure.

## Features

- Beautiful Streamlit dashboard UI
- Summary cards for totals and balance
- Editable records table
- Category breakdown
- Monthly trend view
- Simple limit alerts
- Recent records section
- Downloadable CSV, JSON, and TXT reports
- Built-in sample records
- Core calculation logic separated from UI
- Unit tests and GitHub Actions workflow

## Tech Stack

- Python
- Streamlit
- Standard-library calculations
- Pytest

## Project Structure

```text
personal-dashboard-tracker/
├── app.py
├── dashboard_tracker.py
├── README.md
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── sample_data/
│   └── sample_records.csv
├── tests/
│   └── test_dashboard_tracker.py
└── .github/
    └── workflows/
        └── python-tests.yml
```

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Run Tests

```bash
pytest
```

## How It Works

Each record has a date, type, category, description, and amount. The app calculates totals, monthly summaries, category breakdowns, limit usage, and exportable reports.

## Portfolio Notes

This project demonstrates UI design, dashboard development, CSV handling, data summaries, report exports, testing, and clean documentation.
