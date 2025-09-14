# -----------------------------------------------------------------------------
# Indicator and Pattern Analysis
# -----------------------------------------------------------------------------
# This module will contain all the functions to calculate technical indicators
# and identify the patterns we're looking for.
#
# - Bollinger Band Squeeze
# - Keltner Channel Squeeze
# - Volatility Contraction Pattern (VCP)
# - Volume Price Analysis (VPA) signals (e.g., No Supply)
# - Options-based metrics (e.g., Put-Call Ratio)
# -----------------------------------------------------------------------------

import pandas as pd
import numpy as np

def calculate_atr(df, period=14):
    """Calculates the Average True Range (ATR)."""
    df['high-low'] = df['high'] - df['low']
    df['high-prev_close'] = np.abs(df['high'] - df['close'].shift(1))
    df['low-prev_close'] = np.abs(df['low'] - df['close'].shift(1))
    df['true_range'] = df[['high-low', 'high-prev_close', 'low-prev_close']].max(axis=1)
    df['atr'] = df['true_range'].ewm(alpha=1/period, adjust=False).mean()
    return df

def detect_squeeze(df, bb_period=20, bb_std_dev=2.0, kc_period=20, kc_multiplier=1.5):
    """
    Detects a Bollinger Band / Keltner Channel squeeze.

    Args:
        df (pandas.DataFrame): DataFrame with OHLCV data.
        bb_period (int): Lookback period for Bollinger Bands.
        bb_std_dev (float): Standard deviation for Bollinger Bands.
        kc_period (int): Lookback period for Keltner Channels.
        kc_multiplier (float): Multiplier for the Keltner Channels ATR.

    Returns:
        pandas.DataFrame: The original DataFrame with an added 'in_squeeze' column.
    """
    print("Calculating Squeeze indicator...")

    # Bollinger Bands Calculation
    df['sma'] = df['close'].rolling(window=bb_period).mean()
    df['std_dev'] = df['close'].rolling(window=bb_period).std()
    df['bb_upper'] = df['sma'] + (df['std_dev'] * bb_std_dev)
    df['bb_lower'] = df['sma'] - (df['std_dev'] * bb_std_dev)

    # Keltner Channels Calculation
    df = calculate_atr(df, period=kc_period)
    df['kc_ema'] = df['close'].ewm(span=kc_period, adjust=False).mean()
    df['kc_upper'] = df['kc_ema'] + (df['atr'] * kc_multiplier)
    df['kc_lower'] = df['kc_ema'] - (df['atr'] * kc_multiplier)

    # Squeeze Condition
    df['in_squeeze'] = (df['bb_lower'] > df['kc_lower']) & (df['bb_upper'] < df['kc_upper'])

    print("Squeeze calculation complete.")
    return df


