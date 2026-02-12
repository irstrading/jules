# app.py
print("Starting app.py...")

print("Importing Flask...")
from flask import Flask, render_template
print("Flask imported.")

print("Importing Flask-SocketIO...")
from flask_socketio import SocketIO, emit
print("Flask-SocketIO imported.")

print("Importing time...")
import time
print("time imported.")

print("Importing threading...")
from threading import Thread, Event
print("threading imported.")

print("Importing brokers...")
from brokers import AngelOne, Dhan
print("brokers imported.")

print("Importing strategies...")
from strategies import simple_moving_average_strategy
print("strategies imported.")

print("Importing config...")
import config
print("config imported.")


print("Imports successful.")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

print("Flask and SocketIO initialized.")

# --- Background Thread for Stock Screening ---
thread = Thread()
thread_stop_event = Event()

def stock_screener():
    """
    This function runs in the background and simulates real-time stock screening.
    """
    print("Starting stock screener...")
    # Connect to brokers (example with Angel One)
    # In a real application, you would choose the broker based on user configuration
    # angel_one = AngelOne(
    #     config.ANGEL_ONE_API_KEY,
    #     config.ANGEL_ONE_SECRET_KEY,
    #     config.ANGEL_ONE_USERNAME,
    #     config.ANGEL_ONE_PASSWORD,
    #     config.ANGEL_ONE_TOTP_SECRET
    # )
    # angel_one.connect()

    while not thread_stop_event.is_set():
        # Simulate fetching market data
        # In a real app, you would get this from the broker's WebSocket feed
        simulated_data = {'symbol': 'RELIANCE', 'price': 2800.00 + (time.time() % 100)}

        # Apply strategy
        signal = simple_moving_average_strategy(simulated_data)

        if signal == "BUY":
            alert_message = f"BUY signal for {simulated_data['symbol']} at {simulated_data['price']}"
            print(alert_message)
            socketio.emit('new_alert', {'data': alert_message}, namespace='/test')

        socketio.sleep(5)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    print('Client connected')
    global thread
    if not thread.is_alive():
        print("Starting Thread")
        thread = socketio.start_background_task(stock_screener)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    print("Inside __main__ block.")
    socketio.run(app, debug=True)
