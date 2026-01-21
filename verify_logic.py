import sys
import os

# Add src to path so we can import 'models' etc.
sys.path.append(os.path.join(os.getcwd(), 'src'))

from engine.arbitrage import ArbitrageEngine
from models import Event, Outcome
from datetime import datetime

def test_arbitrage_logic():
    print("Testing Arbitrage Logic...")
    engine = ArbitrageEngine(threshold=80)
    
    # Mock Events
    event_a = Event(
        id="1", title="Will Trump Win?", market_source="Polymarket", url="", created_at=datetime.now(), volume=1000,
        outcomes=[Outcome("Yes", 0.4, 0.4), Outcome("No", 0.6, 0.6)]
    )
    
    event_b = Event(
        id="2", title="Trump 2024 Election Winner", market_source="Kalshi", url="", created_at=datetime.now(), volume=1000,
        outcomes=[Outcome("Yes", 0.55, 0.55), Outcome("No", 0.45, 0.45)]
    )
    
    # Arb: Buy Yes A (0.4) + Buy No B (0.45) = 0.85 < 1.0 (Profit!)
    
    events = [event_a, event_b]
    opps = engine.find_opportunities(events)
    
    if len(opps) > 0:
        print(f"SUCCESS: Found {len(opps)} opportunities.")
        print(f"Profit: {opps[0]['profit_pct']:.2f}%")
        print(f"Cost: {opps[0]['cost']:.2f}")
    else:
        print("FAILURE: No opportunities found.")

if __name__ == "__main__":
    test_arbitrage_logic()