def detect_vcp(df, trend_period=200, lookback_period=100):
    """
    Detects a Volatility Contraction Pattern (VCP).
    This is the first stage of the implementation.

    Args:
        df (pandas.DataFrame): DataFrame with OHLCV data.
        trend_period (int): The lookback period for the long-term trend SMA.
        lookback_period (int): The period over which to find the initial high.

    Returns:
        bool: True if the initial VCP conditions are met, False otherwise.
    """
    print("Analyzing for VCP conditions...")

    # 1. Trend Filter: Ensure the stock is in a long-term uptrend.
    df['sma_trend'] = df['close'].rolling(window=trend_period).mean()
    last_close = df['close'].iloc[-1]
    last_sma = df['sma_trend'].iloc[-1]

    if last_close < last_sma:
        print("VCP Check Failed: Stock is not in a long-term uptrend (Close < 200-period SMA).")
        return False

    print("VCP Trend Filter Passed: Stock is in an uptrend.")

    # --- VCP Core Logic ---

    # 2. Find the high point of the base within the lookback period.
    lookback_df = df.iloc[-lookback_period:]
    base_high_price = lookback_df['high'].max()
    base_high_date = lookback_df['high'].idxmax()

    print(f"VCP Base High Found: {base_high_price:.2f} on {base_high_date.date()}")

    # 3. Iteratively find and validate all contractions.
    contractions = []
    current_high_price = base_high_price
    current_high_date = base_high_date
    last_low_price = 0

    for i in range(4): # Look for up to 4 contractions
        data_after_current_high = df[df.index > current_high_date]

        if data_after_current_high.empty:
            break

        # Find the next low point
        next_low_price = data_after_current_high['low'].min()
        next_low_date = data_after_current_high['low'].idxmin()

        # This low must be higher than the last low to be a valid contraction
        if next_low_price < last_low_price:
            break

        depth = ((current_high_price - next_low_price) / current_high_price) * 100

        # Check if the contraction is shallower than the previous one
        if contractions and depth >= contractions[-1]['depth']:
            break

        contractions.append({
            'number': i + 1,
            'depth': depth,
            'low_price': next_low_price,
            'low_date': next_low_date
        })

        last_low_price = next_low_price

        # Find the next high point (must be lower than the current high)
        data_after_low = df[df.index > next_low_date]
        if data_after_low.empty:
            break

        next_high_price = data_after_low['high'].max()
        if next_high_price > current_high_price:
             # This would be a breakout, not a new contraction high
            break

        current_high_price = next_high_price
        current_high_date = data_after_low['high'].idxmax()

    print(f"Found {len(contractions)} contractions.")
    for c in contractions:
        print(f"  - C{c['number']}: {c['depth']:.2f}% deep at {c['low_price']:.2f} on {c['low_date'].date()}")

    # 4. Validate the overall VCP pattern
    if not (2 <= len(contractions) <= 4):
        print("VCP Check Failed: Pattern does not have 2-4 contractions.")
        return False

    if contractions[-1]['depth'] > 10.0:
        print(f"VCP Check Failed: Final contraction is {contractions[-1]['depth']:.2f}%, which is not tight enough (< 10%).")
        return False

    print("VCP Pattern is valid.")
    # In the future, we would also check volume and return the pivot point.
    return True


def analyze_vpa(df, vol_period=50):
    """
    Analyzes volume and price action to find VPA signals.

    Args:
        df (pandas.DataFrame): DataFrame with OHLCV data.
        vol_period (int): The lookback period for the volume SMA.

    Returns:
        pandas.DataFrame: The DataFrame with a 'vpa_signal' column.
    """
    print("Analyzing VPA signals...")
    df['vpa_signal'] = 'none'

    # Calculate average volume
    df['vol_sma'] = df['volume'].rolling(window=vol_period).mean()

    # --- VPA Signal: No Supply ---
    # A down bar on low volume, with a narrow range.
    is_down_bar = df['close'] < df['open']
    is_low_volume = df['volume'] < df['vol_sma'] * 0.75 # Volume is < 75% of average
    is_narrow_range = (df['high'] - df['low']) < (df['atr'] * 0.8) # Range is smaller than average

    no_supply_condition = is_down_bar & is_low_volume & is_narrow_range
    df.loc[no_supply_condition, 'vpa_signal'] = 'No Supply'

    # --- Placeholder for other VPA signals (Stopping Volume, etc.) ---

    print("VPA analysis complete.")
    return df


# def analyze_options_data(option_chain):
#     """
#     [DEFERRED] Analyzes option chain data to calculate PCR and find max OI strikes.
#     NOTE: This feature is deferred as the correct library function names could not be determined.
#     """
#     if not option_chain or 'oc' not in option_chain:
#         return None
#
#     print("Analyzing options data...")
#     total_call_oi = 0
#     total_put_oi = 0
#
#     for strike, data in option_chain['oc'].items():
#         if 'ce' in data and data['ce'] is not None:
#             total_call_oi += data['ce'].get('oi', 0)
#         if 'pe' in data and data['pe'] is not None:
#             total_put_oi += data['pe'].get('oi', 0)
#
#     if total_call_oi == 0: # Avoid division by zero
#         pcr = float('inf')
#     else:
#         pcr = total_put_oi / total_call_oi
#
#     metrics = {
#         'total_call_oi': total_call_oi,
#         'total_put_oi': total_put_oi,
#         'pcr': pcr
#     }
#
#     print(f"Options Analysis Complete: Total Call OI: {total_call_oi}, Total Put OI: {total_put_oi}, PCR: {pcr:.2f}")
#     return metrics
