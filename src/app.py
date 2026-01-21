import streamlit as st
import pandas as pd
import time
from datetime import datetime

from clients.polymarket import PolymarketClient
from clients.kalshi import KalshiClient
from clients.opinion import OpinionClient
from clients.predictfun import PredictFunClient
from engine.arbitrage import ArbitrageEngine
from config import Config

st.set_page_config(page_title="PredMkt Arb", layout="wide")

# Initialize Clients
@st.cache_resource
def get_clients():
    return [
        PolymarketClient(), 
        KalshiClient(),
        OpinionClient(),
        PredictFunClient()
    ]

@st.cache_resource
def get_engine():
    return ArbitrageEngine()

clients = get_clients()
engine = get_engine()

# Sidebar
st.sidebar.title("Settings")
auto_refresh = st.sidebar.checkbox("Auto Refresh (30s)", value=False)
match_threshold = st.sidebar.slider("Match Threshold", 50, 100, 85)
investment_amount = st.sidebar.number_input("Investment Amount ($)", value=Config.DEFAULT_INVESTMENT)

engine.threshold = match_threshold

st.title("Prediction Market Scanner")

tab1, tab2 = st.tabs(["New Events", "Arbitrage Opportunities"])

# Data Fetching
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.min

if st.button("Refresh Now") or (auto_refresh and (datetime.now() - st.session_state.last_update).seconds > 30):
    with st.spinner("Fetching data from markets..."):
        all_events = []
        for client in clients:
            events = client.fetch_new_events()
            all_events.extend(events)
        
        st.session_state.all_events = all_events
        st.session_state.last_update = datetime.now()

events = st.session_state.get('all_events', [])

with tab1:
    st.header(f"New Events ({len(events)})")
    if events:
        # Convert to DataFrame for display
        data = []
        for e in events:
            data.append({
                "Title": e.title,
                "Market": e.market_source,
                "Created": e.created_at.strftime("%Y-%m-%d %H:%M"),
                "Volume": f"${e.volume:,.0f}",
                "Outcomes": ", ".join([f"{o.name}: {o.price:.2f}" for o in e.outcomes])
            })
        st.dataframe(pd.DataFrame(data))
    else:
        st.info("No events fetched yet. Click Refresh.")

with tab2:
    st.header("Arbitrage Opportunties")
    if events:
        opportunities = engine.find_opportunities(events)
        
        if opportunities:
            for op in opportunities:
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.subheader(f"Profit: {op['profit_pct']:.1f}%")
                    st.write(f"Total Cost: ${op['cost']:.2f}")
                
                with c2:
                    st.write(f"**Buy {op['buy_on_a']}** on {op['event_a'].market_source}")
                    st.write(f"Event: {op['event_a'].title}")
                    st.write(f"Price: {op['event_a'].get_outcome_price(op['buy_on_a'])}")

                with c3:
                    st.write(f"**Buy {op['buy_on_b']}** on {op['event_b'].market_source}")
                    st.write(f"Event: {op['event_b'].title}")
                    st.write(f"Price: {op['event_b'].get_outcome_price(op['buy_on_b'])}")
                
                st.divider()
        else:
            st.info("No arbitrage opportunities found based on current data.")
            
            # Debug/Demo Mode for user to see what it looks like
            if st.checkbox("Show Demo Arbitrage"):
                st.warning("DEMO MODE: Showing fake opportunity")
                st.write("**Profit: 5.0%**")
                st.write("Buy Yes on Polymarket ($0.45) + Buy No on Kalshi ($0.50) = Cost $0.95")
    else:
        st.info("No events to analyze.")

if auto_refresh:
    time.sleep(1)
    st.rerun()
