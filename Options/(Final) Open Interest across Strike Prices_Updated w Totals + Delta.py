import pandas as pd
import numpy as np
import yfinance as yf
import datetime
import matplotlib.pyplot as plt

def options_chain(symbol):
    tk = yf.Ticker(symbol)
    try:
        current_price = tk.info['regularMarketPrice']
    except KeyError:
        if 'previousClose' in tk.info:
            current_price = tk.info['previousClose']
        else:
            current_price = None
            print("Warning: No price data available for this symbol.")
    
    exps = tk.options
    if not exps:
        raise ValueError("No options data found for this symbol.")

    options = pd.DataFrame()
    for e in exps:
        opt = tk.option_chain(e)
        opt_combined = pd.concat([opt.calls, opt.puts])
        opt_combined['expirationDate'] = e
        options = pd.concat([options, opt_combined], ignore_index=True)

    options['expirationDate'] = pd.to_datetime(options['expirationDate'])
    options['dte'] = (options['expirationDate'] - datetime.datetime.today()).dt.days / 365
    options['CALL'] = options['contractSymbol'].str[4:].apply(lambda x: "C" in x)
    options[['bid', 'ask', 'strike', 'openInterest']] = options[['bid', 'ask', 'strike', 'openInterest']].apply(pd.to_numeric)
    options = options.drop(columns=['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate', 'lastPrice'])

    return options, current_price

def is_third_friday(date):
    """Check if a given date is the third Friday of the month."""
    first_day = datetime.date(date.year, date.month, 1)
    first_friday = first_day + datetime.timedelta(days=(4 - first_day.weekday() + 7) % 7)
    third_friday = first_friday + datetime.timedelta(weeks=2)
    return date.date() == third_friday

symbol = input("Enter the stock symbol: ").strip()
try:
    options_data, current_price = options_chain(symbol)
except yfinance.exceptions.YFinanceException as e:
    print(f"An error occurred: {e}. Please check the stock symbol and try again.")
else:
    expiration_dates = options_data['expirationDate'].unique()
    deltas = []
    for expiration in expiration_dates:
        num_contracts = options_data[options_data['expirationDate'] == expiration].shape[0]
        calls_open_interest = options_data[(options_data['expirationDate'] == expiration) & (options_data['CALL'] == True)]['openInterest'].sum()
        puts_open_interest = options_data[(options_data['expirationDate'] == expiration) & (options_data['CALL'] == False)]['openInterest'].sum()
        delta_open_interest = abs(calls_open_interest - puts_open_interest)
        dominant = 'C' if calls_open_interest > puts_open_interest else 'P'
        deltas.append((expiration, delta_open_interest, dominant))
        opex_label = " (Monthly OPEX)" if is_third_friday(expiration) else ""
        print(f"Expiration Date: {expiration.date()}{opex_label}, Number of Contracts: {num_contracts}, Calls Open Interest: {calls_open_interest}, Puts Open Interest: {puts_open_interest}, Delta: +{delta_open_interest}{dominant}")
    
    if current_price is not None:
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")

        # Plotting the Delta
        delta_dates = [d[0] for d in deltas]
        delta_values = [d[1] for d in deltas]
        delta_labels = [d[2] for d in deltas]

        plt.figure(figsize=(10, 5))
        bars = plt.bar(delta_dates, delta_values, color=['blue' if d == 'C' else 'red' for d in delta_labels], alpha=0.5)
        
        for bar, label in zip(bars, delta_labels):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{label}', ha='center', va='bottom')

        plt.title(f'Delta of Open Interest (Calls vs Puts) for {symbol} as of {today_date}')
        plt.xlabel('Expiration Date')
        plt.ylabel('Delta of Open Interest')
        plt.grid(True)
        plt.show()
    else:
        print("Plot not generated due to lack of current price data.")
