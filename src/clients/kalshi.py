import requests
from datetime import datetime
from typing import List
from clients.base import MarketClient
from models import Event, Outcome

class KalshiClient(MarketClient):
    # Using the public v2 API endpoint
    BASE_URL = "https://api.elections.kalshi.com/trade-api/v2/markets" 

    def fetch_new_events(self) -> List[Event]:
        params = {
            "limit": 20,
            "status": "active"
            # Kalshi API doesn't always support sort by created via public param easily without cursor, 
            # but we'll try standard params or filter client side.
        }
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            events = []
            markets = data.get('markets', [])
            
            # Kalshi "markets" are often individual questions.
            for m in markets:
                outcomes_list = []
                
                # Kalshi usually has 'yes_ask' (buy yes) and 'no_ask' (buy no) prices roughly?
                # Or 'yes_bid' / 'yes_ask'.
                # Let's use 'yes_price' (last match) or mid.
                # Public API often returns `yes_bid`, `yes_ask`.
                
                yes_price = m.get('yes_ask', 0) / 100.0 # Kalshi provides cents usually
                no_price = m.get('no_ask', 0) / 100.0
                
                outcomes_list.append(Outcome(name='Yes', price=yes_price, probability=yes_price))
                outcomes_list.append(Outcome(name='No', price=no_price, probability=no_price))

                # Created time might not be in every public response, use 'open_date'
                created_ts = m.get('open_date')
                dt = datetime.fromisoformat(created_ts.replace('Z', '+00:00')) if created_ts else datetime.now()

                events.append(Event(
                    id=m.get('ticker_name', m.get('id')),
                    title=m.get('title', 'Unknown Event'),
                    market_source="Kalshi",
                    url=f"https://kalshi.com/markets/{m.get('ticker_name')}",
                    created_at=dt,
                    volume=float(m.get('volume_24h', 0)), # approximate
                    outcomes=outcomes_list,
                    image_url=None
                ))
            return events
        except Exception as e:
            print(f"Error fetching Kalshi events: {e}")
            return []
