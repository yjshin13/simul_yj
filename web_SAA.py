import streamlit as st
import pandas as pd
import resampled_mvo
from datetime import datetime
import backtest_graph
import seaborn as sns
import matplotlib.pyplot as plt
import bt

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
    input_universe = universe[universe['symbol'].isin(list(assets))].drop(['key'], axis=1)


   # my_expander = st.expander("", expanded=True)

    with st.form("Resampling Parameters", clear_on_submit=False):

        st.subheader("Resampling Parameters:")

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            Growth_range = st.slider('Equity', 0, 100, (0, 30), 1)
            st.session_state.nPort = st.number_input('Efficient Frontier Points', value=200)

        with col2:
            Inflation_range = st.slider('Inflation', 0, 100, (0, 10), 1)
            st.session_state.nSim = st.number_input('Number of Simulations', value=200)

        with col3:
            Fixed_Income_range = st.slider('Fixed_Income', 0, 100, (60, 100), 1)
            st.session_state.Target = st.number_input('Select Target Return(%)', value=4.00)

            constraint_range=[Growth_range,Inflation_range,Fixed_Income_range]

        st.session_state.summit = st.form_submit_button("Summit")

        if st.session_state.summit:

            st.session_state.summit.EF = resampled_mvo.simulation(input_price, st.session_state.nSim, st.session_state.nPort, input_universe, constraint_range)
            A = input_universe.copy()
            A.index = input_universe['symbol']
            Result = pd.concat([A.drop(['symbol'], axis=1).T, st.session_state.summit.EF.applymap('{:.6%}'.format)], axis=0, join='outer')
            new_col = Result.columns[-2:].to_list() + Result.columns[:-2].to_list()
            Result = Result[new_col]

            # fig, ax = plt.subplots()
            # sns.heatmap(price.pct_change().dropna().corr(), ax=ax)
            # st.write(fig)

    if st.session_state.summit.EF.empty==False:

        with st.expander("Target Return " + str(st.session_state.Target) + "%") :

            Target_Weight = st.session_state.summit.EF.loc[(st.session_state.summit.EF['EXP_RET'] - st.session_state.Target / 100).abs().idxmin()]\
                            .drop(["EXP_RET", "STDEV"])

            Target_Weight_T = pd.DataFrame(Target_Weight).T

            Rebalancing_Wegiht =  pd.DataFrame(Target_Weight_T,
                                    index=pd.date_range(start=input_price.index[0],
                                    end=input_price.index[-1], freq='D')).fillna(method='bfill')

            Rebalancing_Wegiht.iloc[:,:] = Target_Weight_T

            SAA_strategy = bt.Strategy('s1', [bt.algos.RunMonthly(run_on_first_date=True),
                                              # bt.algos.RunAfterDate('2000-01-01'),
                                              bt.algos.SelectAll(),
                                              bt.algos.WeighTarget(Rebalancing_Wegiht),
                                              bt.algos.Rebalance()])

            bt_SAA = bt.Backtest(SAA_strategy, input_price)
            st.session_state.res = bt.run(bt_SAA)

            col4, col5 = st.columns([1, 1])

            with col4:
                st.write("Net Asset Value")
                st.pyplot(backtest_graph.line_chart(st.session_state.res.prices, ""))
            with col5:
                st.write("Drawdown")
                st.pyplot(backtest_graph.line_chart(
                st.session_state.res.backtests['s1'].stats.drawdown, ""))

        st.download_button(
                label="Efficient Frontier",
                data=Result.to_csv(index=False),
                mime='text/csv',
                file_name='Efficient Frontier.csv')



