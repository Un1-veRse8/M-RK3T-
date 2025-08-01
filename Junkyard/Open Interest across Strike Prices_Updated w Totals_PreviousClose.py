import pandas as pd
import yfinance as yf
import datetime
import matplotlib.pyplot as plt

def get_last_trading_day():
    today = datetime.datetime.now()
    if today.hour < 17:  # Assuming data is not reliable for the current day before 5 PM
        today -= datetime.timedelta(days=1)
    weekday = today.weekday()
    if weekday >= 5:  # Adjust for weekends, when markets are closed
        today -= datetime.timedelta(days=(weekday - 4))
    return today.date()

def fetch_options_data(symbol):
    tk = yf.Ticker(symbol)
    exps = tk.options
    if not exps:
        raise ValueError("No options data found for this symbol.")

    options = pd.DataFrame()
    for e in exps:
        opt = tk.option_chain(e)
        opt.calls['type'] = 'Call'
        opt.puts['type'] = 'Put'
        opt_combined = pd.concat([opt.calls, opt.puts])
        opt_combined['expirationDate'] = e
        options = pd.concat([options, opt_combined], ignore_index=True)
    
    return options

def get_valid_options_data(options, as_of_date):
    options['expirationDate'] = pd.to_datetime(options['expirationDate'])
    options['dte'] = (options['expirationDate'] - pd.to_datetime(as_of_date)).dt.days / 365
    options[['bid', 'ask', 'strike', 'openInterest']] = options[['bid', 'ask', 'strike', 'openInterest']].apply(pd.to_numeric, errors='coerce')
    options = options.drop(columns=['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate', 'lastPrice'])
    
    # Filter out rows where openInterest is NaN or zero
    options = options.dropna(subset=['openInterest'])
    options = options[options['openInterest'] > 0]

    return options

def options_chain(symbol, as_of_date):
    tk = yf.Ticker(symbol)
    try:
        # Fetch data for the last 5 days to ensure we get some valid data
        historical_data = tk.history(start=as_of_date - datetime.timedelta(days=5), end=as_of_date)
        if historical_data.empty:
            raise ValueError("No historical data available for the requested period.")
        current_price = historical_data['Close'].dropna().iloc[-1]  # Safely pick the last available close price
    except Exception as e:
        current_price = None
        print(f"Warning: Unable to fetch closing price for last trading day due to: {e}")

    options = fetch_options_data(symbol)
    valid_options = get_valid_options_data(options, as_of_date)

    return valid_options, current_price

last_trading_day = get_last_trading_day()
symbol = input("Enter the stock symbol: ").strip()
try:
    options_data, current_price = options_chain(symbol, last_trading_day)
except Exception as e:
    print(f"An error occurred: {e}. Please check the stock symbol and try again.")
else:
    expiration_dates = options_data['expirationDate'].unique()
    for expiration in expiration_dates:
        num_contracts = options_data[options_data['expirationDate'] == expiration].shape[0]
        print(f"Expiration Date: {expiration.date()}, Number of Contracts: {num_contracts}")

    option_type = input("Display open interest for Calls, Puts or Both? (Enter 'Call', 'Put', or 'Both'): ")
    if current_price is not None:
        plt.figure(figsize=(10, 5))

        if option_type in ['Call', 'Both']:
            calls = options_data[options_data['type'] == 'Call']
            total_calls = calls['openInterest'].sum()
            print(f"Total Call Open Interest: {total_calls}")
            plt.bar(calls['strike'], calls['openInterest'], width=1, color='blue', label=f'Calls (Total OI: {total_calls})', alpha=0.5)

        if option_type in ['Put', 'Both']:
            puts = options_data[options_data['type'] == 'Put']
            total_puts = puts['openInterest'].sum()
            print(f"Total Put Open Interest: {total_puts}")
            plt.bar(puts['strike'], puts['openInterest'], width=1, color='red', label=f'Puts (Total OI: {total_puts})', alpha=0.5)

        plt.axvline(x=current_price, color='green', linestyle='dashed', linewidth=1, label=f'Current Price: {current_price:.2f}')
        plt.title(f'Open Interest across All Strike Prices for {symbol} as of {last_trading_day}')
        plt.xlabel('Strike Price')
        plt.ylabel('Open Interest')
        plt.legend()
        plt.grid(True)
        plt.show()
    else:
        print("Plot not generated due to lack of current price data.")
