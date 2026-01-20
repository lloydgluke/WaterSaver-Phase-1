"""
tips.py
-------
Provides random water-saving tips for display in the dashboard.
Tips are written with light HTML markup (bold, lists, etc.)
to render nicely in templates.
"""

import random

# List of water-saving tips (with HTML for formatting)
TIPS = [
    "<strong>Water early or late:</strong> Water your garden during the early morning or late evening to minimise evaporation.",
    "<strong>Use mulch:</strong> Mulch keeps soil moist, regulates temperature, and improves long-term soil health.",
    "<strong>Collect rainwater:</strong> Store water in barrels during wet periods for later use in dry spells.",
    "<strong>Drip irrigation:</strong> Deliver water directly to plant roots to reduce runoff and evaporation.",
    "<strong>Hand watering:</strong> Gives you better control over plant hydration and avoids overwatering.",
    "<strong>Group plants by water needs:</strong> Hydrozoning ensures efficient irrigation across plant types.",
    "<strong>Avoid overwatering:</strong> Test soil moisture before irrigating to prevent root rot and disease.",
    "<strong>Use greywater:</strong> Reuse safe household water (e.g. from sinks/showers) for non-edible plants.",
    "<strong>Vertical gardening:</strong> Reduces evaporation and maximises space efficiency in small gardens."
]

def get_tip():
    """Pick and return a random water-saving tip."""
    return random.choice(TIPS)


