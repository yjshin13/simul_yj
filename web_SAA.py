import streamlit as st
import pandas as pd
import resampled_mvo
from datetime import datetime
import backtest_graph
import seaborn as sns
import matplotlib.pyplot as plt
import bt
import numpy as np

st.set_page_config(layout="wide")

file = st.file_uploader("Upload investment universe & price data", type=['xlsx', 'xls', 'csv'])

if file is not None:


    price = pd.read_excel(file, sheet_name="price",
                           names=None, dtype={'Date': datetime}, index_col=0, header=0).dropna()

    universe = pd.read_excel(file, sheet_name="universe",
                             names=None, dtype={'Date': datetime}, header=0)

    universe['key'] = universe['symbol'] + " - " + universe['name']

    select = st.multiselect('Input Assets', universe['key'], universe['key'])
    assets = universe['symbol'][universe['key'].isin(select)]

    input_price = price[list(assets)]
    input_universe = universe[universe['symbol'].isin(list(assets))].drop(['key'], axis=1)
    input_universe = input_universe.reset_index(drop=True) #index 깨지면 Optimization 배열 범위 초과 오류 발생

    with st.form("Resampling Parameters", clear_on_submit=False):

        st.subheader("Resampling Parameters:")

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            Growth_range = st.slider('Equity Weight Constraint', 0, 100, (0, 30), 1)
            nPort = st.number_input('Efficient Frontier Points', value=200)

        with col2:
            Inflation_range = st.slider('Inflation Weight Constraint', 0, 100, (0, 10), 1)
            nSim = st.number_input('Number of Simulations', value=200)

        with col3:
            Fixed_Income_range = st.slider('Fixed_Income Weight Constraint', 0, 100, (60, 100), 1)
            Target = st.number_input('Select Target Return(%)', value=4.00)

            constraint_range = [Growth_range,Inflation_range,Fixed_Income_range]

        summit = st.form_submit_button("Summit")

        if summit and ('EF' not in st.session_state):

            st.session_state.input_price = input_price
            st.session_state.input_universe = input_universe
            st.session_state.nPort = nPort
            st.session_state.nSim = nSim
            st.session_state.constraint_range = constraint_range

            st.session_state.EF = resampled_mvo.simulation(st.session_state.input_price,
                                                           st.session_state.nSim, st.session_state.nPort,
                                                           st.session_state.input_universe,
                                                           st.session_state.constraint_range)
            A = st.session_state.input_universe.copy()
            A.index = st.session_state.input_universe['symbol']
            Result = pd.concat([A.drop(['symbol'], axis=1).T, st.session_state.EF.applymap('{:.6%}'.format)], axis=0, join='outer')
            new_col = Result.columns[-2:].to_list() + Result.columns[:-2].to_list()
            st.session_state.Result = Result[new_col]

        if summit and ([st.session_state.nPort, st.session_state.nSim,
                       st.session_state.constraint_range, list(st.session_state.input_price.columns)] \
                       != [nPort, nSim, constraint_range, list(input_price.columns)]):

            st.session_state.input_price = input_price
            st.session_state.input_universe = input_universe
            st.session_state.nPort = nPort
            st.session_state.nSim = nSim
            st.session_state.constraint_range = constraint_range

            st.session_state.EF = resampled_mvo.simulation(st.session_state.input_price,
                                                           st.session_state.nSim, st.session_state.nPort,
                                                           st.session_state.input_universe,
                                                           st.session_state.constraint_range)
            A = st.session_state.input_universe.copy()
            A.index = st.session_state.input_universe['symbol']
            Result = pd.concat([A.drop(['symbol'], axis=1).T, st.session_state.EF.applymap('{:.6%}'.format)], axis=0, join='outer')
            new_col = Result.columns[-2:].to_list() + Result.columns[:-2].to_list()
            st.session_state.Result = Result[new_col]


    if 'EF' in st.session_state:

        with st.expander("Target Return " + str(Target) + "%", expanded=True) :

            Target_Weight = st.session_state.EF.loc[(st.session_state.EF['EXP_RET'] - Target / 100).abs().idxmin()]\
                            .drop(["EXP_RET", "STDEV"])

            Target_Weight_T = pd.DataFrame(Target_Weight).T

            st.session_state.Rebalancing_Wegiht =  pd.DataFrame(Target_Weight_T,
                                    index=pd.date_range(start=st.session_state.input_price.index[0],
                                    end=st.session_state.input_price.index[-1], freq='D')).fillna(method='bfill')

            st.session_state.Rebalancing_Wegiht.iloc[:,:] = Target_Weight_T

            if  st.session_state.Rebalancing_Wegiht.columns == st.session_state.input_price.columns:

                SAA_strategy = bt.Strategy('s1', [bt.algos.RunMonthly(run_on_first_date=True),
                                                  # bt.algos.RunAfterDate('2000-01-01'),
                                                  bt.algos.SelectAll(),
                                                  bt.algos.WeighTarget( st.session_state.Rebalancing_Wegiht),
                                                  bt.algos.Rebalance()])

                bt_SAA = bt.Backtest(SAA_strategy, st.session_state.input_price)
                res = bt.run(bt_SAA)

            st.empty()

            st.write("Backtest")

            start_date = st.session_state.input_price.index[0].strftime("%Y-%m-%d")
            end_date = st.session_state.input_price.index[-1].strftime("%Y-%m-%d")
            Anuuual_RET = round(float(((res.prices.iloc[-1] / 100) ** (365 / (len(res.prices) - 1)) - 1) * 100), 2)
            Anuuual_Vol = round(float(np.std(res.prices.pct_change().dropna())*np.sqrt(365)*100),2)
            Anuuual_Sharpe = round(Anuuual_RET/Anuuual_Vol,2)
            MDD = round(float(res.stats[res.stats.index == 'max_drawdown'].values * 100), 2)

            col10, col11, col12, col13 = st.columns([1, 1, 1, 1])

            with col10:
                st.info("Period: " + str(start_date) + " ~ " + str(end_date))

            with col11:
                st.info("Annual Return: "+str(Anuuual_RET)+"%")

            with col12:
                st.info("Max Drawdown: "+str(MDD) + "%")


            col6, col7, col8, col9 = st.columns([1, 1, 1, 1])


            with col6:
                st.info("Sharpe: " + str(Anuuual_Sharpe))

            with col7:
                st.info("Annual vol: " + str(Anuuual_Vol)+"%")


            col4, col5 = st.columns([1, 1])

            with col4:
                st.write("Net Asset Value")
                st.pyplot(backtest_graph.line_chart(res.prices, ""))
            with col5:
                st.write("Drawdown")
                st.pyplot(backtest_graph.line_chart(
                res.backtests['s1'].stats.drawdown, ""))

        st.download_button(
                label="Efficient Frontier",
                data=st.session_state.Result.to_csv(index=False),
                mime='text/csv',
                file_name='Efficient Frontier.csv')
