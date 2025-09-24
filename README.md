# 🚦 Road Safety EDA (Streamlit)

A lightweight Streamlit dashboard for **quick exploratory analysis of road-accident data**.  
Filter by district and date range, view monthly trends, and see cause breakdowns.  
Ships with a small sample CSV; simply swap in **IRAD / Police** exports to analyze real data.

---

## ✨ Features
- Interactive filters for **Date** and **District**
- Key metrics: **Incidents • Injuries • Fatalities**
- Charts:
  - **Incidents by Month**
  - **Causes Breakdown**
- Runs fully **offline**—no external database required

---

## 📂 Project Structure
road-safety-eda/
├─ app.py # Streamlit dashboard
├─ requirements.txt # Python dependencies
├─ README.md # Project documentation (this file)
├─ LICENSE # MIT license
└─ data/
└─ accidents.csv # Sample dataset (replace with real data when available)

---

## ⚙️ Quickstart

### Option A — Using Conda (recommended)
```bash
conda create -n roadsafety python=3.11 -y
conda activate roadsafety
pip install -r requirements.txt
streamlit run app.py
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
Open the Local URL shown in the terminal (e.g. http://localhost:8501) to use the dashboard.
Data Format

Your CSV should have the following columns:

column	type	example
date	date	2025-05-12
district	string	Raisen
injuries	integer	3
fatalities	integer	1
cause	string	Overspeeding

To use your own data: export it to CSV, name it accidents.csv, and place it inside the data/ folder.

---

### How to use
1. In the GitHub editor where you have `README.md` open, **Ctrl +A** to select all existing text.
2. **Paste** everything above to replace it.
3. Add a short commit message like `Revamp README with full project details`.
4. Click **Commit changes**.

Your repository will immediately display this polished, complete README.
