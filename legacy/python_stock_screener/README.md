
# Real-Time Stock Screener

This project is a real-time stock screening application using Python, Flask, and Socket.IO.

## Features

- Real-time alerts displayed on a web interface.
- Modular architecture for connecting to different brokers.
- Customizable trading strategies.

## Setup

1.  **Create the directory structure:**
    - `python_stock_screener/`
    - `python_stock_screener/templates/`

2.  **Create the files with the code provided in the sections above.**

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your API keys:**
    - Open `config.py` and add your API keys for Angel One and/or Dhan.

## Running the Application

1.  **Start the server:**
    ```bash
    python app.py
    ```

2.  **Open your browser:**
    - Navigate to `http://127.0.0.1:5000` to see the real-time alerts.

## How to Customize

-   **Add a new broker:**
    -   Create a new class in `brokers.py` that inherits from the `Broker` class.
    -   Implement the `connect` method for the new broker.
-   **Add a new trading strategy:**
    -   Create a new function in `strategies.py`.
    -   Update `app.py` to use your new strategy.
