import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".fred_cache")


def fetch_fred_data_with_cache(api_key, series_id, start_date=None):
    """
    Fetch data for a FRED series with caching.

    Parameters:
    api_key (str): Your FRED API key.
    series_id (str): The series ID to fetch.
    start_date (str): Start date in YYYY-MM-DD format (optional).

    Returns:
    pandas.DataFrame: DataFrame containing the date and value of the series.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{series_id}.csv")

    if os.path.exists(cache_file):
        df = pd.read_csv(cache_file, parse_dates=['date'])
        print(f"Loaded data from cache for series: {series_id}")
        if start_date:
            df = df[df['date'] >= start_date]
        return df

    base_url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        'api_key': api_key,
        'series_id': series_id,
        'file_type': 'json'
    }
    if start_date:
        params['observation_start'] = start_date

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()

    if 'observations' not in data:
        raise ValueError("No observations found in the response.")

    df = pd.DataFrame(data['observations'])
    df = df[['date', 'value']]
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df.to_csv(cache_file, index=False)
    print(f"Fetched data from API and saved to cache for series: {series_id}")

    return df


def plot_series(df, series_id):
    """
    Plot a FRED series.

    Parameters:
    df (pandas.DataFrame): DataFrame containing the data to plot.
    series_id (str): The series ID (used for labeling).
    """
    plt.figure(figsize=(10, 6))
    plt.plot(pd.to_datetime(df['date']), df['value'], label=series_id)
    plt.title(f"{series_id} Time Series")
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()


def plot_dual_axis(df1, series_id1, df2, series_id2):
    """
    Plot two series with different scales on the same graph using dual axes.

    Parameters:
    df1 (pandas.DataFrame): DataFrame containing the first series data.
    series_id1 (str): The series ID for the first series.
    df2 (pandas.DataFrame): DataFrame containing the second series data.
    series_id2 (str): The series ID for the second series.
    """
    # Align the data by date
    common_dates = set(df1['date']).intersection(set(df2['date']))
    df1 = df1[df1['date'].isin(common_dates)].sort_values('date')
    df2 = df2[df2['date'].isin(common_dates)].sort_values('date')

    # Convert 'date' column to datetime
    df1['date'] = pd.to_datetime(df1['date'])
    df2['date'] = pd.to_datetime(df2['date'])

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # First series
    ax1.plot(df1['date'], df1['value'], color='blue', label=series_id1)
    ax1.set_xlabel("Date")
    ax1.set_ylabel(f"{series_id1} Value", color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid()

    # Second series
    ax2 = ax1.twinx()  # Instantiate a second y-axis that shares the same x-axis
    ax2.plot(df2['date'], df2['value'], color='orange', label=series_id2)
    ax2.set_ylabel(f"{series_id2} Value", color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')

    # Title and legends
    fig.suptitle(f"Comparison of {series_id1} and {series_id2}")
    fig.tight_layout()  # Adjust layout to prevent overlap
    plt.show()


if __name__ == "__main__":
    FRED_API_KEY = "2799e7146b69c660e478eaaf3b3750a6"  # Replace with your FRED API key

    print("Welcome to the Enhanced FRED Data Fetcher!")
    series_id = input("Enter the primary FRED Series ID to fetch data: ").strip()
    start_date = input("Enter the start date (YYYY-MM-DD, press Enter to skip): ").strip()
    if not start_date:
        start_date = None

    try:
        # Fetch and plot the primary series
        series_data = fetch_fred_data_with_cache(FRED_API_KEY, series_id, start_date)
        plot_series(series_data, series_id)

        # Prompt for dual-axis plotting
        if input("Would you like to compare this series with another series using a dual-axis plot? (yes/no): ").strip().lower() == 'yes':
            second_series_id = input("Enter the second FRED Series ID to compare: ").strip()
            second_series_data = fetch_fred_data_with_cache(FRED_API_KEY, second_series_id, start_date)
            plot_dual_axis(series_data, series_id, second_series_data, second_series_id)

        print("Process completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
