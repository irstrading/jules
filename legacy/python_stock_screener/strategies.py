# strategies.py

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
