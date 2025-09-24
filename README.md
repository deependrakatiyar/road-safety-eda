# Road Safety EDA (Streamlit)

A lightweight exploratory analysis app over a sample *accidents* dataset. Filter by date/district and see quick summaries & charts. You can replace the sample CSV with **IRAD**/police data exported to CSV.

## How to run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Files
- `data/accidents.csv` – sample dataset (replace with real data when available)
- `app.py` – Streamlit dashboard (no internet needed)
