import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

# Cache directory for offline mode
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
    # Ensure the cache directory exists
    os.makedirs(CACHE_DIR, exist_ok=True)

    # Define the cache file path
    cache_file = os.path.join(CACHE_DIR, f"{series_id}.csv")

    # Check if data is cached
    if os.path.exists(cache_file):
        df = pd.read_csv(cache_file, parse_dates=['date'])
        print(f"Loaded data from cache for series: {series_id}")
        
        # Filter data based on start date
        if start_date:
            df = df[df['date'] >= start_date]
        return df

    # Fetch data from FRED API
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

    # Create DataFrame
    df = pd.DataFrame(data['observations'])
    df = df[['date', 'value']]
    df['value'] = pd.to_numeric(df['value'], errors='coerce')

    # Save to cache
    df.to_csv(cache_file, index=False)
    print(f"Fetched data from API and saved to cache for series: {series_id}")

    #C:\Users\User\.fred_cache

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

if __name__ == "__main__":
    FRED_API_KEY = "2799e7146b69c660e478eaaf3b3750a6"  # Replace with your FRED API key

    print("Welcome to the FRED Data Fetcher with Offline Mode!")
    offline_mode = input("Enable offline mode? (yes/no): ").strip().lower() == 'yes'

    series_id = input("Enter the FRED Series ID to fetch data: ").strip()
    start_date = input("Enter the start date (YYYY-MM-DD, press Enter to skip): ").strip()

    if not start_date:
        start_date = None

    try:
        if offline_mode:
            print("Offline mode enabled. Checking for cached data...")
        series_data = fetch_fred_data_with_cache(FRED_API_KEY, series_id, start_date)

        # Display data preview
        print(series_data.head())

        save_data = input("Would you like to save the data to a CSV file? (yes/no): ").strip().lower()
        if save_data == 'yes':
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            output_file = os.path.join(desktop_path, f"{series_id}_data.csv")
            series_data.to_csv(output_file, index=False)
            print(f"Data saved to {output_file}")

        plot_series(series_data, series_id)
    except Exception as e:
        print(f"Error fetching or plotting data: {e}")
