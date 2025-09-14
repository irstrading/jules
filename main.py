# -----------------------------------------------------------------------------
# Explosive Move Stock Scanner
# -----------------------------------------------------------------------------
# This is the main entry point for the application.
#
# The script will perform the following steps:
# 1. Load configuration and stock list from config.py.
# 2. Initialize the Dhan API client.
# 3. Loop through each stock in the list.
# 4. For each stock, loop through the specified timeframes (1H, 4H).
# 5. Fetch historical price and volume data.
# 6. Fetch options chain data.
# 7. Apply the indicator and pattern analysis functions from indicators.py.
# 8. If all conditions for an "explosive move" are met, send an alert.
# 9. Send the alert via the Telegram bot.
# -----------------------------------------------------------------------------
import config
import dhan_client
import indicators
import test_utils
import telegram_alerter
from datetime import datetime, timedelta

def main():
    """The main function to run the stock scanner."""
    print("Starting the stock scanner...")

    # --- Using Mock Data for Testing ---
    # We are using mock data to test the indicator logic without needing live API keys.
    # To switch to live data, comment out the mock data line and uncomment the API client lines.

    client = dhan_client.get_dhan_client()
    # to_date = datetime.now().strftime('%Y-%m-%d')
    # from_date = (datetime.now() - timedelta(days=250)).strftime('%Y-%m-%d')

    for stock in config.STOCKS_TO_SCAN:
        print(f"\n--- Analyzing {stock} ---")

        # Use mock data instead of fetching from the API
        df_1h = test_utils.create_mock_dataframe(days=300)

        # df_1h = dhan_client.get_historical_data(
        #     client=client,
        #     symbol=stock,
        #     exchange_segment="NSE_EQ",
        #     instrument_type="EQUITY",
        #     from_date=from_date,
        #     to_date=to_date
        # )

        if df_1h is not None and not df_1h.empty:
            # --- 1-Hour Timeframe Analysis ---
            print("\nAnalyzing 1-Hour Timeframe...")
            df_1h_squeezed = indicators.detect_squeeze(df_1h)

            # Display the last 5 rows to check the 'in_squeeze' column
            print("Latest 1H data with Squeeze signal:")
            print(df_1h_squeezed[['close', 'in_squeeze']].tail())

            # Run VCP analysis on the 1H data
            vcp_valid_1h = indicators.detect_vcp(df_1h_squeezed)

            # --- Final Alerting Logic ---
            is_squeezed_1h = df_1h_squeezed['in_squeeze'].iloc[-1]
            if is_squeezed_1h and vcp_valid_1h:
                alert_message = (
                    f"🚀 *Explosive Move Alert (1H)!* 🚀\n\n"
                    f"*Stock:* {stock}\n"
                    f"*Pattern:* Volatility Squeeze + VCP Detected\n"
                    f"The stock is consolidating tightly and may be preparing for a significant move."
                )
                telegram_alerter.send_telegram_alert(alert_message)


            # --- 4-Hour Timeframe Analysis ---
            print("\nAnalyzing 4-Hour Timeframe...")
            df_4h = dhan_client.resample_to_4h(df_1h)
            if df_4h is not None and not df_4h.empty:
                df_4h_squeezed = indicators.detect_squeeze(df_4h)
                print("Latest 4H data with Squeeze signal:")
                print(df_4h_squeezed[['close', 'in_squeeze']].tail())

                # Run VCP analysis on the 4H data
                vcp_valid_4h = indicators.detect_vcp(df_4h_squeezed)

                # --- Final Alerting Logic ---
                is_squeezed_4h = df_4h_squeezed['in_squeeze'].iloc[-1]
                if is_squeezed_4h and vcp_valid_4h:
                    alert_message = (
                        f"🚀 *Explosive Move Alert (4H)!* 🚀\n\n"
                        f"*Stock:* {stock}\n"
                        f"*Pattern:* Volatility Squeeze + VCP Detected\n"
                        f"The stock is consolidating tightly and may be preparing for a significant move."
                    )
                    telegram_alerter.send_telegram_alert(alert_message)

        # --- Options Analysis (DEFERRED) ---
        # option_chain_data = dhan_client.get_option_chain(client, stock, "NSE_EQ")
        # if option_chain_data:
        #     options_metrics = indicators.analyze_options_data(option_chain_data)
        #     # In the final version, these metrics will be used in the final condition check.
        else:
            print(f"Could not fetch or data is empty for {stock}. Skipping.")

    print("\nScanner finished.")

if __name__ == "__main__":
    main()
