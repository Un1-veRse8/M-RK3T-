import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

CATEGORIES = {
    "Money, Banking, and Finance": {
        "GDP": "Gross Domestic Product",
        "M1SL": "M1 Money Stock",
        "M2SL": "M2 Money Stock",
        "FEDFUNDS": "Effective Federal Funds Rate",
        "DGS10": "10-Year Treasury Constant Maturity Rate",
        "BAA10YM": "Moody's Seasoned Baa Corporate Bond Yield Relative to Yield on 10-Year Treasury Constant Maturity",
        "PAYEMS": "Total Nonfarm Payrolls",
        "TOTRESNS": "Total Reserves of Depository Institutions",
        "NONBORRES": "Reserves of Depository Institutions Non-Borrowed",
        "HHMSDODNS": "Household Debt Service Payments",
        "MORTGAGE30US": "30-Year Fixed Mortgage Rate",
        "BUSLOANS": "Commercial and Industrial Loans",
        "REALLN": "Real Estate Loans",
        "CONSUMERLN": "Consumer Loans",
        "DTB3": "3-Month Treasury Bill Rate",
        "NCBMTYO": "Net Commercial Bank Loans to Manufacturing",
        "DEXUSEU": "U.S. / Euro Exchange Rate",
        "DEXJPUS": "U.S. / Japanese Yen Exchange Rate",
        "DEXCHUS": "U.S. / Chinese Yuan Exchange Rate",
        "DTWEXBGS": "Trade Weighted U.S. Dollar Index: Broad Goods",
        "EXUSUK": "Exchange Rate of USD to GBP",
        "EXUSCA": "Exchange Rate of USD to CAD",
        "HOUST": "Housing Starts",
        "SP500": "S&P 500 Index"
    },
    "Population, Employment, and Labor Markets": {
        "UNRATE": "Unemployment Rate",
        "CPIAUCSL": "Consumer Price Index for All Urban Consumers",
        "ICSA": "Initial Claims for Unemployment Insurance",
        "LNS14000000": "Labor Force Participation Rate",
        "PAYEMS": "Total Nonfarm Payrolls",
        "CES0500000003": "Average Weekly Hours of All Employees",
        "HSN1F": "New One-Family Houses Sold",
        "PERMIT": "Building Permits",
        "RSAFS": "Advance Retail Sales",
        "W875RX1": "Personal Savings Rate",
        "IR": "Industrial Production Index",
        "CES0500000001": "Average Hourly Earnings of Production Workers",
        "DFF": "Discount Rate",
        "EXUSJP": "Exchange Rate of USD to JPY",
        "HSN1F": "New Home Sales",
        "EXUSCA": "Exchange Rate of USD to CAD",
        "CES2000000008": "Labor Force Underemployment Rate",
        "HOUST": "Housing Starts",
        "CPIU": "Urban CPI",
        "PERMIT": "Permits for Building",
        "EXUSSG": "USD to Singapore Dollar",
        "SP500": "S&P 500",
        "HHMSDODNS": "Household Debt Service Payments"  
    },
    "Production and Business Activity": {
        "INDPRO": "Industrial Production Index",
        "IPMAN": "Industrial Production: Manufacturing",
        "MCUMFN": "Capacity Utilization: Manufacturing",
        "AWHMAN": "Average Weekly Hours: Manufacturing",
        "AWOTMAN": "Average Overtime Hours: Manufacturing",
        "MANEMP": "All Employees: Manufacturing",
        "PERMIT": "Building Permits",
        "HOUST": "Housing Starts",
        "RSAFS": "Advance Retail Sales",
        "UMCSENT": "University of Michigan Consumer Sentiment Index",
        "TOTALSA": "Total Vehicle Sales",
        "BUSINV": "Business Inventories",
        "WHLSL": "Wholesale Sales",
        "RETAIL": "Retail Trade",
        "SREV": "State Revenue Data",
        "HBR": "Home Buyer Readings",
        "DEXCNUS": "USD to Chinese Yuan",
        "HOUINV": "Housing Inventory"
    },
    "Prices": {
        "CPIAUCSL": "Consumer Price Index for All Urban Consumers",
        "CPILFESL": "Consumer Price Index for All Urban Consumers: Less Food and Energy",
        "WPSFD49207": "Producer Price Index by Commodity: Final Demand",
        "PCEDG": "Personal Consumption Expenditures: Durable Goods",
        "PCEPIL": "Personal Consumption Expenditures Price Index",
        "CUSR0000SA0L2": "CPI Less Shelter",
        "CUUR0000SA0L2": "CPI Less Food",
        "CUUR0000SETA01": "Consumer Prices for Urban Consumers",
        "DEFLATOR": "GDP Deflator",
        "EXPORT": "Export Price Index",
        "IMPORT": "Import Price Index",
        "PPIID": "Producer Price Index",
        "HPI": "Housing Price Index",
        "RENT": "Housing Rentals",
        "FOODIND": "Food CPI Growth Rates"
    },
    "National Accounts": {
        "GDP": "Gross Domestic Product",
        "GNP": "Gross National Product",
        "NIPA": "National Income and Product Accounts",
        "DISPOS": "Disposable Personal Income",
        "PI": "Personal Income",
        "SALES": "Retail Sales",
        "INVENT": "Business Inventories",
        "GDPDEF": "GDP Deflator",
        "NETEXP": "Net Exports",
        "GOVTEX": "Government Expenditures",
        "CONSUMP": "Personal Consumption Expenditures",
        "INVEST": "Gross Private Domestic Investment",
        "EXPEND": "Total Expenditures",
        "PRICES": "Aggregate Price Indices",
        "LABCOMP": "Labor Compensation",
        "CORPPR": "Corporate Profits",
        "CIVPART": "Civilian Labor Force Participation Rate"
    },
    "Regional Data": {
        "HOUST": "Housing Starts",
        "BLIN": "Building Permits",
        "POP": "Population Growth",
        "JOBS": "Regional Employment",
        "UNEMP": "Regional Unemployment Rate",
        "MEDINC": "Median Income by State",
        "HPI": "Home Price Index",
        "SALES": "Retail Sales by State",
        "RENT": "Rent Prices",
        "CONSTR": "Construction Employment",
        "REV": "Regional Government Revenue",
        "EXP": "Regional Government Expenditures",
        "TAXES": "Tax Revenue by State",
        "FORECLOS": "Foreclosure Rates",
        "MANUF": "Regional Manufacturing Output",
        "TRADE": "Regional Trade Volumes",
        "MIGR": "Migration Patterns",
        "UTIL": "Utility Prices",
        "INFRA": "Infrastructure Spending"
    },
    "U.S. Trade and International Transactions": {
        "NETEXP": "Net Exports of Goods and Services",
        "IMP": "U.S. Imports",
        "EXP": "U.S. Exports",
        "BALANCE": "Trade Balance",
        "SERVEXP": "Services Exports",
        "SERVIMP": "Services Imports",
        "FOREIGN": "Foreign Investment in the U.S.",
        "USINV": "U.S. Investment Abroad",
        "FPI": "Foreign Portfolio Investment",
        "REM": "Remittances",
        "EXRATE": "Exchange Rates",
        "GOLD": "Gold Reserves",
        "OIL": "Oil Exports and Imports",
        "TECH": "Technology Trade",
        "TRAVEL": "Travel and Tourism Receipts",
        "DEFTRADE": "Defense Trade",
        "TEXTILES": "Textile Exports and Imports",
        "AUTO": "Automotive Trade",
        "AGRI": "Agricultural Trade",
        "PHARMA": "Pharmaceutical Trade"
    },
    "Academic Data": {
        "ENROLL": "School Enrollment Statistics",
        "DEBT": "Student Loan Debt",
        "EDUEXP": "Education Expenditures",
        "R&D": "Research and Development Spending",
        "PUBSCH": "Public School Funding",
        "HIGHGRAD": "High School Graduation Rates",
        "COLLEGE": "College Enrollment Trends",
        "STEM": "STEM Program Enrollment",
        "FACULTY": "Faculty Employment Data",
        "TUIT": "Tuition Costs Trends",
        "SCHOLAR": "Scholarship Disbursements",
        "LOAN": "Student Loan Borrowing Trends",
        "LITRATE": "Literacy Rates",
        "EDUTEST": "Education Testing Statistics",
        "DROPOUT": "Dropout Rates",
        "POSTGRAD": "Postgraduate Education Trends",
        "ALUM": "Alumni Donation Trends",
        "EDUCAP": "Education Capital Spending",
        "CHARTER": "Charter School Enrollment",
        "ONLINE": "Online Education Participation"
    }
}

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".fred_cache")


