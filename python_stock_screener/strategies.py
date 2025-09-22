# strategies.py
import pandas as pd
import numpy as np

def williams_vix_fix(data, period=22):
    """
    Calculates the Williams Vix Fix indicator.

    The Williams Vix Fix is a volatility indicator that estimates the market's expectation
    of volatility. It measures the highest closing price over a lookback period and compares
    it to the current low, providing insights into market fear or complacency.

    Formula: ((Highest(Close, period) - Low) / Highest(Close, period)) * 100

    Args:
        data (pd.DataFrame): A DataFrame containing at least 'close' and 'low' price columns.
        period (int): The lookback period for calculating the highest close. Default is 22.

    Returns:
        pd.Series: A pandas Series containing the Williams Vix Fix values.
    """
    if not all(col in data.columns for col in ['close', 'low']):
        raise ValueError("Input DataFrame must contain 'close' and 'low' columns.")

    highest_close = data['close'].rolling(window=period).max()
    wvf = ((highest_close - data['low']) / highest_close) * 100
    return wvf

def vortex_indicator(data, period=14):
    """
    Calculates the Vortex Indicator (VI+ and VI-).

    The Vortex Indicator is used to spot trend reversals and confirm current trends.
    It consists of two oscillating lines: VI+ (uptrend) and VI- (downtrend).

    Args:
        data (pd.DataFrame): DataFrame with 'high', 'low', 'close' columns.
        period (int): The lookback period. Default is 14.

    Returns:
        tuple: A tuple containing two pd.Series (VI+, VI-).
    """
    if not all(col in data.columns for col in ['high', 'low', 'close']):
        raise ValueError("Input DataFrame must contain 'high', 'low', and 'close' columns.")

    # True Range
    tr1 = data['high'] - data['low']
    tr2 = abs(data['high'] - data['close'].shift(1))
    tr3 = abs(data['low'] - data['close'].shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Vortex Movement
    vm_plus = abs(data['high'] - data['low'].shift(1))
    vm_minus = abs(data['low'] - data['high'].shift(1))

    # Sum over the period
    sum_tr = tr.rolling(window=period).sum()
    sum_vm_plus = vm_plus.rolling(window=period).sum()
    sum_vm_minus = vm_minus.rolling(window=period).sum()

    # VI+ and VI-
    vi_plus = sum_vm_plus / sum_tr
    vi_minus = sum_vm_minus / sum_tr

    return vi_plus, vi_minus

def true_strength_index(data, r=25, s=13, signal_period=13):
    """
    Calculates the True Strength Index (TSI) and its signal line.

    The TSI is a momentum oscillator that ranges between +100 and -100.
    It's based on a double-smoothed exponential moving average of price momentum.

    Args:
        data (pd.DataFrame): DataFrame with a 'close' column.
        r (int): The period for the first EMA smoothing. Default is 25.
        s (int): The period for the second EMA smoothing. Default is 13.
        signal_period (int): The period for the signal line EMA. Default is 13.

    Returns:
        tuple: A tuple containing two pd.Series (TSI, signal_line).
    """
    if 'close' not in data.columns:
        raise ValueError("Input DataFrame must contain a 'close' column.")

    # Price change
    pc = data['close'].diff(1)

    # First smoothing (EMA of pc and abs(pc))
    ema_pc = pc.ewm(span=r, min_periods=r).mean()
    ema_abs_pc = abs(pc).ewm(span=r, min_periods=r).mean()

    # Second smoothing
    ema2_pc = ema_pc.ewm(span=s, min_periods=s).mean()
    ema2_abs_pc = ema_abs_pc.ewm(span=s, min_periods=s).mean()

    # TSI calculation
    tsi = 100 * (ema2_pc / ema2_abs_pc)

    # Signal line
    signal_line = tsi.ewm(span=signal_period, min_periods=signal_period).mean()

    return tsi, signal_line

def on_balance_volume(data):
    """
    Calculates the On-Balance Volume (OBV).

    OBV is a cumulative momentum indicator that uses volume flow to predict
    changes in stock price.

    Args:
        data (pd.DataFrame): DataFrame with 'close' and 'volume' columns.

    Returns:
        pd.Series: A pandas Series containing the OBV values.
    """
    if not all(col in data.columns for col in ['close', 'volume']):
        raise ValueError("Input DataFrame must contain 'close' and 'volume' columns.")

    obv = pd.Series(0, index=data.index)
    obv.iloc[0] = data['volume'].iloc[0]

    price_diff = data['close'].diff()

    # Vectorized calculation
    obv_changes = np.where(price_diff > 0, data['volume'],
                           np.where(price_diff < 0, -data['volume'], 0))

    # Set first change to 0, since it's the starting point
    obv_changes[0] = 0

    obv = obv_changes.cumsum() + data['volume'].iloc[0]

    return pd.Series(obv, index=data.index)

def calculate_all_indicators(data, wvf_period=22, vortex_period=14, tsi_r=25, tsi_s=13, tsi_signal=13, obv_sma_period=20):
    """
    Calculates all the indicators needed for the Market-Pulse strategy and adds them to the DataFrame.
    """
    indicator_data = data.copy()
    indicator_data['wvf'] = williams_vix_fix(indicator_data, period=wvf_period)
    indicator_data['vi_plus'], indicator_data['vi_minus'] = vortex_indicator(indicator_data, period=vortex_period)
    indicator_data['tsi'], indicator_data['tsi_signal'] = true_strength_index(indicator_data, r=tsi_r, s=tsi_s, signal_period=tsi_signal)
    indicator_data['obv'] = on_balance_volume(indicator_data)
    indicator_data['obv_sma'] = indicator_data['obv'].rolling(window=obv_sma_period).mean()
    return indicator_data

def market_pulse_strategy(data_with_indicators, wvf_threshold=80):
    """
    Generates trading signals based on the "Market-Pulse" strategy using a DataFrame
    that already contains all the necessary indicator values.

    Args:
        data_with_indicators (pd.DataFrame): DataFrame pre-populated with indicator values.
        wvf_threshold (float): Threshold for WVF to indicate high volatility.

    Returns:
        pd.Series: A Series of signals ('BUY', 'SELL', 'HOLD').
    """
    # 1. Define conditions for BUY and SELL signals from pre-calculated indicators
    high_volatility = data_with_indicators['wvf'] > wvf_threshold
    uptrend = data_with_indicators['vi_plus'] > data_with_indicators['vi_minus']
    downtrend = data_with_indicators['vi_minus'] > data_with_indicators['vi_plus']
    tsi_bullish_cross = (data_with_indicators['tsi'].shift(1) < data_with_indicators['tsi_signal'].shift(1)) & \
                        (data_with_indicators['tsi'] > data_with_indicators['tsi_signal'])
    tsi_bearish_cross = (data_with_indicators['tsi'].shift(1) > data_with_indicators['tsi_signal'].shift(1)) & \
                        (data_with_indicators['tsi'] < data_with_indicators['tsi_signal'])
    volume_confirms_buy = data_with_indicators['obv'] > data_with_indicators['obv_sma']
    volume_confirms_sell = data_with_indicators['obv'] < data_with_indicators['obv_sma']

    # 2. Combine conditions
    buy_signal = high_volatility & uptrend & tsi_bullish_cross & volume_confirms_buy
    sell_signal = high_volatility & downtrend & tsi_bearish_cross & volume_confirms_sell

    # 3. Generate signals
    signals = pd.Series('HOLD', index=data_with_indicators.index)
    signals[buy_signal] = 'BUY'
    signals[sell_signal] = 'SELL'

    return signals

def simple_moving_average_strategy(data):
    """
    A simple trading strategy based on moving averages.
    This is a placeholder. Implement your actual strategy here.
    """
    print("Executing simple moving average strategy...")
    # In a real scenario, you would analyze the data and generate buy/sell signals.
    if data['price'] > 100:
        return "BUY"
    else:
        return "HOLD"
