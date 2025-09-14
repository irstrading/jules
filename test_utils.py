# -----------------------------------------------------------------------------
# Test Utilities
# -----------------------------------------------------------------------------
# This module contains helper functions for testing the scanner,
# primarily by generating mock data.
# -----------------------------------------------------------------------------

import pandas as pd
import numpy as np

def create_mock_dataframe(days=250):
    """
    Generates a mock pandas DataFrame with OHLCV data for testing.

    Args:
        days (int): The number of days (bars) to generate.

    Returns:
        pandas.DataFrame: A DataFrame with sample data.
    """
    print(f"Generating {days} bars of mock OHLCV data...")
    dates = pd.to_datetime(pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D'))

    # Create a base price series with some trend and noise
    price = (np.sin(np.linspace(0, 10, days)) * 20 +
             np.linspace(0, 50, days) +  # Upward trend
             np.random.normal(0, 2, days) + 150) # Noise and base price

    data = {
        'open': price + np.random.normal(0, 1, days),
        'high': price + np.abs(np.random.normal(0, 2, days)) + 2,
        'low': price - np.abs(np.random.normal(0, 2, days)) - 2,
        'close': price,
        'volume': np.random.randint(100000, 5000000, days)
    }

    df = pd.DataFrame(data, index=dates)

    # Ensure OHLC integrity
    df['high'] = df[['high', 'open', 'close']].max(axis=1)
    df['low'] = df[['low', 'open', 'close']].min(axis=1)

    print("Mock data generated.")
    return df
