import backtest
import streamlit as st
from datetime import datetime
import backtest_graph2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
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

        col40, col41, col42, col43, col44, col45, col46, col47 = st.columns([1, 1, 1, 1, 1, 1, 1, 1])

        with col40:

            start_date = st.date_input("Start", value=input_price.index[0])
            start_date = datetime.combine(start_date, datetime.min.time())

        with col41:

            end_date = st.date_input("End", value=input_price.index[-1])
            end_date = datetime.combine(end_date, datetime.min.time())

        with col42:

            option1 = st.selectbox(
                'Data Frequency', ('Daily', 'Monthly'))

        with col43:

            rebal = st.selectbox('Rebalancing', ( 'Monthly', 'Daily', 'Quarterly', 'Yearly'))

        with col44:

            commission = st.number_input('Commission(%)')

        if option1 == 'Daily':
            daily = True
            monthly = False
            annualization = 365
            freq = 1

        if option1 == 'Monthly':
            daily = False
            monthly = True
            annualization = 12
            freq = 2

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
            st.session_state.portfolio_port, st.session_state.allocation = backtest.simulation(st.session_state.input_price,
                                                                                               st.session_state.slider,
                                                                                               commission,
                                                                                               rebal)

            if monthly == True:
                st.session_state.portfolio_port = st.session_state.portfolio_port[st.session_state.portfolio_port.index.is_month_end==True]

            st.session_state.portfolio_port.index = st.session_state.portfolio_port.index.date
            st.session_state.drawdown = backtest.drawdown(st.session_state.portfolio_port)
            st.session_state.input_price.index = st.session_state.input_price.index.date
            st.session_state.allocation.index = st.session_state.allocation.index.date

        if 'slider' in st.session_state:


            START_DATE = st.session_state.portfolio_port.index[0].strftime("%Y-%m-%d")
            END_DATE = st.session_state.portfolio_port.index[-1].strftime("%Y-%m-%d")
            Anuuual_RET = round(float(((st.session_state.portfolio_port[-1] / 100) ** (annualization / (len(st.session_state.portfolio_port) - 1)) - 1) * 100), 2)
            Anuuual_Vol = round(float(np.std(st.session_state.portfolio_port.pct_change().dropna())*np.sqrt(annualization)*100),2)
            Anuuual_Sharpe = round(Anuuual_RET/Anuuual_Vol,2)
            MDD  =round(float(min(st.session_state.drawdown) * 100), 2)

            col50, col51, col52, col53, col54 = st.columns([1, 1, 1, 1, 1])


            with col50:
                st.info("Period: " + str(START_DATE) + " ~ " + str(END_DATE))

            with col51:
                st.info("Annual Return: "+str(Anuuual_RET)+"%")

            with col52:
                st.info("Annual Volatility: " + str(Anuuual_Vol) +"%")

            with col53:
                
                st.info("Annual Sharpe: " + str(Anuuual_Sharpe))
            with col54:
                
                st.info("Maximum Drawdown: " + str(MDD) + "%")





            col21, col22, col23, col24 = st.columns([0.8, 0.8, 3.5, 3.5])

            with col21:
                st.write('NAV')
                st.dataframe(st.session_state.portfolio_port)

            with col22:
                st.write('MDD')
                st.dataframe(st.session_state.drawdown)

            with col23:
                st.write('Assets')
                st.dataframe(st.session_state.input_price)

            with col24:
                st.write('Allocation')
                st.dataframe(st.session_state.allocation)

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
