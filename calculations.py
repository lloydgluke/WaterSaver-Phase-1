"""
calculations.py
---------------
Helper functions for computing water usage statistics.
Handles monthly cumulative stats and zone-level percentage breakdowns.
"""

from datetime import date
import calendar
from db import get_db_connection


def calculate_usage(flow_rate, duration_minutes):
    """
    Calculate water used in kilolitres based on flow rate (L/min) and duration (min).
    """
    litres = (flow_rate or 0) * (duration_minutes or 0)
    return round(litres / 1000, 2)


def calculate_budget_status(total_usage_kl, daily_budget_kl):
    """
    Return percentage of budget used and status label.
    """
    if not daily_budget_kl:
        return 0.0, "Safe"

    percent = round((total_usage_kl / daily_budget_kl) * 100, 1)
    if percent < 50:
        return percent, "Safe"
    elif percent < 90:
        return percent, "Caution"
    else:
        return percent, "Exceeded"


def get_monthly_stats(username, daily_budget_litres):
    """
    Calculate monthly statistics for a specific user.

    Args:
        username (str): Logged-in username.
        daily_budget_litres (float): Daily budget in litres.

    Returns:
        dict: cumulative usage (KL), daily average (KL/day),
              projected monthly usage (KL), days under/over budget,
              and water saved (KL).
    """
    today = date.today()
    first_day = today.replace(day=1)
    days_in_month = calendar.monthrange(today.year, today.month)[1]

    conn = get_db_connection()
    c = conn.cursor()

    # Total usage for this month so far (for this user)
    row = c.execute("""
        SELECT SUM(water_used) AS total
        FROM usage
        WHERE user=? AND date >= ?
    """, (username, str(first_day))).fetchone()
    cumulative = (row["total"] or 0) if row else 0

    # Daily totals for budget comparison (for this user)
    daily_totals = c.execute("""
        SELECT date, SUM(water_used) AS total
        FROM usage
        WHERE user=? AND date >= ?
        GROUP BY date
    """, (username, str(first_day))).fetchall()

    conn.close()

    # Count days under/over budget and total litres saved
    days_under = sum(1 for r in daily_totals if (r["total"] or 0) <= daily_budget_litres)
    days_over = sum(1 for r in daily_totals if (r["total"] or 0) > daily_budget_litres)
    water_saved = sum(
        (daily_budget_litres - (r["total"] or 0))
        for r in daily_totals
        if (r["total"] or 0) < daily_budget_litres
    )

    # Compute averages and projections
    days_passed = today.day
    monthly_avg_litres = cumulative / days_passed if days_passed else 0
    projected_litres = monthly_avg_litres * days_in_month

    return {
        "cumulative": round(cumulative / 1000, 2),                 # litres → KL
        "monthly_avg": round(monthly_avg_litres / 1000, 2),        # litres → KL/day
        "projected": round(projected_litres / 1000, 2),            # litres → KL
        "days_under": days_under,
        "days_over": days_over,
        "water_saved": round(water_saved / 1000, 2)                # litres → KL
    }


def get_zone_percentages(results, budget_litres):
    """
    Add percentage-of-budget values to each zone usage result.

    Args:
        results (list of dict): Each dict has at least {"usage": litres}.
        budget_litres (float): Total budget in litres.

    Returns:
        list of dict: Same as input, with "percent_of_budget" added.
    """
    return [
        {
            **zone,
            "percent_of_budget": round((zone["usage"] / budget_litres) * 100, 1) if budget_litres else 0
        }
        for zone in results
    ]
