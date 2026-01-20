# setup.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import calendar
from datetime import date

from db import get_db_connection
from config import LEVEL_2_TOWNS, LEVEL_3_TOWNS

setup_bp = Blueprint("setup", __name__)

TOWNS_WITH_RESTRICTIONS = [(t, "Level 2") for t in LEVEL_2_TOWNS] + [(t, "Level 3") for t in LEVEL_3_TOWNS]


@setup_bp.route("/setup", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        town = request.form.get("town", "").strip().upper()

        if not username:
            flash("Please enter a username.")
            return redirect(url_for("setup.setup"))

        # --- Validate town
        valid_towns = set(LEVEL_2_TOWNS) | set(LEVEL_3_TOWNS)
        if town not in valid_towns:
            flash("Please select a valid town from the list.")
            return redirect(url_for("setup.setup"))

        restriction = "Level 2" if town in LEVEL_2_TOWNS else "Level 3"

        # --- Month length (use consistently)
        days_in_month = calendar.monthrange(date.today().year, date.today().month)[1]

        # --- Budget handling
        budget_option = request.form.get("budget_option", "auto")

        if budget_option == "manual":
            try:
                monthly_budget_kl = float(request.form.get("manual_budget") or 0)
            except ValueError:
                monthly_budget_kl = 0.0

            monthly_budget_l = monthly_budget_kl * 1000.0
            daily_budget_l = monthly_budget_l / days_in_month if days_in_month else 0.0

        else:
            rate = 5 if restriction == "Level 2" else 3
            zone_count = int(request.form.get("zone_count") or 0)

            # Handle deleted zones leaving "holes" in indices
            monthly_budget_l = 0.0
            for i in range(zone_count):
                area_str = request.form.get(f"area_{i}", "")
                try:
                    area = float(area_str) if area_str != "" else 0.0
                except ValueError:
                    area = 0.0
                monthly_budget_l += area * rate * days_in_month

            daily_budget_l = monthly_budget_l / days_in_month if days_in_month else 0.0

        conn = get_db_connection()
        c = conn.cursor()

        # Prevent duplicate usernames
        c.execute("SELECT username FROM users WHERE username=?", (username,))
        if c.fetchone():
            flash("Username already exists. Please log in.")
            conn.close()
            return redirect(url_for("login"))

        # Insert new user
        c.execute("""
            INSERT INTO users (username, town, restriction_level, daily_budget_litres, monthly_budget_litres)
            VALUES (?, ?, ?, ?, ?)
        """, (username, town, restriction, daily_budget_l, monthly_budget_l))

        # --- Save zones (handle "holes" safely)
        zone_count = int(request.form.get("zone_count") or 0)

        def to_float(key, default=0.0):
            val = request.form.get(key, "")
            try:
                return float(val) if val != "" else default
            except ValueError:
                return default

        def to_int(key, default=0):
            val = request.form.get(key, "")
            try:
                return int(val) if val != "" else default
            except ValueError:
                return default

        for i in range(zone_count):
            name = request.form.get(f"name_{i}", "").strip()
            if not name:
                continue  # skip deleted/empty zones

            area = to_float(f"area_{i}", 0.0)
            sprinklers = to_int(f"sprinklers_{i}", 0)
            flow_rate = to_float(f"flow_rate_{i}", 0.0)
            source = request.form.get(f"source_{i}", "municipal")

            custom_pressure_raw = request.form.get(f"custom_pressure_{i}", "").strip()
            try:
                custom_pressure = float(custom_pressure_raw) if custom_pressure_raw else None
            except ValueError:
                custom_pressure = None

            c.execute("""
                INSERT INTO zones (user, name, area, sprinklers, flow_rate, source, custom_pressure)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, name, area, sprinklers, flow_rate, source, custom_pressure))

        conn.commit()
        conn.close()

        session["username"] = username
        return redirect(url_for("dashboard.home"))

    return render_template("setup.html", towns=TOWNS_WITH_RESTRICTIONS)
