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

    price = pd.read_excel(file, sheet_name="sheet1",
                           names=None, dtype={'Date': datetime}, index_col=0, header=0)

    price_list = list(map(str, price.columns))
    select = st.multiselect('Input Assets', price_list, price_list)
    input_list = price.columns[price.columns.isin(select)]
    input_price = price[input_list]

    if st.button('Summit') or ('input_list' in st.session_state):
        st.session_state.input_list = input_list
        st.session_state.input_price = input_price.dropna()

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

        slider = pd.Series()
        #
        # st.write(input_price.columns)

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        for i, k in enumerate(st.session_state.input_list, start=0):

            if i % 4 == 1:
                with col1:
                    slider[k] = st.slider(str(k), 0, 100, 0,1)

            if i % 4 == 2:
                with col2:
                    slider[k] = st.slider(str(k), 0, 100, 0,1)

            if i % 4 == 3:
                with col3:
                    slider[k] = st.slider(str(k), 0, 100, 0,1)

            if i % 4 == 0:
                with col4:
                    slider[k] = st.slider(str(k), 0, 100, 0,1)

        st.write(str("Total Weight:   ")+str(slider.sum())+str("%"))



            #########################[Graph Insert]#####################################

        if st.button('Sumulation') or ('slider' in st.session_state):
            col11, col22 = st.columns([3, 7])

            with col11:
                
                st.write("Portfolio NAV")
                st.dataframe(st.session_state.portfolio_port)

            with col22:

                
                st.write("Input Assets")
                st.dataframe(st.session_state.input_price)




                # st.write("Correlation Heatmap")
                #
                # # Increase the size of the heatmap.
                # fig = plt.figure(figsize=(10, 8))
                # # plt.rc('font', family='Malgun Gothic')
                # plt.rcParams['axes.unicode_minus'] = False
                #
                # st.session_state.corr = st.session_state.input_price.pct_change().dropna().corr().round(2)
                # st.session_state.corr.index = pd.Index(st.session_state.corr.index.map(lambda x: str(x)[:7]))
                # st.session_state.corr.columns = st.session_state.corr.index
                # # st.session_state.corr.columns = pd.MultiIndex.from_tuples([tuple(map(lambda x: str(x)[:7], col)) for col in st.session_state.corr.columns])
                #
                # heatmap = sns.heatmap(st.session_state.corr, vmin=-1, vmax=1, annot=True,
                #                       cmap='BrBG')
                # # heatmap.set_title('Correlation Heatmap', fontdict={'fontsize': 20}, pad=12)
                #
                # st.pyplot(fig)

            st.session_state.slider = (slider*0.01).tolist()
            st.session_state.portfolio_port = backtest.simulation(st.session_state.input_price, st.session_state.slider)

            col33, col44,col55 = st.columns([1,4,4])

            with col33:

                st.pyplot(backtest_graph2.line_chart(st.session_state.portfolio_port, ""))


            #
            # with col44:


