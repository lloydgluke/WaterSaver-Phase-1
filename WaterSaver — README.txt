WaterSaver — README
===================

Purpose
-------
WaterSaver is a Flask‑based water usage tracking dashboard for households and farms in Hessequa, South Africa.

It helps you:
- Track daily irrigation per zone
- Monitor usage against daily, weekly, and monthly budgets
- View historical usage trends
- Get water‑saving tips
- Automatically adjust for municipal restriction levels

Language & Framework
--------------------
- **Programming Language:** Python 3.x
- **Framework:** Flask (Python web framework)
- **Database:** SQLite (lightweight, file‑based database)
- **Frontend:** HTML5, CSS3, JavaScript (Chart.js for graphs)

Prerequisites
-------------
Before running WaterSaver, ensure you have:
- Python 3.8 or newer installed
- `pip` (Python package installer) available in your PATH

Quick Installation
------------------
1. **Install Python 3.8+**  
   Confirm `python --version` and `pip --version` work in your terminal.

2. **Download or clone** this project folder.

3. **Open a terminal** in the project folder.

4. **(Optional) Create a virtual environment**:
	python -m venv venv
   Activate it:
   - Windows: venv\Scripts\activate
   - macOS/Linux: source venv/bin/activate

5. **Install all dependencies** (from `requirements.txt`):
   pip install -r requirements.txt

6. **Initialize the database** (first time only):
   python -c "from db import init_db; init_db()"

7. **Run the app**:
   python main.py

8. **Open your browser** and go to:
   http://127.0.0.1:5000

9. **Create your profile** on the Setup page, add zones, and start logging usage.

File Structure
--------------
- `main.py` — Flask app entry point and route handling
- `db.py` — Database initialization and connection helpers
- `config.py` — Restriction levels, rates, and default pressures
- `calculations.py` — Monthly and zone usage calculations
- `lasher.py` — Random water‑saving tips
- `templates/` — HTML templates for pages
- `usage.db` — SQLite database file (created after first run)

Tips
----
- To reset all usage logs for a profile, use the "Clear All Usage" button in the dashboard.
- To add or edit zones later, use the "Add Zone" or "Edit" links in the dashboard.
- Budgets are stored in litres in the database but displayed in kilolitres (KL) in the UI.

Support
-------
If you encounter issues:
- Ensure Python and pip are installed and up to date.
- Check that all required packages are installed.
- If the database is missing columns or corrupted, delete `usage.db` and re‑run the database initialization.

