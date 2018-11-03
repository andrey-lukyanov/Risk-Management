import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like

import pandas_datareader as web
import fix_yahoo_finance as yf
yf.pdr_override() # <== that's all it takes :-)

#Stocks
ticker_list = ["HSBA.L", "BARC.L", 'LLOY.L', "RBS.L", "BP.L", "rdsa.l", "RIO.L", "AAL.L"]

data = web.data.get_data_yahoo(ticker_list, start="2009-07-02", end="2012-07-01")['Close']
data = data.interpolate(method = 'time', axis = 0)
print(data)
print(data.isna().sum())
data.to_csv('stock_prices.csv')

#FX
from pandas_datareader.stooq import StooqDailyReader
import datetime as dt

start_date = dt.date(2009, 7, 1)
end_date = dt.date(2012, 7, 1)

fx = StooqDailyReader(symbols='rubgbp', start="2009-07-01", end="2012-07-01").read()
fx = fx.sort_index()
fx = fx[start_date:end_date]['Close']
print(fx)
fx.to_csv('rubgbp.csv', header=['Close'])