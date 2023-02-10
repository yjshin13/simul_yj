import streamlit as st
import pandas as pd
import resampled_mvo
from datetime import datetime

st.set_page_config(layout="wide")
file = st.file_uploader("Upload investment universe & price data", type=['xlsx', 'xls', 'csv'])

if file is not None:

    assets = pd.read_excel(file, sheet_name="Daily_price",
                           names=None, dtype={'Date': datetime}, index_col=0, header=0).dropna()

    tickers = st.multiselect('', assets.columns, list(assets.columns))

    port_num = st.number_input('Efficient Frontier Points')
    nSim = st.number_input('Number of Simulations')
    Target = st.number_input('Select Target Return(%)')
    Growth = st.slider('Growth', 0, 100, 30, 5)
    Inflation = st.slider('Inflation', 0, 100, 30, 5)
    Fixed_Income = st.slider('Fixed_Income', 0, 100, 30, 5)
