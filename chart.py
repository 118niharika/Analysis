from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

# ----------------------
# Initialize Flask
# ----------------------
app = Flask(_name_, static_folder=".")
CORS(app)

# ----------------------
# DB helper
# ----------------------
def get_db():
    conn = sqlite3.connect("finvoice.sqlite")
    conn.row_factory = sqlite3.Row
    return conn

# ----------------------
# Analytics API
# ----------------------
@app.route("/analytics", methods=["GET"])
def analytics():
    conn = get_db()
    cur = conn.cursor()
    now = datetime.now()

    # Last 30 days expenses
    rows = cur.execute(
        "SELECT * FROM expenses WHERE strftime('%m', ts) = ? AND strftime('%Y', ts) = ? ORDER BY ts ASC",
        (f"{now.month:02d}", str(now.year))
    ).fetchall()
    last30 = [dict(r) for r in rows]

    # Aggregate by day/week/month/year
    per_day = cur.execute("""
        SELECT strftime('%Y-%m-%d', ts) as day, SUM(amount) as total
        FROM expenses
        WHERE ts >= datetime('now','-30 days')
        GROUP BY day
        ORDER BY day ASC
    """).fetchall()

    per_week = cur.execute("""
        SELECT strftime('%Y-%W', ts) as week, SUM(amount) as total
        FROM expenses
        WHERE ts >= datetime('now','-90 days')
        GROUP BY week
        ORDER BY week ASC
    """).fetchall()

    per_month = cur.execute("""
        SELECT strftime('%Y-%m', ts) as month, SUM(amount) as total
        FROM expenses
        WHERE ts >= date('now','start of month','-11 months')
        GROUP BY month
        ORDER BY month ASC
    """).fetchall()

    per_year = cur.execute("""
        SELECT strftime('%Y', ts) as year, SUM(amount) as total
        FROM expenses
        GROUP BY year
        ORDER BY year ASC
    """).fetchall()

    # Category breakdown
    by_cat = {}
    for e in last30:
        by_cat[e["category"]] = by_cat.get(e["category"], 0) + e["amount"]

    return jsonify({
        "categoryBreakdown": by_cat,
        "perDay": [dict(r) for r in per_day],
        "perWeek": [dict(r) for r in per_week],
        "perMonth": [dict(r) for r in per_month],
        "perYear": [dict(r) for r in per_year]
    })

# ----------------------
# Serve HTML
# ----------------------
@app.route("/")
def index():
    return send_from_directory(os.path.dirname(os.path.abspath(_file_)), "chart.html")

# ----------------------
# Run App
# ----------------------
if _name_ == "_main_":
    app.run(host="0.0.0.0", port=5000, debug=True)
