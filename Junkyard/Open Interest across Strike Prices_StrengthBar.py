import pandas as pd
import numpy as np
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def get_last_trading_day():
    today = datetime.datetime.now()
    if today.hour < 17:  # Assuming data is not reliable for the current day before 5 PM
        today -= datetime.timedelta(days=1)
    weekday = today.weekday()
    if weekday >= 5:  # Adjust for weekends, when markets are closed
        today -= datetime.timedelta(days=(weekday-4))
    return today.date()

def options_chain(symbol, as_of_date):
    tk = yf.Ticker(symbol)
    try:
        historical_data = tk.history(start=as_of_date - datetime.timedelta(days=5), end=as_of_date)
        if historical_data.empty:
            raise ValueError("No historical data available for the requested period.")
        current_price = historical_data['Close'].dropna().iloc[-1]
    except Exception as e:
        current_price = None
        print(f"Warning: Unable to fetch closing price for last trading day due to: {e}")

    exps = tk.options
    if not exps:
        raise ValueError("No options data found for this symbol.")

    options = pd.DataFrame()
    for e in exps:
        opt = tk.option_chain(e)
        opt_combined = pd.concat([opt.calls, opt.puts])
        opt_combined['expirationDate'] = e
        options = pd.concat([options, opt_combined], ignore_index=True)

    options['expirationDate'] = pd.to_datetime(options['expirationDate']) + datetime.timedelta(days=1)
    options['dte'] = (options['expirationDate'] - pd.to_datetime(as_of_date)).dt.days / 365
    options['CALL'] = options['contractSymbol'].str[4:].apply(lambda x: "C" in x)
    options[['bid', 'ask', 'strike', 'openInterest']] = options[['bid', 'ask', 'strike', 'openInterest']].apply(pd.to_numeric)
    options = options.drop(columns=['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate', 'lastPrice'])

    return options, current_price

last_trading_day = get_last_trading_day()
symbol = input("Enter the stock symbol: ").strip()
try:
    options_data, current_price = options_chain(symbol, last_trading_day)
except Exception as e:
    print(f"An error occurred: {e}. Please check the stock symbol and try again.")
else:
    option_type = input("Display open interest for Calls, Puts or Both? (Enter 'Call', 'Put', or 'Both'): ")
    if current_price is not None:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={'width_ratios': [3, 1]})

        if option_type in ['Call', 'Both']:
            calls = options_data[options_data['CALL'] == True]
            total_calls = calls['openInterest'].sum()
            ax1.bar(calls['strike'], calls['openInterest'], width=1, color='blue', label='Calls', alpha=0.6)

        if option_type in ['Put', 'Both']:
            puts = options_data[options_data['CALL'] == False]
            total_puts = puts['openInterest'].sum()
            ax1.bar(puts['strike'], puts['openInterest'], width=1, color='red', label='Puts', alpha=0.6)

        ax1.axvline(x=current_price, color='green', linestyle='dashed', linewidth=1, label='Current Price')
        ax1.set_title(f'Open Interest across Strike Prices for {symbol} as of {last_trading_day}')
        ax1.set_xlabel('Strike Price')
        ax1.set_ylabel('Open Interest')
        ax1.legend()
        ax1.grid(True)

        # Side Bar Plot for the strength of calls vs puts
        total_open_interest = total_calls + total_puts
        call_proportion = (total_calls / total_open_interest) * 100 if total_open_interest > 0 else 0
        put_proportion = (total_puts / total_open_interest) * 100 if total_open_interest > 0 else 0
        ax2.barh(['Option Dominance'], [call_proportion], color='blue')
        ax2.barh(['Option Dominance'], [put_proportion], color='red', left=call_proportion)
        ax2.set_xlim(0, 100)
        ax2.set_title('Call vs Put Dominance')
        ax2.set_xlabel('Percentage of Total Open Interest')

        plt.tight_layout()
        plt.show()
    else:
        print("Plot not generated due to lack of current price data.")
