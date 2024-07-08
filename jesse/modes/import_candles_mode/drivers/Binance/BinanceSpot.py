from .BinanceMain import BinanceMain
from jesse.enums import exchanges


class BinanceSpot(BinanceMain):
    def __init__(self) -> None:
        super().__init__(
            name=exchanges.BINANCE_SPOT,
            # rest_endpoint='https://www.binance.com/api/v3/klines',
            rest_endpoint='https://api.binance.com/api/v3/klines',
            backup_exchange_class=None
        )
