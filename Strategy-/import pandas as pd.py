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

def fetch_series_from_category(api_key, category_id):
    """
    Fetch all series under a specific category ID.

    Parameters:
    api_key (str): Your FRED API key.
    category_id (int): The category ID to fetch series from.

    Returns:
    list: A list of series dictionaries.
    """
    base_url = "https://api.stlouisfed.org/fred/category/series"
    params = {
        'api_key': api_key,
        'category_id': category_id,
        'file_type': 'json',
        'limit': 1000,
        'offset': 0
    }

    all_series = []

    while True:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if 'seriess' not in data:
            break

        all_series.extend(data['seriess'])

        if len(data['seriess']) < params['limit']:
            break

        params['offset'] += params['limit']

    return all_series

def fetch_all_series(api_key):
    """
    Recursively fetch all FRED series IDs and descriptions from all categories.

    Parameters:
    api_key (str): Your FRED API key.

    Returns:
    pandas.DataFrame: A DataFrame containing all FRED series IDs and descriptions.
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
        raise ValueError("No categories found in the response.")

    all_series = []

    def fetch_recursively(category_id):
        # Fetch series for the current category
        series = fetch_series_from_category(api_key, category_id)
        all_series.extend(series)

        # Fetch subcategories
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

    # Start recursive fetching from the root category
    fetch_recursively(0)

    return pd.DataFrame(all_series)

def fetch_fred_data(api_key, series_id, start_date=None):
    """
    Fetch data for a specific FRED series ID.

    Parameters:
    api_key (str): Your FRED API key.
    series_id (str): The series ID to fetch.
    start_date (str): Start date in YYYY-MM-DD format (optional).

    Returns:
    pandas.DataFrame: DataFrame containing the date and value of the series.
    """
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

    print("Welcome to the FRED Data Fetcher and Plotter!")
    download_all = input("Would you like to download all available FRED series IDs? Please know this can take a VERY long time. (yes/no): ").strip().lower()

    if download_all == 'yes':
        print("Fetching all available FRED series IDs...")
        try:
            all_series_df = fetch_all_series(FRED_API_KEY)
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            all_series_file = os.path.join(desktop_path, "FRED_All_Series.csv")
            all_series_df.to_csv(all_series_file, index=False)
            print(f"All series IDs saved to {all_series_file}")
        except Exception as e:
            print(f"Error fetching all series IDs: {e}")

    search_choice = input("Would you like to search by category or use your own Series ID? (category/custom): ").strip().lower()

    if search_choice == 'category':
        print("Select a category to explore Top FRED Series IDs:")
        for i, category in enumerate(CATEGORIES.keys(), start=1):
            print(f"{i}. {category}")

        category_choice = int(input("Enter the number of the category you want to explore: "))
        selected_category = list(CATEGORIES.keys())[category_choice - 1]

        print(f"You selected: {selected_category}")
        print("Top Series IDs in this category:")
        for series_id, description in CATEGORIES[selected_category].items():
            print(f"- {series_id}: {description}")

        series_id = input("Enter the FRED Series ID to fetch data: ").strip()
    else:
        series_id = input("Enter the FRED Series ID to fetch data: ").strip()

    start_date = input("Enter the start date (YYYY-MM-DD, press Enter to skip): ").strip()

    if not start_date:
        start_date = None

    try:
        print(f"Fetching data for series ID: {series_id}...")
        series_data = fetch_fred_data(FRED_API_KEY, series_id, start_date)
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
