import streamlit as st
import pandas as pd
import resampled_mvo
from datetime import datetime
import io

st.set_page_config(layout="wide")
st.warning('혜린이 안녕 아이러븅')

file = st.file_uploader("Upload investment universe & price data", type=['xlsx', 'xls', 'csv'])

if file is not None:

    assets = pd.read_excel(file, sheet_name="Daily_price",
                           names=None, dtype={'Date': datetime}, index_col=0, header=0).dropna()

    tickers = st.multiselect('Input Assets', assets.columns, list(assets.columns))


   # my_expander = st.expander("", expanded=True)

    with st.form("Resampling Parameters", clear_on_submit=True):

        st.subheader("Resampling Parameters:")

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            Growth = st.slider('Equity', 0, 100, (0, 30), 1)
            nPort = st.number_input('Efficient Frontier Points', value=200)

        with col2:
            Inflation = st.slider('Inflation', 0, 100, (0, 10), 1)
            nSim = st.number_input('Number of Simulations', value=200)

        with col3:
            Fixed_Income = st.slider('Fixed_Income', 0, 100, (60, 100), 1)
            Target = st.number_input('Select Target Return(%)', value=4.00)

        # if st.button("Summit"):
        #     st.text("혜린아 오늘 뭐하구놀까")

        submit = st.form_submit_button("Summit", on_click=True)

        if submit is not None:

            EF = resampled_mvo.simulation(assets, nSim, nPort)
