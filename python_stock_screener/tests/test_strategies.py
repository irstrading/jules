import unittest
import pandas as pd
import numpy as np
from python_stock_screener.strategies import (
    williams_vix_fix, vortex_indicator, true_strength_index, on_balance_volume,
    calculate_all_indicators, market_pulse_strategy
)

class TestStrategies(unittest.TestCase):

    def setUp(self):
        """Set up a standard dataframe for testing."""
        size = 100
        self.base_data = pd.DataFrame({
            'high': np.linspace(100, 200, size),
            'low': np.linspace(98, 198, size),
            'close': np.linspace(99, 199, size),
            'volume': np.full(size, 1000, dtype=int)
        })

    def test_williams_vix_fix(self):
        """
        Test the Williams Vix Fix calculation with sample data.
        """
        data = {
            'close': [110, 112, 115, 114, 116, 118, 120, 119, 117, 122],
            'low':   [108, 110, 113, 112, 114, 116, 118, 117, 115, 120]
        }
        df = pd.DataFrame(data)
        period = 5
        wvf = williams_vix_fix(df, period=period)
        self.assertTrue(pd.isna(wvf[3]))
        self.assertAlmostEqual(wvf[4], 1.7241379, places=5)

    def test_vortex_indicator(self):
        """
        Test the Vortex Indicator calculation.
        """
        data = {
            'high':  [25.0, 25.1, 25.3, 24.8, 25.2],
            'low':   [24.5, 24.7, 24.9, 24.6, 24.8],
            'close': [24.9, 25.0, 25.2, 24.7, 25.1]
        }
        df = pd.DataFrame(data)
        period = 3
        vi_plus, vi_minus = vortex_indicator(df, period=period)
        self.assertTrue(pd.isna(vi_plus[2]))
        self.assertAlmostEqual(vi_plus[3], 0.92857, places=5)
        self.assertAlmostEqual(vi_minus[3], 0.85714, places=5)

    def test_true_strength_index(self):
        """
        Test the True Strength Index calculation.
        """
        data = {'close': np.arange(100, 150, 1)}
        df = pd.DataFrame(data)
        r, s, sig = 10, 5, 5
        tsi, signal_line = true_strength_index(df, r=r, s=s, signal_period=sig)
        self.assertTrue(pd.isna(tsi[r + s - 2]))
        self.assertFalse(pd.isna(tsi[r + s - 1]))
        self.assertTrue(all(tsi.dropna() <= 100))

    def test_on_balance_volume(self):
        """
        Test the On-Balance Volume calculation.
        """
        data = {
            'close':  [10, 12, 11, 11, 13, 14],
            'volume': [1000, 1500, 1200, 800, 2000, 2500]
        }
        df = pd.DataFrame(data)
        obv = on_balance_volume(df)
        expected_obv = pd.Series([1000, 2500, 1300, 1300, 3300, 5800])
        pd.testing.assert_series_equal(obv, expected_obv, check_names=False)

    def test_market_pulse_strategy_buy_signal(self):
        """
        Test the market_pulse_strategy BUY signal logic by mocking conditions.
        """
        indicator_df = calculate_all_indicators(self.base_data.copy())
        signal_idx = indicator_df.index[-5]

        # Force all conditions to be TRUE at the signal index
        indicator_df.loc[signal_idx, 'wvf'] = 81
        indicator_df.loc[signal_idx, 'vi_plus'] = 2
        indicator_df.loc[signal_idx, 'vi_minus'] = 1
        indicator_df.loc[signal_idx - 1, 'tsi'] = 0
        indicator_df.loc[signal_idx - 1, 'tsi_signal'] = 1
        indicator_df.loc[signal_idx, 'tsi'] = 1
        indicator_df.loc[signal_idx, 'tsi_signal'] = 0
        indicator_df.loc[signal_idx, 'obv'] = 2
        indicator_df.loc[signal_idx, 'obv_sma'] = 1

        # Make sure the next day does not trigger a signal
        indicator_df.loc[signal_idx + 1, 'wvf'] = 70

        signals = market_pulse_strategy(indicator_df)

        self.assertEqual(signals.loc[signal_idx], 'BUY')
        self.assertEqual(signals.value_counts().get('BUY', 0), 1)
        self.assertEqual(signals.loc[signal_idx + 1], 'HOLD')

if __name__ == '__main__':
    unittest.main()
