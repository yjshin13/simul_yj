import numpy as np
import pandas as pd
from cvxpy import *
import warnings
import arch.bootstrap as bs
warnings.filterwarnings("ignore")
from tqdm import tqdm
# plt.show()


def optimal_portfolio(returns, nPort, cons1, cons2, cons3):

    n = len(returns.columns)
    w = Variable(n)
    mu = returns.mean() * 252
    Sigma = returns.cov() * 252
    gamma = Parameter(nonneg=True)
    ret = mu.values.T * w
    risk = quad_form(w, Sigma.values)
    prob = Problem(Maximize(ret - gamma * risk),
                   [sum(w) == 1, w >= 0.0,
                    sum(w[cons1]) <= 0,  # Equity Weight Constraint
                    sum(w[cons2]) <= 0.2,  # Inflation Protection Constraint
                    sum(w[cons3]) >= 0.8])  # Fixed Income Constraint

    risk_data = np.zeros(nPort)
    ret_data = np.zeros(nPort)
    gamma_vals = np.logspace(-2, 3, num=nPort)
    weights = []

    for i in range(nPort):


        gamma.value = gamma_vals[i]
        prob.solve()
        # prob.solve(verbose=True)
        risk_data[i] = sqrt(risk).value
        ret_data[i] = ret.value
        weights.append(np.squeeze(np.asarray(w.value)))


    weight = pd.DataFrame(data=weights, columns=returns.columns)
    return weight, ret_data, risk_data


def simulation(index_data, sims, nPort, universe):
    # period=int(period/2)+1
    # create date index

    growth = universe.index[universe['asset_class'] == 'equity']
    inflation = universe.index[universe['asset_class'] == 'inflation_protection']
    fixed_income = universe.index[universe['asset_class'] == 'fixed_income']

    input_returns = index_data.pct_change().dropna()
    period = len(input_returns)
    input_returns = np.log(input_returns+1)
    er = input_returns.mean()
    cov = input_returns.cov()
    corr = input_returns.corr()

    dates = pd.date_range(start='2022-08-20', periods=period, freq='D')
    data = []
    # generate 10 years of daily data

    for i in range(0, sims):
        data.append(pd.DataFrame(columns=cov.columns, index=dates,
                                data=np.random.multivariate_normal(er.values, cov.values, period)))
                                #data = resample_returns(input_data, period, 3)))

    #data = bootstrapping(input_returns, n_sim=sims)

    # store values from simulation
    weights = []
    stdev = []
    exp_ret = []

    for i in tqdm(range(0, sims)):

        try:

            # optimize over every simulation
            w, r, std = optimal_portfolio(data[i], nPort, growth, inflation, fixed_income)
            weights.append(w)
            stdev.append(std)
            exp_ret.append(r)

        except SolverError:

            pass

    w = np.mean(weights, axis=0)
    s = np.mean(stdev, axis=0)
    r = np.mean(exp_ret, axis=0)
    concat = np.hstack([a.reshape(nPort, -1) for a in [r, s, w]])
    column_names = list(input_returns.columns)
    Resampled_EF = pd.DataFrame(concat, columns=["EXP_RET", "STDEV"] + column_names)

    return Resampled_EF
