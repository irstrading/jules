import pandas as pd
import numpy as np
from python_stock_screener.strategies import calculate_all_indicators, market_pulse_strategy

def generate_sample_data(size=150):
    """Generates a sample DataFrame of stock data for demonstration."""
    data = pd.DataFrame({
        'high': np.linspace(100, 250, size),
        'low': np.linspace(98, 248, size),
        'close': np.linspace(99, 249, size),
        'volume': np.random.randint(10000, 50000, size=size)
    })
    # Add some noise to make it more realistic
    noise = np.random.randn(size) * 2
    data['close'] = data['close'] + noise
    data['high'] = data['high'] + noise
    data['low'] = data['low'] + noise
    return data

def run_demonstration():
    """
    Runs a demonstration of the Market-Pulse trading strategy.
    """
    print("--- Market-Pulse Strategy Demonstration ---")

    # 1. Generate sample stock data
    print("\n1. Generating sample stock data...")
    stock_data = generate_sample_data()

    # 2. Calculate all indicators
    print("2. Calculating all required technical indicators...")
    data_with_indicators = calculate_all_indicators(stock_data)

    # 3. Apply the trading strategy to get signals
    print("3. Applying the Market-Pulse strategy to generate signals...")
    signals = market_pulse_strategy(data_with_indicators)

    # 4. Combine signals with the data
    results = data_with_indicators.copy()
    results['signal'] = signals

    # 5. Display the last 15 days of data, indicators, and signals
    print("\n--- Results (last 15 days) ---")

    # Filter for days where a signal is generated
    actionable_days = results[results['signal'] != 'HOLD']

    if actionable_days.empty:
        print("\nNo 'BUY' or 'SELL' signals were generated in this sample run.")
        print("Displaying the last 15 days of data for context:")
        print(results.tail(15).to_string())
    else:
        print("\nDisplaying days with 'BUY' or 'SELL' signals:")
        print(actionable_days.to_string())

if __name__ == '__main__':
    run_demonstration()
