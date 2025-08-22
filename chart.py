from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("finvoice.sqlite")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/analytics", methods=["GET"])
def analytics():
    conn = get_db()
    cur = conn.cursor()

    # Per Day (last 30 days)
    per_day = cur.execute("""
        SELECT strftime('%Y-%m-%d', ts) as day, SUM(amount) as total
        FROM expenses
        WHERE ts >= datetime('now','-30 days')
        GROUP BY day
        ORDER BY day ASC
    """).fetchall()

    # Per Week (last 12 weeks)
    per_week = cur.execute("""
        SELECT strftime('%Y-%W', ts) as week, SUM(amount) as total
        FROM expenses
        WHERE ts >= datetime('now','-90 days')
        GROUP BY week
        ORDER BY week ASC
    """).fetchall()

    # Per Month (last 12 months)
    per_month = cur.execute("""
        SELECT strftime('%Y-%m', ts) as month, SUM(amount) as total
        FROM expenses
        WHERE ts >= date('now','start of month','-11 months')
        GROUP BY month
        ORDER BY month ASC
    """).fetchall()

    # Per Year
    per_year = cur.execute("""
        SELECT strftime('%Y', ts) as year, SUM(amount) as total
        FROM expenses
        GROUP BY year
        ORDER BY year ASC
    """).fetchall()

    return jsonify({
        "perDay": [dict(r) for r in per_day],
        "perWeek": [dict(r) for r in per_week],
        "perMonth": [dict(r) for r in per_month],
        "perYear": [dict(r) for r in per_year]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
