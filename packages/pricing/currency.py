"""
ResearchOS Multi-Currency Converter & Exchange Engine
Default Currency: AUD (Australian Dollar)
"""
from datetime import datetime
from typing import Dict

# Verified benchmark exchange rates with AUD base
RATES_TO_AUD = {
    "AUD": 1.0,
    "USD": 1.54,    # 1 USD ≈ 1.54 AUD
    "EUR": 1.67,    # 1 EUR ≈ 1.67 AUD
    "GBP": 1.95,    # 1 GBP ≈ 1.95 AUD
    "NZD": 0.94,    # 1 NZD ≈ 0.94 AUD
    "CAD": 1.13,    # 1 CAD ≈ 1.13 AUD
    "JPY": 0.010,   # 1 JPY ≈ 0.010 AUD
}


class CurrencyConverter:
    def __init__(self):
        self.rates = RATES_TO_AUD
        self.last_updated = datetime.utcnow()

    def to_aud(self, amount: float, currency: str = "USD") -> float:
        rate = self.rates.get(currency.upper(), 1.54)
        return round(amount * rate, 2)

    def format_aud(self, amount: float) -> str:
        return f"${amount:,.2f} AUD"


currency_converter = CurrencyConverter()
