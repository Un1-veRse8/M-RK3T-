import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

# URL of the Wikipedia page containing the list of S&P 500 companies
wiki_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

def get_sp500_symbols():
    response = requests.get(wiki_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    symbols = []
    for row in table.find_all('tr')[1:]:
        symbol = row.find_all('td')[0].text.strip()
        symbols.append(symbol)
    return symbols

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_historical_data(symbols, start_year):
    end_date = pd.Timestamp.today()
    start_date = pd.Timestamp(f"{start_year}-01-01")
    data_dict = {}
    for symbol in symbols:
        data = yf.download(symbol, start=start_date, end=end_date)
        if not data.empty:
            data_dict[symbol] = data
    return data_dict

def get_rsi_values(data_dict):
    rsi_dict = {}
    for symbol, data in data_dict.items():
        rsi = calculate_rsi(data)
        rsi_dict[symbol] = rsi.dropna()
    return rsi_dict

def calculate_rsi_percentages(rsi_dict, spx_index):
    rsi_above_70_percent = {}
    rsi_below_30_percent = {}
    for date in spx_index:
        rsi_above_70 = sum(1 for rsi in rsi_dict.values() if date in rsi.index and rsi.loc[date] > 70) / len(rsi_dict) * 100
        rsi_below_30 = sum(1 for rsi in rsi_dict.values() if date in rsi.index and rsi.loc[date] < 30) / len(rsi_dict) * 100
        rsi_above_70_percent[date] = rsi_above_70
        rsi_below_30_percent[date] = rsi_below_30
    return pd.Series(rsi_above_70_percent), pd.Series(rsi_below_30_percent)

def plot_charts(spx_data, rsi_above_70_percent, rsi_below_30_percent, overlay):
    if overlay:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))

        ax1.plot(spx_data.index, spx_data['Close'], label='SPX', color='blue')
        ax1.set_title('SPX with RSI > 70 (%)')
        ax1.set_ylabel('SPX')
        ax1.legend(loc='upper left')

        ax1_twin = ax1.twinx()
        ax1_twin.plot(rsi_above_70_percent.index, rsi_above_70_percent, label='RSI > 70 (%)', color='red')
        ax1_twin.set_ylabel('RSI > 70 (%)')
        ax1_twin.legend(loc='upper right')

        ax2.plot(spx_data.index, spx_data['Close'], label='SPX', color='blue')
        ax2.set_title('SPX with RSI < 30 (%)')
        ax2.set_ylabel('SPX')
        ax2.legend(loc='upper left')

        ax2_twin = ax2.twinx()
        ax2_twin.plot(rsi_below_30_percent.index, rsi_below_30_percent, label='RSI < 30 (%)', color='green')
        ax2_twin.set_ylabel('RSI < 30 (%)')
        ax2_twin.legend(loc='upper right')

        fig.tight_layout()
        plt.show()
    else:
        fig, axs = plt.subplots(2, 2, figsize=(15, 10), sharex=True)
        
        axs[0, 0].plot(spx_data.index, spx_data['Close'], label='SPX', color='blue')
        axs[0, 0].set_title('SPX')
        axs[0, 0].set_ylabel('SPX')
        axs[0, 0].legend(loc='upper left')

        axs[0, 1].plot(spx_data.index, spx_data['Close'], label='SPX', color='blue')
        axs[0, 1].set_title('SPX')
        axs[0, 1].set_ylabel('SPX')
        axs[0, 1].legend(loc='upper left')

        axs[1, 0].plot(rsi_above_70_percent.index, rsi_above_70_percent, label='RSI > 70 (%)', color='red')
        axs[1, 0].set_title('RSI > 70 (%)')
        axs[1, 0].set_ylabel('RSI > 70 (%)')
        axs[1, 0].legend(loc='upper left')

        axs[1, 1].plot(rsi_below_30_percent.index, rsi_below_30_percent, label='RSI < 30 (%)', color='green')
        axs[1, 1].set_title('RSI < 30 (%)')
        axs[1, 1].set_ylabel('RSI < 30 (%)')
        axs[1, 1].legend(loc='upper left')

        fig.tight_layout()
        plt.show()

def plot_average_rsi(spx_data, avg_rsi_values):
    avg_rsi_ma = avg_rsi_values.rolling(window=21).mean()

    fig, ax1 = plt.subplots(figsize=(15, 10))

    ax1.plot(spx_data.index, spx_data['Close'], label='SPX', color='blue')
    ax1.set_title('SPX with Average RSI and 21-Day MA')
    ax1.set_ylabel('SPX')
    ax1.legend(loc='upper left')

    ax1_twin = ax1.twinx()
    ax1_twin.plot(avg_rsi_values.index, avg_rsi_values, label='Average RSI', color='orange')
    ax1_twin.plot(avg_rsi_ma.index, avg_rsi_ma, label='21-Day MA of Average RSI', color='purple')
    ax1_twin.set_ylabel('Average RSI')
    ax1_twin.legend(loc='upper right')

    fig.tight_layout()
    plt.show()

# Fetch S&P 500 symbols
sp500_symbols = get_sp500_symbols()

# User-defined start year
start_year = int(input("Enter the start year: "))

# Fetch historical data
data_dict = get_historical_data(sp500_symbols, start_year)

# Fetch SPX data
spx_data = yf.download("^GSPC", start=f"{start_year}-01-01", end=pd.Timestamp.today())

# Calculate RSI values
rsi_dict = get_rsi_values(data_dict)

# Calculate RSI percentages
rsi_above_70_percent, rsi_below_30_percent = calculate_rsi_percentages(rsi_dict, spx_data.index)

# Calculate average RSI over time
avg_rsi_values = pd.Series({date: sum(rsi.loc[date] for rsi in rsi_dict.values() if date in rsi.index) / len(rsi_dict) for date in spx_data.index})

# User choice for overlay or separate plot
overlay_choice = input("Would you like to overlay RSI percentages on the SPX chart? (yes/no): ").strip().lower()
overlay = True if overlay_choice == 'yes' else False

# Plot charts
plot_charts(spx_data, rsi_above_70_percent, rsi_below_30_percent, overlay)

# Plot average RSI with moving average
plot_average_rsi(spx_data, avg_rsi_values)
