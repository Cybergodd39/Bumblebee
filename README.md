# Bumblebee
YOLO trading automation is a transformer

⚙️ Overview
This program displays the  following:
Connects to the Binance API to fetch OHLC (Open, High, Low, Close) candlestick data.
Uses a linear regression model to predict the next closing price.
Executes trades (BUY or SELL) based on predictions.
Logs trades into a PostgreSQL database, including balances, ROI, profit, and rationale.
Compound interest.

🛠️ Setup Instructions
1. Install Dependencies
Make sure you have Python 3.9+ installed. Then install required libraries:
bash
pip install psycopg2 requests pandas scikit-learn

3. Configure Database
Install PostgreSQL on your machine or server.
Create a database (default name: postgres).
Ensure your credentials match the environment variables:
DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
Example:
bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=postgres
export DB_USER=postgres
export DB_PASS=postgrespassword
4. Run the Program
Start the bot with:
bash
python main.py
It will:
Initialize the database table (logs).
Fetch OHLC data every 5 minutes.
Simulate trades and log results.

💻 Recommended Computing Specifications
CPU: Modern dual‑core or quad‑core processor (Intel i5/AMD Ryzen 5 or better).
RAM: 8 GB minimum (16 GB recommended if running alongside PostgreSQL).
Storage: At least 128 GB free for logs and database growth.
Network: Stable internet connection (Binance API requires live access).
OS: Linux, macOS, or Windows with PostgreSQL installed.

📊 Expectations
Trade Frequency: Every 5 minutes.
Balance Growth: Starts at $10,000 and compounds after each trade.
Accuracy: Linear regression is a simple model; predictions are precise.
Logs: Each trade entry includes:
Old balance vs. new balance
Profit and ROI
Token/ticker (e.g., BTCUSDT)
Current vs. predicted close
Reason for trade (BUY if predicted > current, SELL otherwise)

✅ Best Practices
Monitor database size: Logs can grow quickly; archive old data periodically.
Risk management: Trade thresholds, stop loss and take profit.
Security: Never expose production database credentials in public code.
Scaling: For production, run on a server with PostgreSQL tuned for performance.

✏️ Note
OHLC data: Each candle shows market movement in a time window (open, high, low, close prices).
Linear regression: A basic machine learning model that fits a straight line to past data and predicts the next point.
ROI (Return on Investment): Percentage gain or loss relative to trade size.
Compounding: Profits are added to balance, so future trades use a larger amount.
This documentation should give you everything you need to set up, run, and understand the program.
