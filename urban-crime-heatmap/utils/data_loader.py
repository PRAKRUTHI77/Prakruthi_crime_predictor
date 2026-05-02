"""
utils/data_loader.py
Synthesises realistic crime statistics modelled on UNODC public data.
Real public source: https://dataunodc.un.org/dp-intentional-homicide-victims
"""

import numpy as np
import pandas as pd
import streamlit as st

COUNTRY_META = {
    "United States":  {"iso": "USA", "lat": 37.09,  "lon": -95.71,  "region": "Americas",     "flag": "🇺🇸"},
    "United Kingdom": {"iso": "GBR", "lat": 55.38,  "lon": -3.44,   "region": "Europe",       "flag": "🇬🇧"},
    "Germany":        {"iso": "DEU", "lat": 51.17,  "lon": 10.45,   "region": "Europe",       "flag": "🇩🇪"},
    "France":         {"iso": "FRA", "lat": 46.23,  "lon": 2.21,    "region": "Europe",       "flag": "🇫🇷"},
    "India":          {"iso": "IND", "lat": 20.59,  "lon": 78.96,   "region": "Asia",         "flag": "🇮🇳"},
    "Brazil":         {"iso": "BRA", "lat": -14.24, "lon": -51.93,  "region": "Americas",     "flag": "🇧🇷"},
    "Mexico":         {"iso": "MEX", "lat": 23.63,  "lon": -102.55, "region": "Americas",     "flag": "🇲🇽"},
    "South Africa":   {"iso": "ZAF", "lat": -30.56, "lon": 22.94,   "region": "Africa",       "flag": "🇿🇦"},
    "Nigeria":        {"iso": "NGA", "lat": 9.08,   "lon": 8.68,    "region": "Africa",       "flag": "🇳🇬"},
    "Australia":      {"iso": "AUS", "lat": -25.27, "lon": 133.78,  "region": "Oceania",      "flag": "🇦🇺"},
    "Canada":         {"iso": "CAN", "lat": 56.13,  "lon": -106.35, "region": "Americas",     "flag": "🇨🇦"},
    "Russia":         {"iso": "RUS", "lat": 61.52,  "lon": 105.32,  "region": "Europe",       "flag": "🇷🇺"},
    "China":          {"iso": "CHN", "lat": 35.86,  "lon": 104.20,  "region": "Asia",         "flag": "🇨🇳"},
    "Japan":          {"iso": "JPN", "lat": 36.20,  "lon": 138.25,  "region": "Asia",         "flag": "🇯🇵"},
    "South Korea":    {"iso": "KOR", "lat": 35.91,  "lon": 127.77,  "region": "Asia",         "flag": "🇰🇷"},
    "Saudi Arabia":   {"iso": "SAU", "lat": 23.89,  "lon": 45.08,   "region": "Middle East",  "flag": "🇸🇦"},
    "Argentina":      {"iso": "ARG", "lat": -38.42, "lon": -63.62,  "region": "Americas",     "flag": "🇦🇷"},
}

CRIME_TYPES = [
    "Homicide", "Robbery", "Assault", "Theft",
    "Burglary", "Drug Offenses", "Sexual Violence",
]

YEARS = list(range(2010, 2024))

# Base homicide rate per 100k — UNODC 2022 reference values
BASE_HOMICIDE = {
    "United States": 6.3,  "United Kingdom": 1.1,  "Germany": 0.9,
    "France": 1.3,         "India": 2.8,            "Brazil": 22.4,
    "Mexico": 29.1,        "South Africa": 41.0,    "Nigeria": 34.5,
    "Australia": 0.9,      "Canada": 1.8,           "Russia": 6.8,
    "China": 0.5,          "Japan": 0.2,            "South Korea": 0.6,
    "Saudi Arabia": 1.5,   "Argentina": 5.1,
}

CRIME_MUL = {
    "Homicide": 1.0, "Robbery": 45, "Assault": 120,
    "Theft": 500, "Burglary": 180, "Drug Offenses": 90, "Sexual Violence": 35,
}

