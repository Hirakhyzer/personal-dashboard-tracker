from datetime import date

from dashboard_tracker import Record, build_report, category_breakdown, monthly_breakdown, records_to_csv


def sample_records():
    return [
        Record(date(2026, 6, 1), "Incoming", "Salary", "Monthly payment", 2000.0),
        Record(date(2026, 6, 2), "Outgoing", "Food", "Groceries", 120.0),
        Record(date(2026, 6, 3), "Outgoing", "Transport", "Metro", 40.0),
        Record(date(2026, 6, 4), "Outgoing", "Food", "Cafe", 30.0),
    ]


def test_build_report_totals():
    report = build_report(sample_records(), category_limit=500.0)
    assert report.incoming_total == 2000.0
    assert report.outgoing_total == 190.0
    assert report.balance == 1810.0
    assert report.balance_rate == 90.5


def test_category_breakdown_groups_outgoing_records():
    summary = category_breakdown(sample_records())
    assert summary[0].category == "Food"
    assert summary[0].total == 150.0
    assert summary[0].count == 2


def test_monthly_breakdown_calculates_balance():
    monthly = monthly_breakdown(sample_records())
    assert monthly[0].month == "2026-06"
    assert monthly[0].incoming == 2000.0
    assert monthly[0].outgoing == 190.0
    assert monthly[0].balance == 1810.0


def test_records_to_csv_contains_header():
    csv_text = records_to_csv(sample_records())
    assert "date,type,category,description,amount" in csv_text
    assert "Food" in csv_text
