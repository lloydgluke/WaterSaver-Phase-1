"""
config.py
---------
Central configuration for WaterSaver.
Defines default irrigation pressures, restriction levels,
and daily water allocation rates for towns in Hessequa.
"""

SECRET_KEY = "your-secret-key"

# Default irrigation water pressures by source (in bar)
DEFAULT_PRESSURES = {
    "municipal": 3.0,       # Typical municipal supply pressure
    "borehole": 2.5,        # Borehole pumps generally lower
    "rain_tank": 1.5,       # Gravity-fed rain tanks
    "dam_reservoir": 2.0    # Reservoir or dam outlets
}

# Hessequa restriction levels: towns classified by restriction stage
LEVEL_2_TOWNS = [
    "GOURITSMOND",
    "STILL BAY",
    "MELKHOUTFONTEIN",
    "RIVERSDALE"
]

LEVEL_3_TOWNS = [
    "ALBERTINIA",
    "HEIDELBERG",
    "SLANGRIVIER",
    "JONGENSFONTEIN",
    "WITSAND"
]

# Daily irrigation allowance per square metre, based on restriction level
LEVEL_2_RATE = 5  # litres per m² per day
LEVEL_3_RATE = 3  # litres per m² per day

