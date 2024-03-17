import streamlit as st
import pandas as pd
import resampled_mvo
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import backtest
import seaborn as sns
import backtest_graph2
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(layout="wide")

file = st.file_uploader("Upload investment universe & price data", type=['xlsx', 'xls', 'csv'])
st.warning('Upload data.')

if file is not None:

    # price = pd.read_excel(file, sheet_name="price",
    #                    names=None, dtype={'Date': datetime}, index_col=0, header=0).dropna()
    price = pd.read_excel(file, sheet_name="price", parse_dates=["Date"], index_col=0, header=0).dropna()


    universe = pd.read_excel(file, sheet_name="universe",
                             names=None, dtype={'Date': datetime}, header=0)

    universe['key'] = universe['symbol'] + " - " + universe['name']

    select = st.multiselect('Input Assets', universe['key'], universe['key'])
    assets = universe['symbol'][universe['key'].isin(select)]

    input_price = price[list(assets)]
    input_simul_price = price[list(assets)]
    input_universe = universe[universe['symbol'].isin(list(assets))].drop(['key'], axis=1)
    input_universe = input_universe.reset_index(drop=True) #index 깨지면 Optimization 배열 범위 초과 오류 발생

    key = np.random.uniform(0.0, 2.0)


    with st.form("Resampling Parameters", clear_on_submit=False):

        st.subheader("Resampling Parameters:")

        col20, col21, col22, col23 = st.columns([1,1,1,3])

        with col20:

            start_date = st.date_input("Start", value = input_price.index[0])
            start_date = datetime.combine(start_date, datetime.min.time())

        with col21:

            end_date = st.date_input("End", value = input_price.index[-1])
            end_date = datetime.combine(end_date, datetime.min.time())

        with col22:


            if st.checkbox('Daily', value=False):

                daily = True
                monthly = False
                annualization = 252
                freq = "daily"

            if st.checkbox('Monthly', value=True):

                daily = False
                monthly = True
                annualization = 12
                freq = "monthly"


        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            Growth_range = st.slider('Equity Weight Constraint', 0, 100, (0, 40), 1)
            nPort = st.number_input('Efficient Frontier Points', value=200)

        with col2:
            Inflation_range = st.slider('Inflation Weight Constraint', 0, 100, (0, 30), 1)
            nSim = st.number_input('Number of Simulations', value=200)

        with col3:
            Fixed_Income_range = st.slider('Fixed_Income Weight Constraint', 0, 100, (50, 100), 1)
            Target = st.number_input('Select Target Return(%)', value=4.00)

            constraint_range = [Growth_range,Inflation_range,Fixed_Income_range]

        summit = st.form_submit_button("Summit")



        if summit and (('EF' not in st.session_state) or ([st.session_state.nPort, st.session_state.nSim,
                       st.session_state.constraint_range, list(st.session_state.input_price.columns)] \
                       != [nPort, nSim, constraint_range, list(input_price.columns)])):

            if daily==True:

                st.session_state.input_price = input_price[(input_price.index>=start_date) & (input_price.index<=end_date)]

            if monthly==True:

                st.session_state.input_price = input_price[(input_price.index>=start_date)
                                                           & (input_price.index<=end_date)
                                                           & (input_price.index.is_month_end==True)]

            st.session_state.input_universe = input_universe
            st.session_state.nPort = nPort
            st.session_state.nSim = nSim
            st.session_state.constraint_range = constraint_range



            st.session_state.EF = resampled_mvo.simulation(st.session_state.input_price,
                                                           st.session_state.nSim, st.session_state.nPort,
                                                           st.session_state.input_universe,
                                                           st.session_state.constraint_range,
                                                           annualization)

            st.session_state.key = key

            A = st.session_state.input_universe.copy()
            A.index = st.session_state.input_universe['symbol']
            Result = pd.concat([A.drop(['symbol'], axis=1).T, st.session_state.EF.applymap('{:.6%}'.format)], axis=0, join='outer')
            new_col = Result.columns[-2:].to_list() + Result.columns[:-2].to_list()
            st.session_state.Result = Result[new_col]
            st.session_state.freq_input = freq







    if 'EF' in st.session_state:

        if daily == True:
            st.session_state.input_price = input_price[(input_price.index>=start_date) & (input_price.index<=end_date)]

        if monthly == True:
            st.session_state.input_price = input_price[(input_price.index >= start_date)
                                                       & (input_price.index <= end_date)
                                                       & (input_price.index.is_month_end == True)]

        with st.expander("Optimization (Target: " + str(Target) + "%, " + st.session_state.freq_input + ")", expanded=True) :

            Target_index = (st.session_state.EF['EXP_RET'] - Target / 100).abs().idxmin()

            col_x, col_y, col_z = st.columns([1, 1, 2])

            with col_x:

                st.info("Expected Return: " + str(round(st.session_state.EF.loc[Target_index]["EXP_RET"]*100,2)) + "%")

            with col_y:

                st.info("Expected Risk: " + str(round(st.session_state.EF.loc[Target_index]["STDEV"]*100,2))+"%")

            st.write("")

            Target_Weight = st.session_state.EF.loc[Target_index]\
                            .drop(["EXP_RET", "STDEV"])


            st.subheader("")
            st.empty()


            col_a, col_b = st.columns([1, 1])

            with col_a:

                st.write("Efficient Frontier")
                # EF_point = plt.figure(figsize=(20, 10))
                #
                #
                # Point = np.full(len(st.session_state.EF),0)
                # Point[Target_index] =2
                #
                # plt.scatter(st.session_state.EF['STDEV']*100, (st.session_state.EF['EXP_RET']*100).T,
                #             marker='o',
                #             s=130,
                #             c=Point,
                #            # alpha=0.7,
                #             cmap='Paired',
                #             alpha = 1,
                #             linewidths=2,
                #             edgecolors='lightblue')
                # plt.xticks(fontsize=15)
                # plt.yticks(fontsize=15)
                #
                # plt.xlabel('Expected Risk(%)', fontsize=15, labelpad=20)
                # plt.ylabel('Expected Return(%)', fontsize=15, labelpad=20)
                #
                # st.pyplot(EF_point)

                fig_EF = px.scatter(y=st.session_state.EF['EXP_RET'] * 100, x =st.session_state.EF['STDEV'] * 100)
                fig_EF.update_xaxes(title_text='Standard Deviation',showgrid=True, tickmode='linear', dtick=1)
                fig_EF.update_yaxes(title_text='Expected Return',showgrid=True)
                fig_EF.update_layout(showlegend=False)
                fig_EF.update_layout(template='plotly_dark')
                fig_EF.update_traces(marker=dict(color=['red' if i == Target_index else 'blue' for i in range(len(st.session_state.EF))]))

                st.plotly_chart(fig_EF)

            with col_b:

                st.write("Optimal Weight")
                # x = (Target_Weight*100).values.round(2)
                # y = Target_Weight.index
                #
                # fig_bar, ax_bar = plt.subplots(figsize=(20,10.8))
                # width = 0.75  # the width of the bars
                # bar = ax_bar.barh(y, x, color="lightblue", height= 0.8, )
                #
                # for bars in bar:
                #     width = bars.get_width()
                #     posx = width + 0.5
                #     posy = bars.get_y() + bars.get_height() * 0.5
                #     ax_bar.text(posx, posy, '%.1f' % width, rotation=0, ha='left', va='center', fontsize=13)
                #
                #
                # plt.xticks(fontsize=15)
                # plt.yticks(fontsize=15)
                # plt.xlabel('Weight(%)', fontsize=15, labelpad=20)
                # plt.ylabel('Assets', fontsize=15, labelpad=15)
                # ax_bar.margins(x=0.04, y=0.01)
                #
                # st.pyplot(fig_bar)
                #

                # st.session_state.Result2 = st.session_state.Result.drop(st.session_state.Result.columns[[0, 1]], axis=1, inplace=False).T
                #
                # st.session_state.EF.iloc[Target_index]
                #
                # st.session_state.Result


                # st.dataframe(pd.concat([st.session_state.Result.iloc[1:3].drop(['EXP_RET', 'STDEV'], axis=1).T,
                #                         st.session_state.EF.drop(['EXP_RET', 'STDEV'], axis=1).iloc[Target_index].T],axis=1))
                st.session_state.pie_data = pd.concat([st.session_state.Result.iloc[0:3].drop(['EXP_RET', 'STDEV'], axis=1).T,
                                        st.session_state.EF.drop(['EXP_RET', 'STDEV'], axis=1).iloc[Target_index].T],axis=1)
                st.session_state.pie_data.iloc[:, -1] = (st.session_state.pie_data.iloc[:, -1]*100).round(1)

                fig_pie = px.sunburst(st.session_state.pie_data, path=['asset_category','name'], values=st.session_state.pie_data.columns[-1])
                fig_pie.update_traces(textinfo='label+percent entry')

                st.plotly_chart(fig_pie)


            col_c, col_d = st.columns([1, 1])

            with col_c:
                st.write("Weight vs Return")

                # fig_4, ax_4 = plt.subplots(figsize=(20,10))
                # ax_4.stackplot(st.session_state.EF['EXP_RET']*100, (st.session_state.EF*100).drop(['EXP_RET', 'STDEV'], axis=1).T,
                #                labels = Target_Weight.index, alpha = 0.4, edgecolors="face", linewidths=2)
                #
                # handles, labels = ax_4.get_legend_handles_labels()
                # ax_4.legend(reversed(handles), reversed(labels),loc='lower left', fontsize=14)
                # plt.xticks(fontsize=15)
                # plt.yticks(fontsize=15)
                # plt.xlabel('Return(%)', fontsize=15, labelpad=20)
                # plt.ylabel('Weight(%)', fontsize=15, labelpad=15)
                # ax_4.margins(x=0, y=0)
                #
                # st.pyplot(fig_4)
                #st.write(st.session_state.EF.iloc[:,2:].columns)
                fig_WE = px.area(st.session_state.EF,x='EXP_RET', y=st.session_state.EF.iloc[:,2:].columns)

                fig_WE.update_layout(
                    legend=dict(
                        x=0.0,
                        y=0.0,
                        traceorder='normal',
                        bgcolor='rgba(255, 255, 255, 0.5)',
                        bordercolor='rgba(0, 0, 0, 0.5)',
                        borderwidth=1
                    )
                )


                fig_WE.update_xaxes(title_text='Expected Return', showgrid=True)
                fig_WE.update_yaxes(title_text='Weight', showgrid=True)
                fig_WE.update_layout(height=500)
                #fig_WE.update_layout(showlegend=False)

                st.plotly_chart(fig_WE)


            with col_d:
                st.write("Weight vs STDEV")

                # fig_4, ax_4 = plt.subplots(figsize=(20,10))
                # ax_4.stackplot(st.session_state.EF['EXP_RET']*100, (st.session_state.EF*100).drop(['EXP_RET', 'STDEV'], axis=1).T,
                #                labels = Target_Weight.index, alpha = 0.4, edgecolors="face", linewidths=2)
                #
                # handles, labels = ax_4.get_legend_handles_labels()
                # ax_4.legend(reversed(handles), reversed(labels),loc='lower left', fontsize=14)
                # plt.xticks(fontsize=15)
                # plt.yticks(fontsize=15)
                # plt.xlabel('Return(%)', fontsize=15, labelpad=20)
                # plt.ylabel('Weight(%)', fontsize=15, labelpad=15)
                # ax_4.margins(x=0, y=0)
                #
                # st.pyplot(fig_4)
                # st.write(st.session_state.EF.iloc[:,2:].columns)
                fig_WV = px.area(st.session_state.EF, x='STDEV', y=st.session_state.EF.iloc[:, 2:].columns)

                fig_WV.update_layout(
                    legend=dict(
                        x=0.0,
                        y=0.0,
                        traceorder='normal',
                        bgcolor='rgba(255, 255, 255, 0.5)',
                        bordercolor='rgba(0, 0, 0, 0.5)',
                        borderwidth=1
                    )
                )

                fig_WV.update_xaxes(title_text='Standard Deviation', showgrid=True)
                fig_WV.update_yaxes(title_text='Weight', showgrid=True)
                fig_WV.update_layout(height=500)

                st.plotly_chart(fig_WV)


        st.download_button(
                label="Efficient Frontier",
                data=st.session_state.Result.to_csv(index=False),
                mime='text/csv',
                file_name='Efficient Frontier.csv')

        #if st.button('Simulation'):
        if ('input_simul_price' not in st.session_state) or (st.session_state.key == key):


        #################################################################################################



            st.session_state.Target = Target

            st.session_state.Target_alloc = st.session_state.EF[abs(st.session_state.EF['EXP_RET'] - Target) ==
                                                                min(abs(st.session_state.EF['EXP_RET'] - Target))].drop(columns=['EXP_RET', 'STDEV']).iloc[0]



            st.session_state.Target_alloc['Cash'] = 1 - st.session_state.Target_alloc.sum().sum()

            st.session_state.Target_alloc_input = st.session_state.Target_alloc.values.tolist()

            st.session_state.input_simul_price = input_simul_price



            st.session_state.input_simul_price = pd.concat([st.session_state.input_simul_price,
                                                      pd.DataFrame({'Cash': [100] *
                                                                            len(st.session_state.input_simul_price)},
                                                                   index=st.session_state.input_simul_price.index)], axis=1)



            st.session_state.portfolio_port, st.session_state.allocation_f = \
                backtest.simulation(st.session_state.input_simul_price, st.session_state.Target_alloc, 0, 'Monthly', 'Daily')

            st.session_state.alloc = st.session_state.allocation_f.copy()
            st.session_state.ret = (st.session_state.input_simul_price.iloc[1:] / st.session_state.input_simul_price.shift(1).dropna()) - 1

            st.session_state.attribution = ((st.session_state.ret * (
                st.session_state.alloc.shift(1).dropna())).dropna() + 1).prod(axis=0) - 1

            # if monthly == True:
            #     st.session_state.portfolio_port = st.session_state.portfolio_port[
            #         st.session_state.portfolio_port.index.is_month_end == True]

            st.session_state.drawdown = backtest.drawdown(st.session_state.portfolio_port)
            st.session_state.input_price_N = st.session_state.input_simul_price[
                (st.session_state.input_simul_price.index >= st.session_state.portfolio_port.index[0]) &
                (st.session_state.input_simul_price.index <= st.session_state.portfolio_port.index[-1])]
            st.session_state.input_price_N = 100 * st.session_state.input_price_N / st.session_state.input_price_N.iloc[0, :]

            st.session_state.portfolio_port.index = st.session_state.portfolio_port.index.date
            st.session_state.drawdown.index = st.session_state.drawdown.index.date
            st.session_state.input_price_N.index = st.session_state.input_price_N.index.date
            st.session_state.alloc.index = st.session_state.alloc.index.date

            st.session_state.result = pd.concat([st.session_state.portfolio_port,
                                                 st.session_state.drawdown,
                                                 st.session_state.input_price_N,
                                                 st.session_state.alloc], axis=1)

            st.session_state.START_DATE = st.session_state.portfolio_port.index[0].strftime("%Y-%m-%d")
            st.session_state.END_DATE = st.session_state.portfolio_port.index[-1].strftime("%Y-%m-%d")
            st.session_state.Total_RET = round(float(st.session_state.portfolio_port[-1] / 100 - 1) * 100, 2)
            st.session_state.Anuuual_RET = round(float(((st.session_state.portfolio_port[-1] / 100) ** (
                    annualization / (len(st.session_state.portfolio_port) - 1)) - 1) * 100), 2)
            st.session_state.Anuuual_Vol = round(
                float(np.std(st.session_state.portfolio_port.pct_change().dropna())
                      * np.sqrt(annualization) * 100), 2)

            st.session_state.MDD = round(float(min(st.session_state.drawdown) * 100), 2)
            st.session_state.Daily_RET = st.session_state.portfolio_port.pct_change().dropna()

    #################################################################################################

        st.session_state.result_expander1 = st.expander('Result', expanded=True)

        with st.session_state.result_expander1:

            if 'Target' in st.session_state:

                st.write(" ")

                col50, col51, col52, col53, col54 = st.columns([1, 1, 1, 1, 1])

                with col50:
                    st.info("Period: " + str(st.session_state.START_DATE) + " ~ " + str(st.session_state.END_DATE))

                with col51:
                    st.info("Total Return: " + str(st.session_state.Total_RET) + "%")


                with col52:
                    st.info("Annual Return: " + str(st.session_state.Anuuual_RET) + "%")


                with col53:
                    st.info("Annual Volatility: " + str(st.session_state.Anuuual_Vol) + "%")

                with col54:

                    st.info("MDD: " + str(st.session_state.MDD) + "%")

                col21, col22, col23, col24 = st.columns([0.8, 0.8, 3.5, 3.5])

                with col21:
                    st.write('NAV')
                    st.dataframe(st.session_state.portfolio_port.round(2))

                    st.download_button(
                        label="Download",
                        data=st.session_state.result.to_csv(index=True),
                        mime='text/csv',
                        file_name='Result.csv')

                with col22:
                    st.write('MDD')
                    st.dataframe(st.session_state.drawdown.apply(lambda x: '{:.2%}'.format(x)))

                with col23:
                    st.write('Normalized Price')
                    st.dataframe((st.session_state.input_price_N).
                                 astype('float64').round(2))

                with col24:
                    st.write('Floating Weight')
                    st.dataframe(st.session_state.alloc.applymap('{:.2%}'.format))

                st.write(" ")

                col31, col32 = st.columns([1, 1])

                with col31:
                    st.write("Net Asset Value")
                    # st.pyplot(backtest_graph2.line_chart(st.session_state.portfolio_port, ""))

                    fig = px.line(st.session_state.portfolio_port.round(2))

                    fig.update_xaxes(title_text='Time',showgrid=True)
                    fig.update_yaxes(title_text='NAV',showgrid=True)
                    fig.update_layout(showlegend=False)

                    st.plotly_chart(fig)

                with col32:
                    st.write("Maximum Drawdown")
                    #st.pyplot(backtest_graph2.line_chart(st.session_state.drawdown, ""))

                    fig_MDD = px.line(st.session_state.drawdown)

                    fig_MDD.update_xaxes(title_text='Time',showgrid=True)
                    fig_MDD.update_yaxes(title_text='MDD',showgrid=True)
                    fig_MDD.update_layout(showlegend=False)
                    st.plotly_chart(fig_MDD)

                col61, col62 = st.columns([1, 1])

                with col61:

                    st.download_button(
                        label="Download",
                        data=st.session_state.portfolio_port.to_csv(index=True),
                        mime='text/csv',
                        file_name='Net Asset Value.csv')

                with col62:

                    st.download_button(
                        label="Download",
                        data=st.session_state.drawdown.to_csv(index=True),
                        mime='text/csv',
                        file_name='Maximum Drawdown.csv')

                st.write(" ")

                col_a, col_b, = st.columns([1, 1])

                with col_a:

                    st.write("Performance Attribution")
                    # st.session_state.attribution.index = pd.Index(
                    #     st.session_state.attribution.index.map(lambda x: str(x)[:7]))
                    #
                    # x = (st.session_state.attribution * 100)
                    # y = st.session_state.attribution.index
                    #
                    # fig_bar, ax_bar = plt.subplots(figsize=(18, 11))
                    # width = 0.75  # the width of the bars
                    # bar = ax_bar.barh(y, x, color="lightblue", height=0.8, )
                    #
                    # for bars in bar:
                    #     width = bars.get_width()
                    #     posx = width + 0.01
                    #     posy = bars.get_y() + bars.get_height() * 0.5
                    #     ax_bar.text(posx, posy, '%.1f' % width, rotation=0, ha='left', va='center', fontsize=13)
                    #
                    # plt.xticks(fontsize=15)
                    # plt.yticks(fontsize=15)
                    # plt.xlabel('Attribution(%)', fontsize=15, labelpad=20)
                    # # ax_bar.margins(x=0, y=0)
                    #
                    # st.pyplot(fig_bar)
                    #
                    #


                    st.session_state.attribution2 = st.session_state.attribution.drop(st.session_state.attribution.index[-1],axis=0).copy()
                    st.session_state.pie_data2 = st.session_state.pie_data
                    st.session_state.pie_data2.iloc[:, -1] = (st.session_state.attribution2)
                    st.session_state.pie_data2.iloc[:, -1] = (st.session_state.pie_data2.iloc[:, -1]*100).round(1)
                    

                    fig_pie2 = px.sunburst(st.session_state.pie_data2, path=['asset_category', 'name'], values=st.session_state.pie_data2.columns[-1])
                    fig_pie2.update_traces(textinfo='label+percent entry')

                    st.plotly_chart(fig_pie2)



                with col_b:
                    st.write("Correlation Matrix")
                    #
                    # # Increase the size of the heatmap.
                    # fig2 = plt.figure(figsize=(15, 8.3))
                    # # plt.rc('font', family='Malgun Gothic')
                    # plt.rcParams['axes.unicode_minus'] = False
                    #
                    # st.session_state.corr = st.session_state.input_price.pct_change().dropna().corr().round(2)
                    #
                    # st.session_state.corr.index = pd.Index(st.session_state.corr.index.map(lambda x: str(x)[:7]))
                    # st.session_state.corr.columns = st.session_state.corr.index
                    # # st.session_state.corr.columns = pd.MultiIndex.from_tuples([tuple(map(lambda x: str(x)[:7], col)) for col in st.session_state.corr.columns])
                    #
                    # heatmap = sns.heatmap(st.session_state.corr, vmin=-1, vmax=1, annot=True, cmap='coolwarm')
                    #
                    # # heatmap.set_title('Correlation Heatmap', fontdict={'fontsize': 20}, pad=12)
                    #
                    # st.pyplot(fig2)

                    st.session_state.corr = st.session_state.input_price.pct_change().dropna().corr().round(2)        
                    fig_corr = px.imshow(st.session_state.corr,text_auto=True, aspect="auto")
                    st.plotly_chart(fig_corr)

                col71, col72 = st.columns([1, 1])

                with col71:

                    st.download_button(
                        label="Download",
                        data=((st.session_state.ret * (st.session_state.alloc.shift(1).dropna())).dropna()).to_csv(
                            index=True),
                        mime='text/csv',
                        file_name='Attribution.csv')

                with col72:

                    st.download_button(
                        label="Download",
                        data=st.session_state.corr.to_csv(index=True),
                        mime='text/csv',
                        file_name='Correlation.csv')

