from typing import List, Dict, Tuple
from fuzzywuzzy import fuzz
from models import Event, Outcome

class ArbitrageEngine:
    def __init__(self, threshold: int = 85):
        self.threshold = threshold # Match confidence threshold

    def normalize_title(self, title: str) -> str:
        return title.lower().replace("will ", "").replace("?", "").strip()

    def find_opportunities(self, all_events: List[Event]) -> List[Dict]:
        """
        Finds arbitrage opportunities by matching events across different markets.
        Returns a list of opportunities.
        """
        opportunities = []
        
        # Group events by normalized title to find potential matches
        # This is O(N^2) naive matching, but fine for < 100 active events. 
        # For production with 1000s, need vector search or better blocking.
        
        checked_pairs = set()

        for i, event_a in enumerate(all_events):
            for j, event_b in enumerate(all_events):
                if i >= j: continue # Avoid duplicate pairs and self-match
                if event_a.market_source == event_b.market_source: continue # Same market, skip

                # Simple Fuzzy Match
                score = fuzz.ratio(self.normalize_title(event_a.title), self.normalize_title(event_b.title))
                
                if score > self.threshold:
                    # Potential Match found
                    # Check for Arbitrage: Buy YES on A, Buy NO on B (or vice versa)
                    
                    # Assuming binary Yes/No for simplicity first
                    a_yes = event_a.get_outcome_price("Yes")
                    a_no = event_a.get_outcome_price("No")
                    b_yes = event_b.get_outcome_price("Yes")
                    b_no = event_b.get_outcome_price("No")

                    if a_yes is not None and b_no is not None:
                         # Strategy 1: Buy Yes A + Buy No B
                         cost_1 = a_yes + b_no
                         if cost_1 < 1.0:
                             opportunities.append({
                                 "type": "Arbitrage",
                                 "event_a": event_a,
                                 "event_b": event_b,
                                 "buy_on_a": "Yes",
                                 "buy_on_b": "No",
                                 "cost": cost_1,
                                 "profit_pct": (1.0 - cost_1) / cost_1 * 100
                             })

                    if a_no is not None and b_yes is not None:
                         # Strategy 2: Buy No A + Buy Yes B
                         cost_2 = a_no + b_yes
                         if cost_2 < 1.0:
                             opportunities.append({
                                 "type": "Arbitrage",
                                 "event_a": event_a,
                                 "event_b": event_b,
                                 "buy_on_a": "No",
                                 "buy_on_b": "Yes",
                                 "cost": cost_2,
                                 "profit_pct": (1.0 - cost_2) / cost_2 * 100
                             })
                             
        return sorted(opportunities, key=lambda x: x['profit_pct'], reverse=True)
