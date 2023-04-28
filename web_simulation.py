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
        df = pd.read_excel(file_path, sheet_name="data",
                           names=None, dtype={'Date': datetime}, index_col=0, header=2)

        df2 = pd.read_excel(file_path, sheet_name="data",
                           names=None, index_col=0, header=0, nrows=1)

        return df, df2


    price, weight = load_data(file)

    price_list = list(map(str, price.columns))
    select = st.multiselect('Input Assets', price_list, price_list)
    input_list = price.columns[price.columns.isin(select)]
    input_price = price[input_list]

    if (st.button('Summit') or ('input_list' in st.session_state)):

        st.session_state.summit = 1

        with st.expander('Portfolio', expanded=True):

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
                        slider[k] = st.slider(str(k), 0.0, 100.0,  round(float(weight[k]*100),1), 0.1)

                if i % 4 == 2:
                    with col2:
                        slider[k] = st.slider(str(k), 0.0, 100.0,  round(float(weight[k]*100),1), 0.1)

                if i % 4 == 3:
                    with col3:
                        slider[k] = st.slider(str(k), 0.0, 100.0,  round(float(weight[k]*100),1), 0.1)

                if i % 4 == 0:
                    with col4:
                        slider[k] = st.slider(str(k), 0.0, 100.0, round(float(weight[k]*100),1), 0.1)

            st.write(str("Total Weight:   ") + str((slider.sum().round(2))) + str("%"))

            #########################[Graph Insert]#####################################

            if st.button('Simulation'):


                st.session_state.slider = (slider*0.01).tolist()
                st.session_state.portfolio_port, st.session_state.allocation,\
                    st.session_state.alloc_amount= backtest.simulation(st.session_state.input_price,st.session_state.slider,
                                                                                                   commission,
                                                                                                   rebal)
                st.write(st.session_state.allocation)
                                                                                                    

                st.session_state.contribution = (-1)*(st.session_state.alloc_amount[st.session_state.alloc_amount.index.is_month_end==True].shift(1).dropna()\
                                                /st.session_state.alloc_amount[st.session_state.alloc_amount.index.is_month_end==True].iloc[:-1]-1).sum(axis=0)



                if monthly == True:
                    st.session_state.portfolio_port = st.session_state.portfolio_port[st.session_state.portfolio_port.index.is_month_end==True]

                st.session_state.portfolio_port.index = st.session_state.portfolio_port.index.date
                st.session_state.drawdown = backtest.drawdown(st.session_state.portfolio_port)
                st.session_state.input_price.index = st.session_state.input_price.index.date
                st.session_state.allocation.index = st.session_state.allocation.index.date
                st.session_state.result = pd.concat([st.session_state.portfolio_port,
                                                     st.session_state.drawdown,
                                                     st.session_state.input_price,
                                                     st.session_state.allocation],
                                                    axis=1)





            if 'slider' in st.session_state:

                START_DATE = st.session_state.portfolio_port.index[0].strftime("%Y-%m-%d")
                END_DATE = st.session_state.portfolio_port.index[-1].strftime("%Y-%m-%d")
                Anuuual_RET = round(float(((st.session_state.portfolio_port[-1] / 100) ** (annualization / (len(st.session_state.portfolio_port) - 1)) - 1) * 100), 2)
                Anuuual_Vol = round(float(np.std(st.session_state.portfolio_port.pct_change().dropna())*np.sqrt(annualization)*100),2)
                Anuuual_Sharpe = round(Anuuual_RET/Anuuual_Vol,2)
                MDD  =round(float(min(st.session_state.drawdown) * 100), 2)
                Daily_RET = st.session_state.portfolio_port.pct_change().dropna()


                col21, col22, col23, col24 = st.columns([0.8, 0.8, 3.5, 3.5])

                with col21:
                    st.write('NAV')
                    st.dataframe(st.session_state.portfolio_port.round(2))

                    st.download_button(
                        label="NAV         ",
                        data=st.session_state.portfolio_port.to_csv(index=True),
                        mime='text/csv',
                        file_name='Net Asset Value.csv')

                with col22:
                    st.write('MDD')
                    st.dataframe(st.session_state.drawdown.apply(lambda x: '{:.2%}'.format(x)))

                    st.download_button(
                        label="MDD",
                        data=st.session_state.drawdown.apply(lambda x: '{:.2%}'.format(x)).to_csv(index=True),
                        mime='text/csv',
                        file_name='MAX Drawdown.csv')

                with col23:
                    st.write('Assets')
                    st.dataframe((100*st.session_state.input_price/st.session_state.input_price.iloc[0,:]).
                                  astype('float64').round(2))

                    st.download_button(
                        label="Assets",
                        data=(100*st.session_state.input_price/st.session_state.input_price.iloc[0,:]).
                                  astype('float64').round(2).to_csv(index=True),
                        mime='text/csv',
                        file_name='Assets.csv')

                with col24:
                    st.write('Allocation(floating)')
                    st.dataframe((st.session_state.allocation*0.01))

                    st.download_button(
                        label="Allocation",
                        data=st.session_state.allocation.applymap('{:.2%}'.format).to_csv(index=True),
                        mime='text/csv',
                        file_name='Allocation.csv')


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

                    st.info("MDD: " + str(MDD) + "%")


                col31, col32 = st.columns([1, 1])

                with col31:
                    st.write("Net Asset Value")
                    st.pyplot(backtest_graph2.line_chart(st.session_state.portfolio_port, ""))

                with col32:
                    st.write("MAX Drawdown")
                    st.pyplot(backtest_graph2.line_chart(st.session_state.drawdown, ""))

                col_a, col_b, = st.columns([1,1])


                with col_a:

                    st.write("Contribution")
                    st.write((st.session_state.contribution).sum())



                    x = (st.session_state.contribution * 100)
                    y = st.session_state.contribution.index

                    fig_bar, ax_bar = plt.subplots(figsize=(18, 10.8))
                    width = 0.75  # the width of the bars
                    bar = ax_bar.barh(y, x, color="lightblue", height=0.8, )

                    for bars in bar:
                        width = bars.get_width()
                        posx = width + 0.01
                        posy = bars.get_y() + bars.get_height() * 0.5
                        ax_bar.text(posx, posy, '%.1f' % width, rotation=0, ha='left', va='center', fontsize=13)

                    plt.xticks(fontsize=15)
                    plt.yticks(fontsize=15)
                    plt.xlabel('Contribution(%)', fontsize=15, labelpad=20)
                    plt.ylabel('Assets', fontsize=15, labelpad=15)
                    #ax_bar.margins(x=0, y=0)

                    st.pyplot(fig_bar)

                    # st.write("Return Distribution")
                    #
                    # # plt.hist(Daily_RET, bins=100, label="Daily Return", color="salmon", rwidth=1, density=True)
                    # # plt.legend()
                    # # plt.xticks(np.arange(-0.1, 0.11,0.01), ['{:.1%}'.format(x) for x in np.arange(-0.1, 0.11,0.01)])
                    # # plt.margins(x=-0.1, y=0)
                    # #
                    #
                    # fig1 = plt.figure(figsize=(15, 8.8))
                    # sns.histplot(data=Daily_RET, bins=50, color="blue", legend=None, stat="probability", alpha=0.5, kde=True)
                    #
                    #
                    # plt.xlim([Daily_RET.min(), Daily_RET.max()])
                    # plt.ylim([0, 0.5])
                    # plt.xlabel("Daily Return", size=12)
                    # plt.ylabel("Probability", size=12)
                    # plt.xticks(np.arange(Daily_RET.min().round(2), Daily_RET.max().round(2), (Daily_RET.max().round(2)-Daily_RET.min().round(2))/10), fontsize=12)
                    # plt.grid(True, alpha=1, linestyle="--")
                    # plt.rcParams["figure.figsize"] = [7, 5]
                    # #plt.rcParams["figure.dpi"] = 500
                    #
                    #
                    # st.pyplot(fig1)



                with col_b:
                    st.write("Correlation Matrix")

                    # Increase the size of the heatmap.
                    fig2 = plt.figure(figsize=(15, 8))
                    # plt.rc('font', family='Malgun Gothic')
                    plt.rcParams['axes.unicode_minus'] = False

                    st.session_state.corr = st.session_state.input_price.pct_change().dropna().corr().round(2)
                    st.session_state.corr.index = pd.Index(st.session_state.corr.index.map(lambda x: str(x)[:7]))
                    st.session_state.corr.columns = st.session_state.corr.index
                    # st.session_state.corr.columns = pd.MultiIndex.from_tuples([tuple(map(lambda x: str(x)[:7], col)) for col in st.session_state.corr.columns])

                    heatmap = sns.heatmap(st.session_state.corr, vmin=-1, vmax=1, annot=True, cmap='BrBG')

                    # heatmap.set_title('Correlation Heatmap', fontdict={'fontsize': 20}, pad=12)

                    st.pyplot(fig2)



        # if 'result' in st.session_state:
        #
        #     st.download_button(
        #             label="Net Asset Value",
        #             data=st.session_state.result.to_csv(index=True),
        #             mime='text/csv',
        #             file_name='Net Asset Value.csv')
        #
        #     st.download_button(
        #             label="Correlation Matrix",
        #             data=st.session_state.input_price.pct_change().dropna().corr().round(2).to_csv(index=True),
        #             mime='text/csv',
        #             file_name='Correlation Matrix.csv')
