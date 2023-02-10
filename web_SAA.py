import streamlit as st
import pandas as pd
import resampled_mvo
from datetime import datetime

file = st.file_uploader("Upload investment universe & price data", type=['xlsx', 'xls', 'csv'])

if file is not None:

    assets = pd.read_excel(file, sheet_name="Daily_price",
                           names=None, dtype={'Date': datetime}, index_col=0, header=0).dropna()

    tickers = st.multiselect('select', assets.keys(), assets.keys())

    number1 = st.number_input('Efficient Frontier Points')
    st.write(number1)

    number2 = st.number_input('Number of Simulations')
    st.write(number2)

    number3 = st.number_input('Select Target Return(%)')
    st.write(number3)

