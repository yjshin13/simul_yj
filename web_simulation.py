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
    price_list = list(map(str, price.columns))
    select = st.multiselect('Input Assets', price_list, price_list)
    input_list = price.columns[price.columns.isin(select)]
    input_price = price[input_list]

    if st.button('적용'):
    #
    # with st.form("Input Assets", clear_on_submit=False):
    #
    #     st.subheader("Input Assets:")
    #     col20, col21, col22, col23 = st.columns([1, 1, 1, 3])
    #
    #     with col20:
    #
    #         start_date = st.date_input("Start", value=price.index[0])
    #         start_date = datetime.combine(start_date, datetime.min.time())
    #
    #     with col21:
    #
    #         end_date = st.date_input("End", value=price.index[-1])
    #         end_date = datetime.combine(end_date, datetime.min.time())
    #
    #     with col22:
    #
    #         # st.write("Data Frequency")
    #
    #         if st.checkbox('Daily', value=True):
    #             daily = True
    #             monthly = False
    #             annualization = 252
    #             freq = "daily"
    #
    #         if st.checkbox('Monthly', value=False):
    #             daily = False
    #             monthly = True
    #             annualization = 12
    #             freq = "monthly"
    #
    #     col1, col2, col3 = st.columns([1, 1, 1])

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        for i, k in enumerate(input_price.columns):

            if i % 4 == 1:
                with col1:
                    st.session_state.slider = st.slider(str(k), 0, 100)

            if i % 4 == 2:
                with col2:
                    st.session_state.slider = st.slider(str(k), 0, 100)

            if i % 4 == 3:
                with col3:
                    st.session_state.slider = st.slider(str(k), 0, 100)

            if i % 4 == 0:
                with col4:
                    st.session_state.slider = st.slider(str(k), 0, 100)


