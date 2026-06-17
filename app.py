from __future__ import annotations

from datetime import date
from pathlib import Path

import streamlit as st

from dashboard_tracker import Record, build_report, load_records_from_csv, records_to_csv

BASE_DIR = Path(__file__).parent
SAMPLE_FILE = BASE_DIR / "sample_data" / "sample_records.csv"

st.set_page_config(
    page_title="Personal Dashboard Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
.main {
    background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 48%, #f0fdf4 100%);
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.hero {
    padding: 2.25rem;
    border-radius: 30px;
    background: radial-gradient(circle at top left, rgba(16,185,129,.25), transparent 32%),
                radial-gradient(circle at bottom right, rgba(59,130,246,.24), transparent 36%),
                linear-gradient(135deg, rgba(15,23,42,.97), rgba(30,41,59,.94));
    color: white;
    box-shadow: 0 20px 50px rgba(15, 23, 42, .14);
    margin-bottom: 1.2rem;
}
.hero h1 {
    font-size: 3.05rem;
    line-height: 1.04;
    margin-bottom: .6rem;
}
.hero p {
    font-size: 1.08rem;
    color: rgba(255,255,255,.82);
    max-width: 920px;
}
.badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: .55rem;
    margin-top: 1rem;
}
.badge {
    padding: .45rem .75rem;
    border-radius: 999px;
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.20);
    font-size: .86rem;
}
.card {
    padding: 1.15rem;
    border-radius: 24px;
    background: rgba(255,255,255,.86);
    border: 1px solid rgba(148,163,184,.24);
    box-shadow: 0 14px 34px rgba(15,23,42,.08);
    min-height: 138px;
}
.card-label {
    font-size: .84rem;
    color: #64748b;
    margin-bottom: .35rem;
}
.card-value {
    font-size: 2rem;
    font-weight: 800;
    color: #0f172a;
}
.card-help {
    font-size: .88rem;
    color: #64748b;
    margin-top: .3rem;
}
.panel {
    padding: 1rem;
    border-radius: 24px;
    background: rgba(255,255,255,.78);
    border: 1px solid rgba(148,163,184,.24);
    box-shadow: 0 12px 28px rgba(15,23,42,.06);
}
.timeline-item {
    padding: .85rem 1rem;
    border-left: 4px solid #10b981;
    background: rgba(255,255,255,.84);
    border-radius: 16px;
    margin-bottom: .7rem;
    box-shadow: 0 8px 22px rgba(15,23,42,.06);
}
.small-note {
    color: #64748b;
    font-size: .92rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def default_rows() -> list[dict]:
    return [
        {"date": date(2026, 6, 1), "type": "Incoming", "category": "Salary", "description": "Monthly payment", "amount": 2200.0},
        {"date": date(2026, 6, 2), "type": "Outgoing", "category": "Rent", "description": "Apartment", "amount": 650.0},
        {"date": date(2026, 6, 3), "type": "Outgoing", "category": "Food", "description": "Groceries", "amount": 120.0},
        {"date": date(2026, 6, 4), "type": "Outgoing", "category": "Transport", "description": "Metro card", "amount": 45.0},
        {"date": date(2026, 6, 8), "type": "Outgoing", "category": "Learning", "description": "Online course", "amount": 79.0},
        {"date": date(2026, 6, 12), "type": "Incoming", "category": "Freelance", "description": "Dashboard project", "amount": 450.0},
        {"date": date(2026, 6, 15), "type": "Outgoing", "category": "Food", "description": "Cafe", "amount": 28.5},
    ]


def rows_to_records(rows) -> list[Record]:
    if hasattr(rows, "to_dict"):
        rows = rows.to_dict("records")
    records = []
    for row in rows:
        if not str(row.get("category", "")).strip():
            continue
        records.append(
            Record(
                record_date=row["date"],
                record_type=str(row.get("type", "Outgoing")),
                category=str(row.get("category", "General")).strip(),
                description=str(row.get("description", "")).strip(),
                amount=max(0.0, float(row.get("amount", 0.0) or 0.0)),
            )
        )
    return records


with st.sidebar:
    st.title("📊 Dashboard Controls")
    st.caption("Edit sample records, set a category limit, and export a clean report.")
    category_limit = st.slider("Category alert limit", 50.0, 2000.0, 500.0, 50.0)
    st.divider()
    load_sample = st.button("Load sample records", use_container_width=True)
    st.divider()
    st.markdown("### Tip")
    st.info("Use clear categories so the summary table and chart are easy to understand.")

if load_sample or "record_rows" not in st.session_state:
    if SAMPLE_FILE.exists() and load_sample:
        loaded = load_records_from_csv(SAMPLE_FILE)
        st.session_state["record_rows"] = [
            {
                "date": item.record_date,
                "type": item.record_type,
                "category": item.category,
                "description": item.description,
                "amount": item.amount,
            }
            for item in loaded
        ]
    else:
        st.session_state["record_rows"] = default_rows()

st.markdown(
    """
    <div class="hero">
      <h1>Personal Dashboard Tracker</h1>
      <p>Organize records, understand category totals, monitor monthly balance, and export polished dashboard reports.</p>
      <div class="badge-row">
        <span class="badge">Editable records</span>
        <span class="badge">Category summary</span>
        <span class="badge">Monthly trends</span>
        <span class="badge">Limit alerts</span>
        <span class="badge">Export reports</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("1. Add or edit records")
st.caption("Each row becomes part of the dashboard summary.")

edited_rows = st.data_editor(
    st.session_state["record_rows"],
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "date": st.column_config.DateColumn("Date"),
        "type": st.column_config.SelectboxColumn("Type", options=["Incoming", "Outgoing"]),
        "category": st.column_config.TextColumn("Category"),
        "description": st.column_config.TextColumn("Description"),
        "amount": st.column_config.NumberColumn("Amount", min_value=0.0, step=1.0),
    },
)

records = rows_to_records(edited_rows)
report = build_report(records, category_limit=category_limit)

st.markdown("## 2. Dashboard")

card_a, card_b, card_c, card_d = st.columns(4)
cards = [
    (card_a, "Incoming", f"{report.incoming_total:,.2f}", "Total incoming records"),
    (card_b, "Outgoing", f"{report.outgoing_total:,.2f}", "Total outgoing records"),
    (card_c, "Balance", f"{report.balance:,.2f}", "Incoming minus outgoing"),
    (card_d, "Balance Rate", f"{report.balance_rate:.1f}%", "Balance as percent of incoming"),
]

for col, label, value, help_text in cards:
    with col:
        st.markdown(
            f"""
            <div class="card">
                <div class="card-label">{label}</div>
                <div class="card-value">{value}</div>
                <div class="card-help">{help_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

if report.alerts:
    st.markdown("### Alerts")
    for alert in report.alerts:
        st.warning(alert)

left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown("### Category breakdown")
    category_rows = [
        {
            "Category": item.category,
            "Total": item.total,
            "Records": item.count,
            "Share": f"{item.share_percent}%",
        }
        for item in report.category_summaries
    ]
    st.dataframe(category_rows, use_container_width=True, hide_index=True)
    if category_rows:
        chart_data = {item["Category"]: item["Total"] for item in category_rows}
        st.bar_chart(chart_data)

with right:
    st.markdown("### Monthly summary")
    monthly_rows = [
        {
            "Month": item.month,
            "Incoming": item.incoming,
            "Outgoing": item.outgoing,
            "Balance": item.balance,
        }
        for item in report.monthly_summaries
    ]
    st.dataframe(monthly_rows, use_container_width=True, hide_index=True)
    if monthly_rows:
        chart_data = {
            item["Month"]: {"Incoming": item["Incoming"], "Outgoing": item["Outgoing"], "Balance": item["Balance"]}
            for item in monthly_rows
        }
        st.line_chart(chart_data)

st.markdown("## 3. Recent records")
if report.recent_records:
    for item in report.recent_records:
        st.markdown(
            f"""
            <div class="timeline-item">
                <strong>{item.category}</strong> · {item.record_type} · {item.amount:,.2f}<br>
                <span class="small-note">{item.record_date.isoformat()} · {item.description}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info("Add records to show recent activity.")

st.markdown("## 4. Export")
export_col1, export_col2, export_col3 = st.columns(3)
with export_col1:
    st.download_button(
        "Download CSV",
        data=records_to_csv(records),
        file_name="dashboard_records.csv",
        mime="text/csv",
        use_container_width=True,
    )
with export_col2:
    st.download_button(
        "Download JSON report",
        data=report.to_json(),
        file_name="dashboard_report.json",
        mime="application/json",
        use_container_width=True,
    )
with export_col3:
    st.download_button(
        "Download text report",
        data=report.to_text(),
        file_name="dashboard_report.txt",
        mime="text/plain",
        use_container_width=True,
    )
