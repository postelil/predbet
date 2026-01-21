from abc import ABC, abstractmethod
from typing import List
from models import Event

class MarketClient(ABC):
    @abstractmethod
    def fetch_new_events(self) -> List[Event]:
        """Fetches the most recent events from the market."""
        pass
