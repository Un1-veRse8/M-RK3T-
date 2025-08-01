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

    options['expirationDate'] = pd.to_datetime(options['expirationDate']) + datetime.timedelta(days=1)
    options['dte'] = (options['expirationDate'] - datetime.datetime.today()).dt.days / 365
    options['CALL'] = options['contractSymbol'].str[4:].apply(lambda x: "C" in x)
    options[['bid', 'ask', 'strike', 'volume']] = options[['bid', 'ask', 'strike', 'volume']].apply(pd.to_numeric)
    options = options.drop(columns=['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate', 'lastPrice'])

    return options, current_price

# Example of how to call the function
symbol = input("Enter the stock symbol: ")
option_type = input("Display volume for Calls, Puts or Both? (Enter 'Call', 'Put', or 'Both'): ")
options_data, current_price = options_chain(symbol)

if current_price is not None:
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")  # Format today's date

    plt.figure(figsize=(10, 5))
    if option_type in ['Call', 'Both']:
        volume_agg_calls = options_data[options_data['CALL'] == True].groupby('strike')['volume'].sum()
        plt.bar(volume_agg_calls.index, volume_agg_calls.values, width=1, color='blue', label='Calls', alpha=0.5)
    if option_type in ['Put', 'Both']:
        volume_agg_puts = options_data[options_data['CALL'] == False].groupby('strike')['volume'].sum()
        plt.bar(volume_agg_puts.index, volume_agg_puts.values, width=1, color='red', label='Puts', alpha=0.5)

    # Adding Current Price to Chart
    plt.axvline(x=current_price, color='green', linestyle='dashed', linewidth=1, label='Current Price')

    # Adding a text watermark
    plt.text(0.5, 0.5, 'o5341V', fontsize=40, color='gray', ha='center', va='center', alpha=0.5, transform=plt.gca().transAxes)

    plt.title(f'Volume Aggregated Across All Strike Prices for: ${symbol}\nas of {today_date}')
    plt.xlabel('Strike Price')
    plt.ylabel('Aggregated Volume')
    plt.legend()
    plt.grid(True)
    plt.show()
else:
    print("Plot not generated due to lack of current price data.")
