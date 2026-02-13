# database/manager.py

import sqlite3
import pandas as pd
import json
from datetime import datetime
from config import settings

class DatabaseManager:
    def __init__(self, db_name=settings.DB_NAME):
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
            # Table for signals
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    strategy TEXT,
                    symbol TEXT,
                    direction TEXT,
                    price REAL,
                    confidence REAL,
                    reasoning TEXT,
                    outcome TEXT,
                    pnl REAL
                )
            ''')
            # Table for analysis cycles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    cycle_number INTEGER,
                    spot_price REAL,
                    net_gex REAL,
                    pcr REAL,
                    alignment TEXT,
                    matched_patterns TEXT
                )
            ''')
            # System state
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            conn.commit()

    def test_connection(self):
        try:
            with self._get_connection() as conn:
                conn.execute("SELECT 1")
            return True
        except:
            return False

    def save_analysis_cycle(self, cycle_number, timestamp, market_data, analysis_results, signals):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            patterns = [p['name'] for p in analysis_results.get('patterns', [])]
            cursor.execute('''
                INSERT INTO analysis_history (timestamp, cycle_number, spot_price, net_gex, pcr, alignment, matched_patterns)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                cycle_number,
                market_data.get('spot_price'),
                analysis_results['gex'].get('net_gex'),
                analysis_results['oi'].get('pcr'),
                json.dumps(analysis_results.get('alignment')),
                json.dumps(patterns)
            ))

            for s in signals:
                cursor.execute('''
                    INSERT INTO signals (timestamp, strategy, symbol, direction, price, confidence, reasoning)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (timestamp, s['strategy'], s['symbol'], s['direction'], s['price'], s['confidence'], s['reasoning']))

            conn.commit()

    def get_config(self, key, default=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_config WHERE key = ?", (key,))
            result = cursor.fetchone()
            return result[0] if result else default

    def set_config(self, key, value):
        with self._get_connection() as conn:
            conn.execute("INSERT OR REPLACE INTO system_config (key, value) VALUES (?, ?)", (key, str(value)))
            conn.commit()

    def close(self):
        pass # sqlite handles connection closing with context managers
