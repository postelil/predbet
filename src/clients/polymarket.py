import requests
from datetime import datetime
from typing import List
from clients.base import MarketClient
from models import Event, Outcome

class PolymarketClient(MarketClient):
    BASE_URL = "https://gamma-api.polymarket.com/events"

    def fetch_new_events(self) -> List[Event]:
        params = {
            "limit": 20,
            "sort": "createdAt",
            "order": "desc",
            "closed": "false" # Only active events
        }
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            events = []
            for item in data:
                # Gamma API structure can vary, need robustness
                if not item.get('markets'):
                    continue
                    
                # Usually an event has multiple markets, or one main market. 
                # For binary events, usually one market.
                main_market = item['markets'][0] 
                
                outcomes_list = []
                # Check provided outcomes. Usually ["Yes", "No"] or similar.
                # Prices are in the 'outcomePrices' list in order.
                raw_outcomes = eval(main_market.get('outcomes', '[]')) # risky eval, but commonly returned as string list "['Yes', 'No']"
                prices = eval(main_market.get('outcomePrices', '[]'))
                
                if len(raw_outcomes) == len(prices):
                    for i, name in enumerate(raw_outcomes):
                        try:
                            price = float(prices[i])
                        except:
                            price = 0.0
                        outcomes_list.append(Outcome(name=name, price=price, probability=price))

                events.append(Event(
                    id=str(item['id']),
                    title=item['title'],
                    market_source="Polymarket",
                    url=f"https://polymarket.com/event/{item['slug']}",
                    created_at=datetime.fromisoformat(item['createdAt'].replace('Z', '+00:00')),
                    volume=float(item.get('volume', 0)),
                    outcomes=outcomes_list,
                    image_url=item.get('icon')
                ))
            return events
        except Exception as e:
            print(f"Error fetching Polymarket events: {e}")
            return []
