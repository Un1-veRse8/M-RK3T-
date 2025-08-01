import pandas as pd
import matplotlib.pyplot as plt
import requests

def fetch_fred_data(series_id, start_date, api_key):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&observation_start={start_date}&api_key={api_key}&file_type=json"
    response = requests.get(url)
    data = response.json()
    return pd.DataFrame(data['observations'])

def calculate_monthly_returns(df, date_column, value_column):
    df[date_column] = pd.to_datetime(df[date_column])
    df['Month'] = df[date_column].dt.month
    df['Year'] = df[date_column].dt.year
    df.set_index(date_column, inplace=True)
    df[value_column] = pd.to_numeric(df[value_column], errors='coerce')
    monthly_returns = df[value_column].resample('MS').ffill().pct_change()
    return monthly_returns

def plot_seasonality(year_ranges, series_id, api_key):
    plt.figure(figsize=(15, 10))
    
    for i, (start_year, end_year) in enumerate(year_ranges):
        start_date = f"{start_year}-01-01"
        
        df = fetch_fred_data(series_id, start_date, api_key)
        
        if df.empty:
            print(f"No data available for the range starting {start_year}")
            continue
        
        end_date = df['date'].max()[:10]  # Get the last available date
        end_year = pd.to_datetime(end_date).year
        
        monthly_returns = calculate_monthly_returns(df, 'date', 'value')
        
        monthly_avg_returns = monthly_returns.groupby(monthly_returns.index.month).mean()
        overall_avg_return = monthly_returns.mean()
        
        ax = plt.subplot(len(year_ranges), 1, i + 1)
        monthly_avg_returns.plot(ax=ax, marker='o', linestyle='-', label=f'{start_year}-{end_year}')
        ax.axhline(y=overall_avg_return, color='r', linestyle='--', label='Overall Avg Return')
        ax.set_title(f'Average Monthly Returns ({start_year}-{end_year})')
        ax.set_xlabel('Month')
        ax.set_ylabel('Average Return')
        ax.legend()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Prompt the user for input
    api_key = '2799e7146b69c660e478eaaf3b3750a6'
    series_id = 'SP500'  # Example series ID for S&P 500
    year_ranges = []
    
    while True:
        start_year = input("Enter the start year for the range (or 'done' to finish): ")
        if start_year.lower() == 'done':
            break
        year_ranges.append((int(start_year), None))
    
    if year_ranges:
        plot_seasonality(year_ranges, series_id, api_key)
