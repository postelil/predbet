# Prediction Market Arbitrage Bot

This tool monitors prediction markets (Polymarket, Kalshi, Opinion*, PredictFun*) to find arbitrage opportunities where you can buy "Yes" on one market and "No" on another for a guaranteed profit.

## Features
- **Real-Time Feed**: Aggregates events from multiple markets.
- **Arbitrage Scanner**: Automatically finds events with >0% risk-free profit spread.
- **Profit Calculator**: Enter your investment amount to see exact returns.
- **Web Interface**: Clean dashboard built with Streamlit.

## Supported Markets
- **Polymarket**: ✅ Live (Gamma API)
- **Kalshi**: ✅ Live (Public V2)
- **Opinion Labs**: ⚠️ Integrated but using **Test Data** (Public API not found).
- **PredictFun**: ⚠️ Integrated but using **Test Data** (Public API not found).

> **Note**: To enable real data for Opinion/PredictFun, update the `BASE_URL` in `src/clients/opinion.py` and `src/clients/predictfun.py` with their real API endpoints.

## Installation

1. Install Python 3.10+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the dashboard:
```bash
streamlit run src/app.py
```

The app will open in your browser (usually http://localhost:8501).
