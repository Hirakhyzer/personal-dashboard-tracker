"""Core calculation logic for the Personal Dashboard Tracker app."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path


@dataclass
class Record:
    record_date: date
    record_type: str
    category: str
    description: str
    amount: float

    @property
    def month_key(self) -> str:
        return self.record_date.strftime("%Y-%m")


@dataclass
class CategorySummary:
    category: str
    total: float
    count: int
    share_percent: float


@dataclass
class MonthlySummary:
    month: str
    incoming: float
    outgoing: float
    balance: float


@dataclass
class DashboardReport:
    incoming_total: float
    outgoing_total: float
    balance: float
    balance_rate: float
    category_summaries: list[CategorySummary]
    monthly_summaries: list[MonthlySummary]
    alerts: list[str]
    recent_records: list[Record]

    def to_dict(self) -> dict:
        return {
            "incoming_total": self.incoming_total,
            "outgoing_total": self.outgoing_total,
            "balance": self.balance,
            "balance_rate": self.balance_rate,
            "category_summaries": [asdict(item) for item in self.category_summaries],
            "monthly_summaries": [asdict(item) for item in self.monthly_summaries],
            "alerts": self.alerts,
            "recent_records": [
                {**asdict(item), "record_date": item.record_date.isoformat()}
                for item in self.recent_records
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_text(self) -> str:
        lines = [
            "Personal Dashboard Report",
            "=========================",
            f"Incoming total: {self.incoming_total:.2f}",
            f"Outgoing total: {self.outgoing_total:.2f}",
            f"Balance: {self.balance:.2f}",
            f"Balance rate: {self.balance_rate:.1f}%",
            "",
            "Category summaries:",
        ]
        for item in self.category_summaries:
            lines.append(f"- {item.category}: {item.total:.2f} across {item.count} records ({item.share_percent:.1f}%)")
        lines.append("")
        lines.append("Monthly summaries:")
        for item in self.monthly_summaries:
            lines.append(f"- {item.month}: incoming {item.incoming:.2f}, outgoing {item.outgoing:.2f}, balance {item.balance:.2f}")
        if self.alerts:
            lines.append("")
            lines.append("Alerts:")
            lines.extend(f"- {alert}" for alert in self.alerts)
        return "\n".join(lines) + "\n"


def parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def normalize_type(value: str) -> str:
    cleaned = str(value).strip().lower()
    if cleaned in {"incoming", "income", "in"}:
        return "Incoming"
    if cleaned in {"outgoing", "expense", "spending", "out"}:
        return "Outgoing"
    return "Outgoing"


def load_records_from_csv(path: str | Path) -> list[Record]:
    with Path(path).open(newline="", encoding="utf-8") as file:
        rows = csv.DictReader(file)
        return [
            Record(
                record_date=parse_date(row["date"]),
                record_type=normalize_type(row["type"]),
                category=row["category"].strip(),
                description=row["description"].strip(),
                amount=float(row["amount"]),
            )
            for row in rows
        ]


def category_breakdown(records: list[Record]) -> list[CategorySummary]:
    outgoing_records = [item for item in records if item.record_type == "Outgoing"]
    outgoing_total = sum(item.amount for item in outgoing_records)
    category_totals: dict[str, float] = defaultdict(float)
    category_counts: dict[str, int] = defaultdict(int)

    for item in outgoing_records:
        category_totals[item.category] += item.amount
        category_counts[item.category] += 1

    summaries = []
    for category, total in category_totals.items():
        share = (total / outgoing_total * 100) if outgoing_total else 0
        summaries.append(CategorySummary(category, round(total, 2), category_counts[category], round(share, 1)))
    return sorted(summaries, key=lambda item: item.total, reverse=True)


def monthly_breakdown(records: list[Record]) -> list[MonthlySummary]:
    data: dict[str, dict[str, float]] = defaultdict(lambda: {"incoming": 0.0, "outgoing": 0.0})
    for item in records:
        key = item.month_key
        if item.record_type == "Incoming":
            data[key]["incoming"] += item.amount
        else:
            data[key]["outgoing"] += item.amount

    summaries = []
    for month, values in sorted(data.items()):
        incoming = round(values["incoming"], 2)
        outgoing = round(values["outgoing"], 2)
        summaries.append(MonthlySummary(month, incoming, outgoing, round(incoming - outgoing, 2)))
    return summaries


def build_alerts(records: list[Record], category_limit: float) -> list[str]:
    alerts = []
    for item in category_breakdown(records):
        if item.total > category_limit:
            alerts.append(f"{item.category} is above the selected category limit by {item.total - category_limit:.2f}.")
    if not records:
        alerts.append("Add records to generate dashboard insights.")
    return alerts


def build_report(records: list[Record], category_limit: float = 500.0) -> DashboardReport:
    incoming_total = round(sum(item.amount for item in records if item.record_type == "Incoming"), 2)
    outgoing_total = round(sum(item.amount for item in records if item.record_type == "Outgoing"), 2)
    balance = round(incoming_total - outgoing_total, 2)
    balance_rate = round((balance / incoming_total * 100), 1) if incoming_total else 0.0
    recent_records = sorted(records, key=lambda item: item.record_date, reverse=True)[:8]

    return DashboardReport(
        incoming_total=incoming_total,
        outgoing_total=outgoing_total,
        balance=balance,
        balance_rate=balance_rate,
        category_summaries=category_breakdown(records),
        monthly_summaries=monthly_breakdown(records),
        alerts=build_alerts(records, category_limit),
        recent_records=recent_records,
    )


def records_to_csv(records: list[Record]) -> str:
    lines = ["date,type,category,description,amount"]
    for item in records:
        lines.append(
            f"{item.record_date.isoformat()},{item.record_type},{item.category},{item.description},{item.amount:.2f}"
        )
    return "\n".join(lines) + "\n"
