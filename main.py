import pandas as pd
import yfinance as yf
from sendemail import send_email
from jinja2 import Template
from datetime import datetime, timedelta

# read the stocks and filter to the ones needed
stocks = pd.read_csv('stocks_universe.csv')
stocks = stocks[(stocks['CapCategory'] == 'mega') | (stocks['sector'].isin(['Technology', 'Financial Services']))]

# config
errors = []
l_52w_high = []
crossover_sma = []
crossover_sma_days  = 200
data = {
    'crossover_sma_days ': crossover_sma_days ,}

# calculate the start date 2 years from now
current_date = datetime.now()
start_date = (current_date + timedelta(days=-2*365)).strftime("%Y-%m-%d")  # Approximate 2 years as 2 * 365 days

for index, row in stocks.iterrows():
    stock = row['symbol']

    try:
        df = yf.download(stock, start=start_date)['Adj Close'].to_frame()
        df.sort_values('Date', inplace=True, ascending=True)
        df['pct_change'] = df['Adj Close'].pct_change()

        # 52-week high calculation
        df['52W_high'] = df['Adj Close'].rolling(window=252).max()
        df['52W_high'] = df['52W_high'] == df['Adj Close']
        # calculate how many highs last month
        df['52W_high_count'] = df['52W_high'].rolling(window=22).sum()
        if df['52W_high'].iloc[-1]:
            l_52w_high.append({'ticker': stock,
                               'name': row['shortName'],
                               'sector_industry': f'{row["sector"]} / {row["industry"]}',
                               'cap': row['CapCategory'],
                               'close': round(df['Adj Close'].iloc[-1], 2),
                               'pct_change': round(df['pct_change'].iloc[-1] * 100, 2),
                               'last_month_52highs': df['52W_high_count'].iloc[-1]})

        # crossover_sma
        sma_col = "sma_" + str(crossover_sma_days)
        df[sma_col] = df['Adj Close'].rolling(window=crossover_sma_days).mean()
        if df['Adj Close'].iloc[-1] > df[sma_col].iloc[-1] and df['Adj Close'].iloc[-2] < df[sma_col].iloc[-2]:
            crossover_sma.append({'ticker': stock,
                                  'name': row['shortName'],
                                  'sector_industry': f'{row["sector"]} / {row["industry"]}',
                                  'cap': row['CapCategory'],
                                  'close': round(df['Adj Close'].iloc[-1], 2),
                                  'pct_change': round(df['pct_change'].iloc[-1] * 100, 2)})

    except Exception as e:
        errors.append({'stock': stock, 'error': str(e)})

# get sp500 data
try:
    df = yf.download('^GSPC', start=start_date)['Adj Close'].to_frame()
    df.sort_values('Date', inplace=True, ascending=True)
    df['pct_change'] = df['Adj Close'].pct_change()
    data['sp500'] = round(df['Adj Close'].iloc[-1],2)
    data['sp_pct_change'] = round(df['pct_change'].iloc[-1]*100, 2)
except:
    errors.append('Could not get SP500 data')

# create the body of the email and send it
with open('email_template.html', 'r') as file:
    html_template = file.read()
template = Template(html_template)
html_output = template.render(data_52w_high=l_52w_high, data_crossover=crossover_sma, errors=errors, data=data)

send_email("Daily Stocks Email", html_output)
