import pandas as pd


def cleansing(assets_data=pd.DataFrame(), alloc=list()):

    alloc = pd.DataFrame(alloc).T

    assets_data = pd.DataFrame(assets_data,
                           index=pd.date_range(start=assets_data.index[0],
                                                end=assets_data.index[-1], freq='D')).fillna(method='ffill')

    allocation = pd.DataFrame(index=assets_data.index, columns=assets_data.columns)
    allocation[:] = alloc
    allocation = allocation[allocation.index.is_month_end == True]

    return assets_data, allocation


def simulation(assets_data, allocation, date='1900-01-01', commission=0):

    assets_data = assets_data[assets_data.index>=date]

    if type(allocation)==list:
        assets_data ,allocation = cleansing(assets_data, allocation)

    portfolio = pd.DataFrame(index=assets_data.index, columns=['nav']).squeeze()
    portfolio = portfolio[portfolio.index >= allocation.index[0]]
    portfolio[0] = 100

    k = 0
    j_rebal = 0
    i_rebal=0

    last_alloc = allocation.iloc[0]

    for i in range(0, len(portfolio)-1):


        if portfolio.index[i] in allocation.index:


            # cost = (commission / 100) * x[i - 1] * transaction_weight[i - 1]

            j = assets_data.index.get_loc(portfolio.index[i + 1])
            k = allocation.index.get_loc(portfolio.index[i])
            i_rebal = portfolio.index.get_loc(portfolio.index[i])
            j_rebal = assets_data.index.get_loc(portfolio.index[i])


            transaction_weight = abs(allocation.iloc[k] - last_alloc).sum()
            cost = commission * transaction_weight

            print(transaction_weight)

            portfolio[i + 1] = portfolio[i_rebal]*(1-cost)*\
                               (assets_data.iloc[j]/assets_data.iloc[j_rebal] * allocation.iloc[k]).sum()


            last_alloc = assets_data.iloc[j] / assets_data.iloc[j_rebal] * allocation.iloc[k]

        else:

            j = assets_data.index.get_loc(portfolio.index[i + 1])

            portfolio[i + 1] = portfolio[i_rebal]*(1-cost)*\
                               (assets_data.iloc[j]/assets_data.iloc[j_rebal] * allocation.iloc[k]).sum()


            last_alloc = assets_data.iloc[j] / assets_data.iloc[j_rebal] * allocation.iloc[k]

    return portfolio.astype('float64').round(3)

def drawdown(nav: pd.Series):
    """
    주어진 NAV 데이터로부터 Drawdown을 계산합니다.

    Parameters:
        nav (pd.Series): NAV 데이터. 인덱스는 일자를 나타내며, 값은 해당 일자의 NAV입니다.

    Returns:
        pd.Series: 주어진 NAV 데이터로부터 계산된 Drawdown을 나타내는 Series입니다.
            인덱스는 일자를 나타내며, 값은 해당 일자의 Drawdown입니다.
    """
    # 누적 최대값 계산
    cummax = nav.cummax()

    # 현재 값과 누적 최대값의 차이 계산
    drawdown = nav - cummax

    # Drawdown 비율 계산
    drawdown_pct = drawdown / cummax

    drawdown_pct.name = 'drawdown'

    return drawdown_pct
