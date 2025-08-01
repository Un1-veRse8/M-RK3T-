import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def fetch_data(ticker, years_back):
    end_date = pd.Timestamp.today()
    start_date = end_date - pd.DateOffset(years=years_back)
    data = yf.download(ticker, start=start_date, end=end_date)
    return data, start_date.year

def calculate_monthly_returns(data):
    data['Month'] = data.index.month
    data['Year'] = data.index.year
    monthly_returns = data['Adj Close'].resample('M').ffill().pct_change() * 100  # Convert to percentage
    monthly_returns = monthly_returns.reset_index()
    monthly_returns['Month'] = monthly_returns['Date'].dt.month
    monthly_returns['Year'] = monthly_returns['Date'].dt.year
    return monthly_returns

def calculate_cumulative_average_returns(monthly_returns, current_year):
    monthly_avg_returns = monthly_returns.groupby(['Month', 'Year'])['Adj Close'].mean().unstack()
    cumulative_avg_returns = monthly_avg_returns.cumsum(axis=0)
    avg_returns = cumulative_avg_returns.mean(axis=1)
    current_year_returns = cumulative_avg_returns[current_year]
    return avg_returns, current_year_returns

def plot_seasonality(avg_returns, current_year_returns, current_year, start_year):
    plt.figure(figsize=(10, 6))
    plt.plot(avg_returns.index, avg_returns.values, label=f'Average Returns Since {start_year}')
    plt.plot(current_year_returns.index, current_year_returns.values, label=f'{current_year} Returns')
    plt.xlabel('Month')
    plt.ylabel('Cumulative Average Return (%)')
    plt.title(f'Seasonality Chart for SPX (^GSPC) - {start_year} to {current_year}')
    plt.legend()
    plt.grid(True)
    plt.xticks(ticks=range(1, 13), labels=[
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    
    # Set y-axis ticks to increment by 1
    max_y = max(avg_returns.max(), current_year_returns.max())
    plt.yticks(range(0, int(max_y) + 2, 1))

    # Add watermark
    plt.text(0.5, 0.5, '@o5341V', fontsize=50, color='gray', ha='center', va='center', alpha=0.5, transform=plt.gca().transAxes)

    plt.show()

def main():
    ticker = "^GSPC"
    years_back = int(input("Enter the number of years to look back: "))
    current_year = pd.Timestamp.today().year

    data, start_year = fetch_data(ticker, years_back)
    monthly_returns = calculate_monthly_returns(data)
    avg_returns, current_year_returns = calculate_cumulative_average_returns(monthly_returns, current_year)
    plot_seasonality(avg_returns, current_year_returns, current_year, start_year)

if __name__ == "__main__":
    main()
