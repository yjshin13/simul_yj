import streamlit as st
import pandas as pd
import resampled_mvo
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

file = st.file_uploader("Upload investment universe & price data", type=['xlsx', 'xls', 'csv'])

if file is not None:

    EF = pd.DataFrame()
    price = pd.read_excel(file, sheet_name="price",
                           names=None, dtype={'Date': datetime}, index_col=0, header=0).dropna()

    universe = pd.read_excel(file, sheet_name="universe",
                             names=None, dtype={'Date': datetime}, header=0)

    universe['key'] = universe['symbol'] + " - " + universe['name']

    select = st.multiselect('Input Assets', universe['key'], universe['key'])
    assets = universe['symbol'][universe['key'].isin(list(select))]

    input_price = price[list(assets)]
    input_universe = universe[universe['symbol'].isin(list(assets))]


   # my_expander = st.expander("", expanded=True)

    with st.form("Resampling Parameters", clear_on_submit=False):

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

            st.write(Fixed_Income[1])

        summit = st.form_submit_button("Summit")

        if summit:

            EF = resampled_mvo.simulation(input_price, nSim, nPort, input_universe)
            EF = EF.applymap('{:.6%}'.format)

            # fig, ax = plt.subplots()
            # sns.heatmap(price.pct_change().dropna().corr(), ax=ax)
            # st.write(fig)

    if EF.empty==False:

        st.download_button(
                label="Efficient Frontier",
                data=EF.to_csv(),
                mime='text/csv',
                file_name='Efficient Frontier.csv')

