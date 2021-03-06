import datetime

import numpy as np
import pandas as pd
import requests
import streamlit as st


@st.cache
def fetch_j_league_schedule(year: int = 1992) -> pd.DataFrame:
    """Load J League schedule dataset."""
    url = "https://data.j-league.or.jp/SFMS01/search"
    params = {"competition_years": year, "lang": "en"}
    response = requests.get(url, params=params)

    attrs = {"class": "table-base00 search-table"}
    na_values = {"Date": ["To be decided"], "Score": ["vs", "Postponed"]}

    (df,) = pd.read_html(response.content, attrs=attrs, na_values=na_values)

    # Preprocess data
    df["Date"] = df["Date"].str.extract("(\d+\s\w+)", expand=False)
    df["Date"] = df["Date"] + " " + df["Year"].astype(str) + " " + df["Kick-off"]
    df["Date"] = pd.to_datetime(df["Date"])

    df.insert(0, "Datetime", df["Date"])
    df.drop(columns=["Year", "Date", "Kick-off"], inplace=True)

    return df


now = datetime.datetime.now()
year_start = 1992
year_end = now.year
years = np.arange(year_start, year_end + 1)

year = st.sidebar.selectbox("Which year's game results would you like to see?", years)
df = fetch_j_league_schedule(year=year)

st.title("J League Application")

st.write("The total number of attendees varies as follows.")

grouped = df.groupby(["Tournaments", pd.Grouper(key="Datetime", freq="D")])
res = grouped["Att."].sum()
res = res.unstack(fill_value=0, level="Tournaments")

# Avoid a ValueError raised by altair
columns = list(res.columns)
res.columns = columns

columns = st.multiselect("Choose tournaments to display.", columns, default=columns)

if columns:
    res = res[columns]

res.sort_index(inplace=True)

res = res.cumsum()

st.line_chart(res)

st.write("The result of each game are as follows.")

expr = st.text_input("Insert a query string to evaluate.", 'Home == "Kashima"')

if expr:
    df = df.query(expr)

st.write(df.style.background_gradient(cmap="Blues", subset=["Att."]))