# Socioeconomic data (gdp/cap, unemployment%, urbanisation%, gini, police/100k)
SOCIO = {
    "United States":  (65000, 3.8,  82, 39.5, 240),
    "United Kingdom": (45000, 4.1,  84, 33.1, 210),
    "Germany":        (50000, 3.0,  77, 31.7, 290),
    "France":         (44000, 8.5,  81, 32.4, 185),
    "India":          (7000,  7.0,  35, 35.7, 145),
    "Brazil":         (15000, 12.5, 87, 52.9, 100),
    "Mexico":         (19000, 3.5,  80, 45.4, 98),
    "South Africa":   (13000, 32.0, 67, 63.0, 185),
    "Nigeria":        (5000,  23.0, 53, 43.0, 20),
    "Australia":      (55000, 4.5,  86, 34.4, 212),
    "Canada":         (52000, 5.5,  81, 33.3, 200),
    "Russia":         (27000, 4.8,  74, 37.5, 405),
    "China":          (18000, 4.0,  64, 38.2, 155),
    "Japan":          (42000, 2.8,  92, 32.1, 205),
    "South Korea":    (40000, 3.5,  82, 31.4, 195),
    "Saudi Arabia":   (53000, 5.5,  84, 45.9, 180),
    "Argentina":      (20000, 10.2, 93, 42.3, 182),
}


@st.cache_data(ttl=3600, show_spinner=False)
def build_global_dataframe() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    rows = []
    for country, meta in COUNTRY_META.items():
        base  = BASE_HOMICIDE[country]
        trend = -0.012 if meta["region"] in ("Europe", "Oceania", "Asia") else -0.004
        for year in YEARS:
            yf = 1 + trend * (year - 2010) + rng.normal(0, 0.04)
            for crime in CRIME_TYPES:
                rate = base * CRIME_MUL[crime] * yf * rng.uniform(0.88, 1.12)
                rows.append({
                    "country":      country,
                    "iso":          meta["iso"],
                    "lat":          meta["lat"],
                    "lon":          meta["lon"],
                    "region":       meta["region"],
                    "year":         year,
                    "crime_type":   crime,
                    "rate_per_100k": max(0.01, rate),
                })
    return pd.DataFrame(rows)


@st.cache_data(ttl=3600, show_spinner=False)
def get_country_data(country: str, crime_types: list, year_range: tuple) -> pd.DataFrame:
    df = build_global_dataframe()
    return df[
        (df["country"] == country) &
        (df["crime_type"].isin(crime_types)) &
        (df["year"].between(*year_range))
    ].copy()


@st.cache_data(ttl=3600, show_spinner=False)
def get_latest_snapshot(crime_types: list, year: int = 2022) -> pd.DataFrame:
    df = build_global_dataframe()
    snap = (
        df[(df["year"] == year) & (df["crime_type"].isin(crime_types))]
        .groupby(["country", "iso", "lat", "lon", "region"])["rate_per_100k"]
        .mean()
        .reset_index()
        .rename(columns={"rate_per_100k": "avg_rate"})
    )
    return snap


@st.cache_data(ttl=3600, show_spinner=False)
def get_timeseries(country: str, crime_types: list, year_range: tuple) -> pd.DataFrame:
    df = get_country_data(country, crime_types, year_range)
    return df.groupby(["year", "crime_type"])["rate_per_100k"].mean().reset_index()


