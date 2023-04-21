import backtest
import streamlit as st
from datetime import datetime
import backtest_graph2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
file = st.file_uploader("Upload investment universe & price data", type=['xlsx', 'xls', 'csv'])
st.warning('Upload data.')

if file is not None:

    @st.cache
    def load_data(file_path):
        df = pd.read_excel(file_path, sheet_name="sheet1",
                           names=None, dtype={'Date': datetime}, index_col=0, header=0)
        return df


    price = load_data(file)

    price_list = list(map(str, price.columns))
    select = st.multiselect('Input Assets', price_list, price_list)
    input_list = price.columns[price.columns.isin(select)]
    input_price = price[input_list]

    if st.button('Summit') or ('input_list' in st.session_state):

        input_price = input_price.dropna()

        col40, col41, col42, col43, col44, col45 = st.columns([1, 1, 1, 1, 1, 3])

        with col40:

            start_date = st.date_input("Start", value=input_price.index[0])
            start_date = datetime.combine(start_date, datetime.min.time())

        with col41:

            end_date = st.date_input("End", value=input_price.index[-1])
            end_date = datetime.combine(end_date, datetime.min.time())

        with col42:

            # st.write("Data Frequency")

            if st.checkbox('Daily Input', value=True):
                daily = True
                monthly = False
                annualization = 252
                freq = 1

            if st.checkbox('Monthly Input', value=False):
                daily = False
                monthly = True
                annualization = 12
                freq = 2

        with col43:

            # st.write("Data Frequency")

            if st.checkbox('Daily Rebalancing', value=False):
                rebal = 1

            if st.checkbox('Monthly Rebalancing', value=True):
                rebal = 2



        with col44:

            if st.checkbox('Quarterly Quarterly', value=False):
                rebal = 3

            if st.checkbox('Yearly Quarterly', value=False):
                rebal = 4

        st.session_state.input_list = input_list

        if daily == True:
            st.session_state.input_price = input_price[
                (input_price.index >= start_date) & (input_price.index <= end_date)]

        if monthly == True:
            st.session_state.input_price = input_price[(input_price.index >= start_date)
                                                       & (input_price.index <= end_date)
                                                       & (input_price.index.is_month_end == True)].dropna()

        col1, col2, col3 = st.columns([1, 1, 1])

        slider = pd.Series()
        #
        # st.write(input_price.columns)

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        for i, k in enumerate(st.session_state.input_list, start=0):

            if i % 4 == 1:
                with col1:
                    slider[k] = st.slider(str(k), 0, 100, 0, 1)

            if i % 4 == 2:
                with col2:
                    slider[k] = st.slider(str(k), 0, 100, 0, 1)

            if i % 4 == 3:
                with col3:
                    slider[k] = st.slider(str(k), 0, 100, 0, 1)

            if i % 4 == 0:
                with col4:
                    slider[k] = st.slider(str(k), 0, 100, 0, 1)

        st.write(str("Total Weight:   ") + str(slider.sum()) + str("%"))

        #########################[Graph Insert]#####################################

        if st.button('Simulation'):
            st.session_state.slider = (slider * 0.01).tolist()
            st.session_state.portfolio_port = backtest.simulation(st.session_state.input_price, st.session_state.slider,0,rebal)

            if monthly == True:
                st.session_state.portfolio_port = st.session_state.portfolio_port[st.session_state.portfolio_port.index.is_month_end==True]

            st.session_state.portfolio_port.index = st.session_state.portfolio_port.index.date
            st.session_state.drawdown = backtest.drawdown(st.session_state.portfolio_port)

        if 'slider' in st.session_state:
            col21, col22, col23 = st.columns([0.8, 0.8, 7])

            with col21:
                st.dataframe(st.session_state.portfolio_port)

            with col22:
                st.dataframe(st.session_state.drawdown)

            with col23:
                st.dataframe(st.session_state.input_price)

            col31, col32 = st.columns([1, 1])

            with col31:
                st.write("Portfolio NAV")
                st.pyplot(backtest_graph2.line_chart(st.session_state.portfolio_port, ""))

            with col32:
                st.write("Portfolio MDD")
                st.pyplot(backtest_graph2.line_chart(st.session_state.drawdown, ""))

            col31, col32, col33 = st.columns([2, 3, 5])

            with col33:
                st.write("Correlation Heatmap")

                # Increase the size of the heatmap.
                fig = plt.figure(figsize=(15, 8))
                # plt.rc('font', family='Malgun Gothic')
                plt.rcParams['axes.unicode_minus'] = False

                st.session_state.corr = st.session_state.input_price.pct_change().dropna().corr().round(2)
                st.session_state.corr.index = pd.Index(st.session_state.corr.index.map(lambda x: str(x)[:7]))
                st.session_state.corr.columns = st.session_state.corr.index
                # st.session_state.corr.columns = pd.MultiIndex.from_tuples([tuple(map(lambda x: str(x)[:7], col)) for col in st.session_state.corr.columns])

                heatmap = sns.heatmap(st.session_state.corr, vmin=-1, vmax=1, annot=True, cmap='BrBG')

                # heatmap.set_title('Correlation Heatmap', fontdict={'fontsize': 20}, pad=12)

                st.pyplot(fig)
