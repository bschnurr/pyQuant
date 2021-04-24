import pandas as pd
import pandas_datareader.data as web
import datetime as dt
import numpy as np
from prettytable import PrettyTable

import helper

def performance_comparison(mpList, mpName):
    
    port_overview = PrettyTable()

    port_overview.field_names = ['INCEPTION DATE', 'MODEL PORTFOLIOS', 'CAGR', 'MDD', 'SHARPE']
    
    for i in range(len(mpList)):
        measures = portfolio_measures(mpList[i])
        port_overview.add_row([measures[0], # INCEPTION DATE
                               mpName[i],# MODEL PORTFOLIO
                               "{:.2f} %".format(measures[1] * 100), # CAGR
                               "{:.2f} %".format(measures[2] * 100), # MDD
                               "{:.2f}".format(measures[3])]) # SHARPE RATIO
    
    port_overview.sortby = 'SHARPE'
    port_overview.reversesort = True
    print(port_overview.get_string(title='MODEL PORTFOLIO PERFORMANCE COMPARISON (as of {})'.format(dt.datetime.today().strftime('%b-%d-%Y'))))

def _retrieve_price(symbols):
    
    START_DATE = dt.datetime(1970,1,1)
    END_DATE = dt.datetime.today()
    
    df = pd.DataFrame()
    
    for symbol in symbols:
        df[symbol] = web.DataReader(symbol, 'yahoo', START_DATE, END_DATE)['Adj Close']
    
    return df

def portfolio_measures(data):
    """
    input: dictionary data symbols as keys and weights as values
    returns portfolio CAGR
    """
    symbols = list(data.keys())
    weights = np.array(list(data.values()))
    
    df = _retrieve_price(symbols)    
    
    daily_returns = df.pct_change()    
    cumulative_returns = (1 + daily_returns).cumprod()
    cumulative_returns.fillna(1,inplace=True)
    cagr = cumulative_returns**(helper.days_year/len(cumulative_returns.index)) - 1
    
    port_cagr = np.dot(cagr.iloc[-1,:],weights)
    
    cov_matrix = daily_returns.cov() * helper.days_year    
    port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    
    port_sharpe = (port_cagr - helper.risk_free) / port_vol
    
    wealth_idx = 1 * (1 + daily_returns).cumprod()    
    previous_peaks = wealth_idx.cummax()
    drawdown = (wealth_idx - previous_peaks) / previous_peaks
    mdd = drawdown.min()
    
    port_mdd = 0
    
    for i in range(len(mdd.values)):
        port_mdd = port_mdd + (mdd.values[i] * weights[i])
    # print(mdd.values[0])
    # print(mdd.values[1])
    
    return df.index[0].strftime('%b-%d-%Y'), port_cagr, port_mdd, port_sharpe

if __name__ == '__main__':
    portfolio_measures({'VFV.TO': 0.5, 'XBB.TO': 0.5})