# -----------------------------------------------------------------------------
# Dhan API Client
# -----------------------------------------------------------------------------
# This module will contain all the functions to interact with the Dhan API.
# - Connecting to the API
# - Fetching historical data
# - Fetching options chain data
# - Placing and managing orders (if needed in the future)
# -----------------------------------------------------------------------------

from dhanhq import dhanhq
import pandas as pd
import config

def get_dhan_client():
    """
    Initializes and returns a Dhan API client instance.

    Returns:
        dhanhq: An instance of the Dhan API client.
    """
    client = dhanhq(config.DHAN_CLIENT_ID, config.DHAN_ACCESS_TOKEN)
    print("Dhan API client initialized successfully.")
    return client

def get_historical_data(client, symbol, exchange_segment, instrument_type, from_date, to_date):
    """
    Fetches historical intraday data for a given stock.

    Args:
        client: The Dhan API client instance.
        symbol (str): The stock trading symbol (e.g., "RELIANCE").
        exchange_segment (str): The exchange segment (e.g., "NSE_EQ").
        instrument_type (str): The instrument type (e.g., "EQUITY").
        from_date (str): The start date in 'YYYY-MM-DD' format.
        to_date (str): The end date in 'YYYY-MM-DD' format.

    Returns:
        pandas.DataFrame: A DataFrame with OHLCV data, or None if an error occurs.
    """
    # In a real implementation, we would need a robust way to map
    # symbol to security_id. For now, we'll need to assume a mapping exists.
    # This is a placeholder for that logic.
    # security_id = get_security_id_for_symbol(symbol)
    security_id = "1333" # Placeholder for INFY

    print(f"Fetching 60-minute data for {symbol} (ID: {security_id})...")

    # The API returns data in 90-day chunks. We'll need to loop if the date range is larger.
    # This is a simplified implementation for a single chunk.
    try:
        # NOTE: The correct function name for the /charts/intraday endpoint
        # appears to be intraday_minute_data.
        response = client.intraday_minute_data(
            security_id=security_id,
            exchange_segment=exchange_segment,
            instrument_type=instrument_type,
            interval=60, # Fetch 60-minute data
            from_date=from_date,
            to_date=to_date
        )

        if response.get('status') == 'success':
            data = response['data']
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['start_Time'])
            df = df.set_index('date')
            print(f"Successfully fetched {len(df)} data points.")
            return df
        else:
            print(f"Error fetching data for {symbol}: {response.get('remarks')}")
            return None

    except Exception as e:
        print(f"An exception occurred while fetching data for {symbol}: {e}")
        return None


def resample_to_4h(df_1h):
    """
    Resamples 1-hour OHLCV data to 4-hour candles.

    Args:
        df_1h (pandas.DataFrame): A DataFrame with 1-hour data.

    Returns:
        pandas.DataFrame: A DataFrame with 4-hour data.
    """
    if df_1h is None or df_1h.empty:
        return None

    print("Resampling 1H data to 4H...")

    resampling_rules = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }

    df_4h = df_1h.resample('4h', origin='start_day').apply(resampling_rules).dropna()
    print(f"Resampling complete. {len(df_4h)} 4H candles created.")
    return df_4h


# def get_option_chain(client, symbol, exchange_segment):
#     """
#     [DEFERRED] Fetches the option chain for the nearest expiry of a given stock.
#     NOTE: This feature is deferred as the correct library function names could not be determined.
#     """
#     # Placeholder for security ID mapping
#     security_id = "1333" # Placeholder for INFY
#     print(f"\nFetching option chain for {symbol} (ID: {security_id})...")
#
#     try:
#         # This is where the call to get the expiry list would go.
#         # Example: expiry_response = client.get_expiries(...)
#
#         # This is where the call to get the option chain would go.
#         # Example: oc_response = client.get_option_chain(...)
#
#         print("Option chain fetching is currently disabled.")
#         return None
#
#     except Exception as e:
#         print(f"An exception occurred while fetching option chain for {symbol}: {e}")
#         return None
