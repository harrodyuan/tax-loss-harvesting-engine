from dataclasses import dataclass
import datetime
from config import WASH_SALE_DAYS

@dataclass
class TaxLot:
    ticker: str
    date_acquired: datetime.date
    shares: float
    cost_basis: float

    def matches_wash_sale(self, ticker: str, date: datetime.date) -> bool:
        """
        Checks if this lot was acquired within 30 days of the given date for the same ticker.
        Used to identify if this purchase triggers a wash sale rule against a loss sale on 'date'.
        """
        if self.ticker != ticker:
            return False
        # Check if date_acquired is within +/- 30 days of the target date
        delta = abs((self.date_acquired - date).days)
        return delta <= WASH_SALE_DAYS

