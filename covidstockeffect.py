import datetime
from distutils import text_file
from matplotlib.pyplot import text
from numpy import size
import pandas_datareader as pdr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import cufflinks as cf
import chart_studio.plotly as py

# start and end dates of stock analysis
start_date = '2018-01-01'
end_date = datetime.date.today().strftime('%Y-%m-%d')

# ticker symbols I am interested in
tickers = ["^DJI", "^GSPC", "^IXIC", "ZM", "NFLX", "FB", "AAL"]

# stored dataframes
each_df = {}
for ticker in tickers:
    each_df[ticker] = pdr.data.DataReader(ticker, 'yahoo', start_date, end_date)

# concatenate dataframes with each ticker together
stocks = pd.concat(each_df, axis=1, keys=tickers)
stocks.columns.names = ['Ticker Symbol', 'Stock Info']

# shape of data
stocks.shape

# summary of datatypes and memory usage
stocks.info()

# look at descriptive statistics of data across horizontal axis
descriptive_statistics = stocks.describe().transpose().style.format("{:.2f}")

# adjusted closing prices dataframe for plotting
adj_closing_price_df = stocks.xs(key='Adj Close', axis=1, level=1)

# plotly python package line plot of adjusted closing prices dataframe
fig = px.line(adj_closing_price_df, x=adj_closing_price_df.index, y=adj_closing_price_df.columns, title="Adjusted Closing Prices")
fig.update_layout(hovermode='x',yaxis_title="Price")
fig.show()

#plotly candlestick chart
#input specific ticker to view candlestick chart of it
# ticker = ""
# fig_candle = go.Figure(data=[go.Candlestick(x=each_df[ticker].index,
                        #open=each_df[ticker]['Open'],
                        #high=each_df[ticker]['High'],
                        #low=each_df[ticker]['Low'],
                        #close=each_df[ticker]['Close'])])
# fig_candle.update_layout(
    #title='Candlestick Chart',
    #yaxis_title='Price',
    #xaxis_title='Date',
    #hovermode='x')
# fig_candle.show()

# stocks return after each day dataframe
dreturns = pd.DataFrame()

# use pct_change() method to get a value from the Adjusted Closing Prices to create a new column representing this value
for ticker in tickers:
    dreturns[ticker] = adj_closing_price_df[ticker].pct_change()*100

# average adjusted returns since 2018
average_returns = dreturns.mean()
avg_return_frame = average_returns.to_frame()

# day of worst single day returns for each company
worst_return = dreturns.idxmin()
# day of best single day returns for each company
best_return = dreturns.idxmax()
# dataframe to showcase best and worst day returns for each company
bw_returns = pd.DataFrame({"Worst": worst_return, "Best": best_return})
bw_returns.columns.names = ['Single Day Returns']
bw_returns.index.names = ['Ticker']

# comparing standard deviations of stocks over the course of 2019-2020, with a newly created dataframe
std_2019 = dreturns.loc['2019-01-01':'2019-12-31'].std()
std_2020 = dreturns.loc['2020-01-01':'2020-12-31'].std()
std_comparison_df = pd.DataFrame({"2019":std_2019, "2020":std_2020})
std_comparison_df.columns.names = ['Standard Deviation Over Years Comparison']
std_comparison_df.index.names = ['Ticker']

# risk vs. returns scatter plot
fig_risk = px.scatter(dreturns, x=dreturns.mean(), y=dreturns.std(),
                    text=dreturns.columns, size_max=60, labels={
                        "x":"Daily Expected Returns (%)",
                        "y":"Risk",
                    },
                    title="Stock Risk Vs. Returns")
fig_risk.update_xaxes(zeroline=True,zerolinewidth=2,zerolinecolor='Black')
fig_risk.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='Black')
fig_risk.update_traces(textposition='top center')
fig_risk.show()

# utilizing python cufflinks package to create a simple moving average for Zoom Co.
ticker_sma = "ZM"
each_df[ticker_sma]['Adj Close'].ta_plot(study='sma',periods=[10])

# utilizing cufflinks to create bollinger bands for Zoom Co.
ticker_bol = "ZM"
each_df[ticker_bol]['Close'].ta_plot(study='boll', periods=20, boll_std=2)

# combining candlestick, simple moving averages, bollinger bands, and trading volume in one plot
# utilize QuantFig class
df_of_interest = each_df['ZM']
qf = cf.QuantFig(df_of_interest,title='A look at Zoom\'s Performance',legend='top',name='GS',up_color='green',down_color='red')
qf.add_bollinger_bands(periods=20,boll_std=2,color=['cyan','grey'],fill=True)
qf.add_volume(name='Volume',up_color='green',down_color='red')
qf.iplot()