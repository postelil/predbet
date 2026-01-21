class Config:
    POLYMARKET_API_URL = "https://gamma-api.polymarket.com/events"
    KALSHI_API_URL = "https://api.elections.kalshi.com/trade-api/v2/markets"
    # Using Kalshi elections API for public data access without auth for basic markets if possible, 
    # otherwise standard V2 API.
    
    REFRESH_RATE_SECONDS = 30
    DEFAULT_INVESTMENT = 100.0
