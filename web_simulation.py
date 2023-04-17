import backtest
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(layout="wide")
file = st.file_uploader("Upload investment universe & price data", type=['xlsx', 'xls', 'csv'])
st.warning('Upload data.')


if file is not None:

    price = pd.read_excel(file, sheet_name="sheet1",
                           names=None, dtype={'Date': datetime}, index_col=0, header=0).dropna()
    select = st.multiselect('Input Assets', price.columns, str(price.columns))
    assets = price[price.isin(select)]

    with st.form("Input Assets", clear_on_submit=False):

        st.subheader("Input Assets:")

        summit = st.form_submit_button("Summit")
