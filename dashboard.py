# dashboard.py
from flask import Blueprint, render_template, request, redirect, url_for, session
import calendar
from datetime import date, timedelta

from db import get_db_connection
from tips import get_tip

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/home", methods=["GET", "POST"])
def home():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    conn = get_db_connection()
    cur = conn.cursor()

    # --- Get user profile (daily + monthly budget must exist)
    user = cur.execute("""
        SELECT town, restriction_level, daily_budget_litres, monthly_budget_litres
        FROM users
        WHERE username=?
    """, (username,)).fetchone()

    if not user:
        conn.close()
        return redirect(url_for("setup.setup"))

    town = user["town"]
    restriction_level = user["restriction_level"]
    daily_budget_l = user["daily_budget_litres"] or 0
    monthly_budget_l = user["monthly_budget_litres"] or 0

    # --- Handle irrigation logging (POST)
    if request.method == "POST":
        zones = cur.execute(
            "SELECT * FROM zones WHERE user=?",
            (username,)
        ).fetchall()

        for zone in zones:
            field_name = f"duration_{zone['id']}"
            minutes_str = request.form.get(field_name, "").strip()

            if not minutes_str:
                continue

            try:
                minutes = float(minutes_str)
            except ValueError:
                continue

            if minutes <= 0:
                continue

            flow_rate = zone["flow_rate"] or 0
            usage_l = flow_rate * minutes

            cur.execute("""
                INSERT INTO usage (user, date, zone_name, duration, water_used)
                VALUES (?, DATE('now'), ?, ?, ?)
            """, (username, zone["name"], minutes, usage_l))

        conn.commit()

    # --- Zones (always load for GET + POST)
    zones = cur.execute(
        "SELECT * FROM zones WHERE user=?",
        (username,)
    ).fetchall()

    today = date.today()

    # --- Today's usage breakdown
    results = []
    for zone in zones:
        row = cur.execute("""
            SELECT
                SUM(duration)  AS total_duration,
                SUM(water_used) AS total_used
            FROM usage
            WHERE user=? AND zone_name=? AND date=?
        """, (username, zone["name"], str(today))).fetchone()

        duration = (row["total_duration"] or 0) if row else 0
        usage = (row["total_used"] or 0) if row else 0

        results.append({
            "name": zone["name"],
            "duration": duration,
            "usage": usage
        })

    # --- Weekly & monthly usage + budgets
    weekly_budget_l = daily_budget_l * 7
    monday = today - timedelta(days=today.weekday())

    weekly_usage = cur.execute("""
        SELECT SUM(water_used) AS total
        FROM usage
        WHERE user=? AND date >= ? AND date <= ?
    """, (username, str(monday), str(today))).fetchone()

    weekly_usage = weekly_usage["total"] or 0

    monthly_usage = cur.execute("""
        SELECT SUM(water_used) AS total
        FROM usage
        WHERE user=? AND strftime('%Y-%m', date)=?
    """, (username, today.strftime("%Y-%m"))).fetchone()

    monthly_usage = monthly_usage["total"] or 0

    weekly_percent_used = round((weekly_usage / weekly_budget_l) * 100, 1) if weekly_budget_l else 0
    monthly_percent_used = round((monthly_usage / monthly_budget_l) * 100, 1) if monthly_budget_l else 0

    # --- Table + weekly chart percentages (against full weekly budget)
    zone_percentages = []
    for r in results:
        percent = round((r["usage"] / weekly_budget_l) * 100, 1) if weekly_budget_l else 0
        zone_percentages.append({
            "name": r["name"],
            "duration": r["duration"],
            "usage": r["usage"],
            "percent_of_budget": percent
        })

    # --- Monthly stats (cumulative, avg, projected)
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_so_far = today.day

    cumulative_usage_kl = round(monthly_usage / 1000, 2)
    avg_usage_kl_per_day = round(cumulative_usage_kl / days_so_far, 2) if days_so_far else 0
    projected_end_month_kl = round(avg_usage_kl_per_day * days_in_month, 2)

    monthly_stats = {
        "cumulative": cumulative_usage_kl,
        "monthly_avg": avg_usage_kl_per_day,
        "projected": projected_end_month_kl
    }

    # --- Chart: Weekly zone % bar
    zone_labels = [r["name"] for r in zone_percentages]
    zone_values = [r["percent_of_budget"] for r in zone_percentages]

    # --- Chart: Monthly zone usage (KL)
    monthly_zone_labels = [r["name"] for r in results]
    monthly_zone_values = [round((r["usage"] or 0) / 1000, 2) for r in results]

    # --- Chart: Daily cumulative usage (this month)
    first_day = today.replace(day=1)
    daily_rows = cur.execute("""
        SELECT date, SUM(water_used) AS total
        FROM usage
        WHERE user=? AND date >= ?
        GROUP BY date
        ORDER BY date
    """, (username, str(first_day))).fetchall()

    daily_usage_labels = list(range(1, days_in_month + 1))
    usage_dict = {int(row["date"].split("-")[2]): (row["total"] or 0) for row in daily_rows}

    cumulative = 0
    daily_usage_values = []
    for day in range(1, days_in_month + 1):
        cumulative += usage_dict.get(day, 0)
        daily_usage_values.append(round(cumulative / 1000, 2))

    projection_series = [None] * (days_in_month - 1) + [projected_end_month_kl]

    conn.close()

    return render_template(
        "index.html",
        today=today,
        town=town,
        restriction_level=restriction_level,
        weekly_budget_kl=round(weekly_budget_l / 1000, 2),
        monthly_budget_kl=round(monthly_budget_l / 1000, 2),
        weekly_percent_used=weekly_percent_used,
        monthly_percent_used=monthly_percent_used,
        zones=zones,
        zone_percentages=zone_percentages,
        monthly_stats=monthly_stats,
        zone_labels=zone_labels,
        zone_values=zone_values,
        monthly_zone_labels=monthly_zone_labels,
        monthly_zone_values=monthly_zone_values,
        daily_usage_labels=daily_usage_labels,
        daily_usage_values=daily_usage_values,
        projection_series=projection_series,
        water_tip=get_tip(),
    )

