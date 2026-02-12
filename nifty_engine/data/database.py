# nifty_engine/data/database.py

import sqlite3
import pandas as pd
from datetime import datetime
from nifty_engine.config import DB_NAME

class Database:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Table for candles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS candles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    timestamp DATETIME,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    interval TEXT,
                    UNIQUE(symbol, timestamp, interval)
                )
            ''')
            # Table for alerts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    timestamp DATETIME,
                    message TEXT,
                    strategy_name TEXT
                )
            ''')
            conn.commit()

    def save_candles(self, df, symbol, interval='1m'):
        """
        Saves a DataFrame of candles to the database.
        Expected columns: ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        """
        df = df.copy()
        df['symbol'] = symbol
        df['interval'] = interval

        with self._get_connection() as conn:
            df.to_sql('candles', conn, if_exists='append', index=False, method=self._insert_on_conflict)

    def _insert_on_conflict(self, table, conn, keys, data_iter):
        """
        Helper method for to_sql to handle conflicts (UPSERT equivalent for older SQLite)
        """
        data = [dict(zip(keys, row)) for row in data_iter]
        cursor = conn.cursor()
        for row in data:
            columns = ', '.join(row.keys())
            placeholders = ', '.join(['?' for _ in row])
            sql = f"INSERT OR REPLACE INTO {table.name} ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(row.values()))

    def get_last_candles(self, symbol, interval='1m', limit=500):
        query = f"""
            SELECT timestamp, open, high, low, close, volume
            FROM candles
            WHERE symbol = '{symbol}' AND interval = '{interval}'
            ORDER BY timestamp DESC
            LIMIT {limit}
        """
        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df.sort_values('timestamp')

    def log_alert(self, symbol, message, strategy_name):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (symbol, timestamp, message, strategy_name)
                VALUES (?, ?, ?, ?)
            ''', (symbol, datetime.now(), message, strategy_name))
            conn.commit()

    def get_recent_alerts(self, limit=50):
        query = f"SELECT * FROM alerts ORDER BY timestamp DESC LIMIT {limit}"
        with self._get_connection() as conn:
            return pd.read_sql_query(query, conn)
