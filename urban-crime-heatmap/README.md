# 🔴 CrimeScope — Urban Crime Intelligence Platform

> Data-driven analysis of global crime patterns using ML models, interactive maps, and real-time synthesized public data.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?style=flat-square&logo=streamlit)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4+-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📸 Features

| Page | Description |
|------|-------------|
| 🌍 **World Heatmap** | Choropleth world map + city-level density hotspot map |
| 📊 **Analytics Dashboard** | Trends, radar, heatmap matrix, correlation lab, animated scatter |
| 🤖 **Crime Predictor** | Random Forest / GBM / Ridge ensemble + 2040 forecast |
| 🔬 **Anomaly Radar** | Isolation Forest + Z-Score outlier detection |
| 📋 **Data Explorer** | Filterable table, CSV export, socioeconomic panel |

---

## 🚀 Quick Start

```bash
git clone https://github.com/your-username/urban-crime-heatmap.git
cd urban-crime-heatmap
pip install -r requirements.txt
streamlit run app.py
```

---

## ☁️ Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path**: `app.py`
5. Click **Deploy** — live in ~60 seconds!

---

## 📁 Project Structure

```
urban-crime-heatmap/
├── app.py                  # Main entry point + sidebar
├── requirements.txt
├── .streamlit/
│   └── config.toml         # Dark theme config
├── pages/
│   ├── heatmap.py          # World + city maps
│   ├── analytics.py        # Multi-chart analytics
│   ├── predictor.py        # ML crime predictor
│   ├── anomaly.py          # Anomaly detection
│   ├── explorer.py         # Data table & export
│   └── about.py
├── models/
│   └── __init__.py
└── utils/
    ├── data_loader.py      # Data synthesis + helpers
    ├── charts.py           # Plotly chart helpers
    └── theme.py            # CSS + colour tokens
```

---

## 🧠 ML Models

- **Random Forest Regressor** — 200 trees, max_depth=8, cross-validated R²
- **Gradient Boosting Regressor** — 150 estimators, learning_rate=0.08
- **Ridge Regression** — Regularised linear baseline
- **Isolation Forest** — Anomaly detection (contamination=8%)
- **Features**: Year, GDP, Unemployment, Urbanisation, Gini, Police Density, Country, Crime Type

---

## 📊 Data Sources

- [UNODC Crime Statistics](https://dataunodc.un.org)
- [World Bank Open Data](https://data.worldbank.org)
- [Global Peace Index](https://visionofhumanity.org)
- [Numbeo Crime Database](https://www.numbeo.com/crime/)
- [FBI UCR / NIBRS](https://ucr.fbi.gov)

---

## 📄 License

MIT © 2024 CrimeScope