def fetch_fred_data_with_cache(api_key, series_id, start_date=None, offline_mode=False):
    """
    Fetch data for a FRED series with caching and optional offline mode.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{series_id}.csv")

    if os.path.exists(cache_file):
        df = pd.read_csv(cache_file, parse_dates=['date'])
        print(f"Loaded data from cache for series: {series_id}")
        if start_date:
            df = df[df['date'] >= start_date]
        return df

    if offline_mode:
        print(f"No cached data available for series: {series_id}. Please switch to online mode to fetch data.")
        return None

    base_url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        'api_key': api_key,
        'series_id': series_id,
        'file_type': 'json'
    }
    if start_date:
        params['observation_start'] = start_date

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if 'observations' not in data:
            print(f"No observations found for series: {series_id}")
            return None

        df = pd.DataFrame(data['observations'])
        df = df[['date', 'value']]
        df['date'] = pd.to_datetime(df['date'])  # Ensure date is parsed correctly
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df.to_csv(cache_file, index=False)
        print(f"Fetched data from API and saved to cache for series: {series_id}")

        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for series: {series_id}. Please check if the series ID is valid. Details: {e}")
        return None


def fetch_all_series(api_key):
    """
    Fetch all available FRED series IDs and save them to a CSV file.
    """
    base_url = "https://api.stlouisfed.org/fred/category/children"
    params = {
        'api_key': api_key,
        'category_id': 0,  # Root category ID
        'file_type': 'json'
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()

    if 'categories' not in data:
        print("No categories found in the response.")
        return None

    all_series = []
    base_url_series = "https://api.stlouisfed.org/fred/category/series"

    def fetch_recursively(category_id):
        params_series = {
            'api_key': api_key,
            'category_id': category_id,
            'file_type': 'json'
        }
        response_series = requests.get(base_url_series, params=params_series)
        response_series.raise_for_status()
        data_series = response_series.json()
        if 'seriess' in data_series:
            all_series.extend(data_series['seriess'])

        # Fetch subcategories recursively
        subcategory_params = {
            'api_key': api_key,
            'category_id': category_id,
            'file_type': 'json'
        }
        subcategory_response = requests.get(base_url, params=subcategory_params)
        subcategory_response.raise_for_status()
        subcategory_data = subcategory_response.json()

        if 'categories' in subcategory_data:
            for subcategory in subcategory_data['categories']:
                fetch_recursively(subcategory['id'])

    fetch_recursively(0)

    df = pd.DataFrame(all_series)
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_file = os.path.join(desktop_path, "FRED_All_Series.csv")
    df.to_csv(output_file, index=False)
    print(f"All FRED series IDs saved to {output_file}")


def apply_moving_average(df, window_size):
    """
    Apply a moving average to a DataFrame.
    """
    df['value'] = df['value'].rolling(window=window_size).mean()
    return df


def calculate_correlation(df1, df2):
    """
    Calculate and display the correlation between two series.
    """
    correlation = df1['value'].corr(df2['value'])
    print(f"\nCorrelation between the two series: {correlation:.4f}")
    return correlation


def plot_single_series(df, series_id):
    """
    Plot a single FRED series.
    """
    if df is None or df.empty:
        print(f"No data available to plot for series: {series_id}")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['value'], label=series_id, color='blue')
    plt.title(f"{series_id} Time Series")
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()


def plot_dual_axis_with_no_overlap(df1, series_id1, df2, series_id2):
    """
    Plot two series with different scales on the same graph using dual axes,
    even if their dates don't overlap.
    """
    # Ensure the datasets have valid datetime columns
    df1['date'] = pd.to_datetime(df1['date'], errors='coerce')
    df2['date'] = pd.to_datetime(df2['date'], errors='coerce')

    # Check for overlapping dates
    common_dates = set(df1['date']).intersection(set(df2['date']))

    if not common_dates:
        print(f"Warning: No overlapping dates between the two series ({series_id1} and {series_id2}). "
              f"Both series will be plotted with their own intervals.")

    # Plot the datasets
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(df1['date'], df1['value'], color='blue', label=series_id1)
    ax1.set_xlabel("Date")
    ax1.set_ylabel(f"{series_id1} Value", color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(which='major', linestyle='-', linewidth=0.5, alpha=0.7)

    ax2 = ax1.twinx()
    ax2.plot(df2['date'], df2['value'], color='orange', label=series_id2)
    ax2.set_ylabel(f"{series_id2} Value", color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')

    # Add title indicating overlap or not
    if not common_dates:
        fig.suptitle(f"Comparison of {series_id1} and {series_id2} (Non-Overlapping Intervals)")
    else:
        fig.suptitle(f"Comparison of {series_id1} and {series_id2}")

    # Format x-axis for better readability
    import matplotlib.dates as mdates
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    FRED_API_KEY = "2799e7146b69c660e478eaaf3b3750a6"  # Replace with your FRED API key

    print("Welcome to the Enhanced FRED Data Fetcher!")
    offline_mode = input("Do you want to use offline mode? (yes/no): ").strip().lower() == 'yes'

    # Option to download all FRED series IDs
    if not offline_mode and input("Would you like to download all available FRED series IDs? This may take a VERY long time. (yes/no): ").strip().lower() == "yes":
        fetch_all_series(FRED_API_KEY)
        exit()

    # Fetch the first series
    series_id1 = input("Enter the first FRED Series ID to fetch data: ").strip()
    start_date = input("Enter the start date (YYYY-MM-DD, press Enter to skip): ").strip()
    if not start_date:
        start_date = None

    df1 = fetch_fred_data_with_cache(FRED_API_KEY, series_id1, start_date, offline_mode)
    if df1 is None:
        print(f"No data available for series: {series_id1}. Exiting.")
        exit()

    if input("Would you like to apply a moving average to this series? (yes/no): ").strip().lower() == 'yes':
        window_size = int(input("Enter the moving average window size (e.g., 12 for monthly): ").strip())
        df1 = apply_moving_average(df1, window_size)

    # Fetch and compare the second series if required
    if input("Would you like to compare this series with another series using a dual-axis plot? (yes/no): ").strip().lower() == "yes":
        series_id2 = input("Enter the second FRED Series ID to fetch data: ").strip()
        df2 = fetch_fred_data_with_cache(FRED_API_KEY, series_id2, start_date, offline_mode)
        if df2 is None:
            print(f"No data available for series: {series_id2}. Exiting.")
            exit()

        if input("Would you like to apply a moving average to this series? (yes/no): ").strip().lower() == 'yes':
            window_size = int(input("Enter the moving average window size (e.g., 12 for monthly): ").strip())
            df2 = apply_moving_average(df2, window_size)

        # Optionally calculate correlation
        if input("Would you like to calculate the correlation between these two series? (yes/no): ").strip().lower() == 'yes':
            calculate_correlation(df1, df2)

        plot_dual_axis_with_no_overlap(df1, series_id1, df2, series_id2)
    else:
        plot_single_series(df1, series_id1)
