from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, math, calendar
from datetime import date, timedelta
from calculations import get_monthly_stats, get_zone_percentages
from db import init_db, DB_NAME, get_db_connection
from config import LEVEL_2_TOWNS, LEVEL_3_TOWNS
from tips import get_tip  
from setup import setup_bp
from dashboard import dashboard_bp

app = Flask(__name__)
app.secret_key = "change_me"
init_db()

app.register_blueprint(setup_bp)
app.register_blueprint(dashboard_bp)

TOWNS_WITH_RESTRICTIONS = [(t, "Level 2") for t in LEVEL_2_TOWNS] + [(t, "Level 3") for t in LEVEL_3_TOWNS]

def db_conn():
    return get_db_connection()

def current_user():
    if "username" not in session:
        return None

    conn = get_db_connection()
    c = conn.cursor()
    row = c.execute("""
        SELECT username, town, restriction_level, daily_budget_litres, monthly_budget_litres
        FROM users
        WHERE username=?
    """, (session["username"],)).fetchone()
    conn.close()

    if not row:
        return None

    return {
        "username": row["username"],
        "town": row["town"],
        "restriction": row["restriction_level"],
        "daily_budget": row["daily_budget_litres"],
        "monthly_budget": row["monthly_budget_litres"],
    }


@app.route("/")
def root():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if not username:
            flash("Please enter a username.")
            return render_template("login.html")
        conn = db_conn()
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE username=?", (username,))
        row = c.fetchone()
        conn.close()
        if row:
            session["username"] = row["username"]
            return redirect(url_for("dashboard.home"))
        else:
            flash("Profile not found. Please create one.")
            return redirect(url_for("setup.setup"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/add_zone", methods=["GET", "POST"])
def add_zone():
    user = current_user()
    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()

        def to_float(key, default=0.0):
            raw = (request.form.get(key) or "").strip()
            try:
                return float(raw) if raw else default
            except ValueError:
                return default

        def to_int(key, default=0):
            raw = (request.form.get(key) or "").strip()
            try:
                return int(raw) if raw else default
            except ValueError:
                return default

        area = to_float("area", 0.0)
        sprinklers = to_int("sprinklers", 0)
        flow_rate = to_float("flow_rate", 0.0)
        source = request.form.get("source", "municipal")

        custom_pressure_raw = (request.form.get("custom_pressure") or "").strip()
        try:
            custom_pressure = float(custom_pressure_raw) if custom_pressure_raw else None
        except ValueError:
            custom_pressure = None

        conn = db_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO zones (user, name, area, sprinklers, flow_rate, source, custom_pressure)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user["username"], name, area, sprinklers, flow_rate, source, custom_pressure))
        conn.commit()
        conn.close()

        return redirect(url_for("dashboard.home"))

    return render_template("add_zone.html")


@app.route("/edit_budget", methods=["GET", "POST"])
def edit_budget():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    conn = get_db_connection()
    c = conn.cursor()

    days_in_month = calendar.monthrange(date.today().year, date.today().month)[1]

    if request.method == "POST":
        raw = (request.form.get("monthly_budget_kl") or "").strip()
        try:
            new_budget_kl = float(raw) if raw else 0.0
        except ValueError:
            new_budget_kl = 0.0

        new_budget_l = new_budget_kl * 1000.0
        new_daily_l = new_budget_l / days_in_month if days_in_month else 0.0

        c.execute("""
            UPDATE users
            SET monthly_budget_litres=?, daily_budget_litres=?
            WHERE username=?
        """, (new_budget_l, new_daily_l, username))

        conn.commit()
        conn.close()
        return redirect(url_for("dashboard.home"))

    row = c.execute("""
        SELECT monthly_budget_litres
        FROM users
        WHERE username=?
    """, (username,)).fetchone()

    conn.close()

    monthly_litres = (row["monthly_budget_litres"] or 0) if row else 0
    current_budget_kl = round(monthly_litres / 1000.0, 2)

    return render_template("edit_budget.html", monthly_budget_kl=current_budget_kl)


@app.route("/delete_zone/<int:zone_id>", methods=["POST"])
def delete_zone(zone_id):
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    conn.execute("DELETE FROM zones WHERE id=? AND user=?", (zone_id, session["username"]))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard.home"))


if __name__ == "__main__":
    app.run(debug=True)