@st.cache_data(ttl=3600, show_spinner=False)
def get_city_hotspots(country: str) -> pd.DataFrame:
    CITIES = {
        "United States":  [("New York",40.71,-74.01,55),("Los Angeles",34.05,-118.24,62),
                           ("Chicago",41.88,-87.63,78),("Houston",29.76,-95.37,61),
                           ("Philadelphia",39.95,-75.17,70),("Detroit",42.33,-83.05,88),
                           ("Baltimore",39.29,-76.61,85),("Memphis",35.15,-90.05,80)],
        "Brazil":         [("São Paulo",-23.55,-46.63,71),("Rio de Janeiro",-22.91,-43.17,85),
                           ("Fortaleza",-3.72,-38.54,90),("Salvador",-12.97,-38.51,82),
                           ("Manaus",-3.10,-60.02,75)],
        "India":          [("Delhi",28.70,77.10,65),("Mumbai",19.08,72.88,52),
                           ("Bangalore",12.97,77.59,48),("Kolkata",22.57,88.36,58),
                           ("Chennai",13.08,80.27,50),("Hyderabad",17.38,78.49,45)],
        "South Africa":   [("Johannesburg",-26.20,28.04,95),("Cape Town",-33.93,18.42,88),
                           ("Durban",-29.86,31.02,82),("Pretoria",-25.75,28.19,75)],
        "Mexico":         [("Mexico City",19.43,-99.13,78),("Tijuana",32.52,-117.04,95),
                           ("Juárez",31.74,-106.49,92),("Guadalajara",20.66,-103.35,68),
                           ("Monterrey",25.69,-100.32,72)],
        "United Kingdom": [("London",51.51,-0.13,55),("Manchester",53.48,-2.24,62),
                           ("Birmingham",52.49,-1.90,65),("Liverpool",53.41,-2.99,60),
                           ("Leeds",53.80,-1.55,57)],
        "Germany":        [("Berlin",52.52,13.40,42),("Hamburg",53.55,9.99,45),
                           ("Munich",48.14,11.58,30),("Cologne",50.94,6.96,40)],
        "France":         [("Paris",48.86,2.35,58),("Marseille",43.30,5.37,72),
                           ("Lyon",45.75,4.83,55),("Toulouse",43.60,1.44,48)],
        "Russia":         [("Moscow",55.75,37.62,62),("Saint Petersburg",59.94,30.32,55),
                           ("Novosibirsk",54.99,82.90,50),("Ekaterinburg",56.84,60.60,58)],
        "Nigeria":        [("Lagos",6.52,3.38,88),("Abuja",9.07,7.40,70),
                           ("Kano",12.00,8.52,78),("Ibadan",7.38,3.90,75)],
        "China":          [("Shanghai",31.23,121.47,25),("Beijing",39.90,116.41,22),
                           ("Guangzhou",23.13,113.26,28),("Shenzhen",22.54,114.06,20)],
        "Japan":          [("Tokyo",35.69,139.69,10),("Osaka",34.69,135.50,12),
                           ("Yokohama",35.44,139.64,11),("Nagoya",35.18,136.91,10)],
        "Australia":      [("Sydney",-33.87,151.21,42),("Melbourne",-37.81,144.96,40),
                           ("Brisbane",-27.47,153.02,45),("Perth",-31.95,115.86,38)],
        "Canada":         [("Toronto",43.65,-79.38,45),("Vancouver",49.25,-123.12,48),
                           ("Montreal",45.50,-73.57,50),("Calgary",51.05,-114.07,40)],
    }
    rng = np.random.default_rng(hash(country) % (2**31))
    meta = COUNTRY_META[country]
    entries = CITIES.get(country, [
        (f"City {i+1}", meta["lat"] + rng.uniform(-5,5), meta["lon"] + rng.uniform(-5,5),
         int(rng.integers(25, 90))) for i in range(6)
    ])
    return pd.DataFrame(entries, columns=["city", "lat", "lon", "crime_index"])


def safety_index(rate: float) -> tuple:
    if rate < 5:   return "VERY SAFE", "#00ff9d"
    if rate < 15:  return "MODERATE", "#ffaa00"
    if rate < 40:  return "HIGH RISK", "#ff6b35"
    return "CRITICAL", "#ff3366"


def risk_score(country: str, crime_types: list) -> dict:
    """Return a dict of insight metrics for a country."""
    df = build_global_dataframe()
    c  = df[(df["country"] == country) & (df["crime_type"].isin(crime_types))]
    latest = c[c["year"] == 2022]["rate_per_100k"].mean()
    prev   = c[c["year"] == 2020]["rate_per_100k"].mean()
    change = (latest - prev) / prev * 100 if prev else 0
    snap   = get_latest_snapshot(crime_types)
    pctile = (snap["avg_rate"] < latest).mean() * 100
    label, color = safety_index(latest)
    gdp, unemp, urban, gini, police = SOCIO.get(country, (20000, 8, 65, 40, 150))
    return {
        "latest_rate": latest, "pct_change": change,
        "percentile": pctile, "label": label, "color": color,
        "gdp": gdp, "unemployment": unemp, "urbanisation": urban,
        "gini": gini, "police_density": police,
    }
