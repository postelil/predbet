from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Outcome:
    name: str # "Yes" or "No" (or candidate name)
    price: float
    probability: float # 0.0 to 1.0

@dataclass
class Event:
    id: str
    title: str
    market_source: str # "Polymarket", "Kalshi", etc.
    url: str
    created_at: datetime
    volume: float
    outcomes: List[Outcome]
    image_url: Optional[str] = None
    
    def get_outcome_price(self, outcome_name: str) -> Optional[float]:
        for o in outcomes:
            if o.name.lower() == outcome_name.lower():
                return o.price
        return None
