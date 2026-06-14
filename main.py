import os
import time
import psycopg2
import requests
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgrespassword")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Table instantiations
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            action VARCHAR(10) NOT NULL,
            trade_amount NUMERIC(15, 2) NOT NULL,
            roi_percentage NUMERIC(10, 2) NOT NULL,
            profit_realized NUMERIC(15, 2) NOT NULL,
            balance NUMERIC(15, 2) NOT NULL
        );
    """)
    conn.commit()

    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name='logs' AND column_name='balance';
    """)
    if not cur.fetchone():
        cur.execute("ALTER TABLE logs ADD COLUMN balance NUMERIC(15, 2) NOT NULL DEFAULT 0;")
        conn.commit()

    cur.close()
    conn.close()

def fetch_ohlc(symbol="BTCUSDT", interval="15m", limit=50):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Error fetching OHLC data:", e)
        return pd.DataFrame()

    if not data:
        print("No data returned from Binance.")
        return pd.DataFrame()

    df = pd.DataFrame(data, columns=[
        "open_time","open","high","low","close","volume",
        "close_time","qav","trades","taker_base_vol","taker_quote_vol","ignore"
    ])
    df["open"] = df["open"].astype(float)
    df["close"] = df["close"].astype(float)
    return df[["open","high","low","close"]]

def linear_regression_predict(df):
    if len(df) < 10:
        print("Not enough data for regression.")
        return None

    X = np.arange(len(df)).reshape(-1, 1)
    y = df["close"].values

    model = LinearRegression()
    model.fit(X, y)

    next_index = np.array([[len(df)]])
    predicted_close = model.predict(next_index)[0]
    return float(predicted_close)

def execute_trade(df, balance, symbol="BTCUSDT"):
    if df.empty or len(df) < 10:
        print("Skipping trade: insufficient data.")
        return None, balance, 0, 0, symbol, 0, 0

    predicted_close = linear_regression_predict(df)
    if predicted_close is None:
        return None, balance, 0, 0, symbol, 0, 0

    current_close = float(df.iloc[-1]["close"])
    old_balance = balance

    if predicted_close > current_close:
        action = "BUY"
        roi_percentage = ((predicted_close - current_close) / current_close) * 100
        reason = "Predicted close higher than current → BUY"
    else:
        action = "SELL"
        roi_percentage = ((current_close - predicted_close) / current_close) * 100
        reason = "Predicted close lower than current → SELL"

    roi_percentage = round(float(roi_percentage), 2)
    profit_realized = round(float(old_balance * (roi_percentage / 100)), 2)
    new_balance = round(old_balance + profit_realized, 2)

    return action, new_balance, roi_percentage, profit_realized, symbol, current_close, predicted_close, reason, old_balance

def log_trade(action, new_balance, roi_percentage, profit_realized, symbol, current_close, predicted_close, reason, old_balance):
    if action is None:
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO logs (timestamp, action, trade_amount, roi_percentage, profit_realized, balance)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        datetime.now(),
        str(action),
        float(old_balance),
        float(roi_percentage),
        float(profit_realized),
        float(new_balance)
    ))
    conn.commit()
    cur.close()
    conn.close()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {action} {symbol} | "
          f"Old Balance: ${old_balance} | New Balance: ${new_balance} | "
          f"Profit: ${profit_realized} ({roi_percentage}%) | "
          f"Current Close: {current_close} | Predicted Close: {predicted_close} | "
          f"Reason: {reason}")

def main():
    init_db()
    interval = 5 * 60
    balance = 10000.00
    while True:
        df = fetch_ohlc(limit=50)
        action, balance, roi_percentage, profit_realized, symbol, current_close, predicted_close, reason, old_balance = execute_trade(df, balance)
        log_trade(action, balance, roi_percentage, profit_realized, symbol, current_close, predicted_close, reason, old_balance)
        print("Running Linear Regression Prediction Backtest")
        time.sleep(interval)

if __name__ == "__main__":
    main()
