import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def fetch_data(ticker, start_year):
    end_date = pd.Timestamp.today()
    start_date = pd.Timestamp(f'{start_year}-01-01')
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

def calculate_yearly_returns(data):
    data['Year'] = data.index.year
    yearly_returns = data['Adj Close'].resample('Y').ffill().pct_change() * 100  # Convert to percentage
    yearly_returns = yearly_returns.reset_index()
    yearly_returns['Year'] = yearly_returns['Date'].dt.year
    yearly_returns = yearly_returns.dropna()  # Drop NA values which result from pct_change
    return yearly_returns

def assign_presidential_years(data):
    # Assigning the presidential cycle years assuming 2024 is an election year
    data['Presidential Year'] = (data['Year'] - 2024) % 4
    data['Presidential Year'] = data['Presidential Year'].replace({
        0: 'Election Year', 
        1: 'Year 1 in Office', 
        2: 'Year 2 in Office', 
        3: 'Pre-Election Year'
    })
    return data

def calculate_cumulative_returns(data):
    # Calculating the cumulative returns correctly
    data['Return'] = data['Adj Close']
    data['Cumulative Return'] = data.groupby('Presidential Year')['Return'].cumsum()
    return data

def plot_presidential_seasonality(data):
    plt.figure(figsize=(14, 8))
    colors = {'Election Year': 'red', 'Year 1 in Office': 'green', 'Year 2 in Office': 'blue', 'Pre-Election Year': 'yellow'}
    for label, color in colors.items():
        subset = data[data['Presidential Year'] == label]
        plt.plot(subset['Year'], subset['Cumulative Return'], label=label, color=color)
    plt.xlabel('Year')
    plt.ylabel('Cumulative Return (%)')
    plt.title('Cumulative Returns Over Time by Presidential Cycle Year')
    plt.legend()
    plt.grid(True)

    # Add watermark
    plt.text(0.5, 0.5, '@o5341V', fontsize=50, color='gray', ha='center', va='center', alpha=0.5, transform=plt.gca().transAxes)

    plt.show()

def main():
    ticker = "^GSPC"
    start_year = 1920  # Fetch data starting from 1920
    data = fetch_data(ticker, start_year)
    yearly_returns = calculate_yearly_returns(data)
    yearly_returns = assign_presidential_years(yearly_returns)
    cumulative_returns = calculate_cumulative_returns(yearly_returns)
    
    plot_presidential_seasonality(cumulative_returns)

if __name__ == "__main__":
    main()
