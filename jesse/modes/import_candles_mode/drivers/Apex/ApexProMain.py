import requests
import jesse.helpers as jh
from jesse.modes.import_candles_mode.drivers.interface import CandleExchange
from typing import Union
from jesse import exceptions
from .apex_pro_utils import timeframe_to_interval


class ApexProMain(CandleExchange):
    def __init__(self, name: str, rest_endpoint: str) -> None:
        from jesse.modes.import_candles_mode.drivers.Binance.BinanceSpot import BinanceSpot

        super().__init__(name=name, count=200, rate_limit_per_second=10, backup_exchange_class=BinanceSpot)
        self.name = name
        self.endpoint = rest_endpoint

    def get_starting_time(self, symbol: str, start_timestamp:int=None) -> int:
        dashless_symbol = jh.dashless_symbol(symbol)
        payload = {
            'symbol': dashless_symbol,
            'interval': 'W',
            'limit': 200,
            'start': 1514811660
        }
        if not start_timestamp is None:
            payload['start'] = start_timestamp

        response = requests.get(self.endpoint + '/v2/klines', params=payload)
        self.validate_response(response)

        if 'data' not in response.json():
            raise exceptions.ExchangeInMaintenance(response.json()['msg'])
        elif response.json()['data'] == {}:
            raise exceptions.InvalidSymbol('Exchange does not support the entered symbol. Please enter a valid symbol.')
        
        data = response.json()['data'][dashless_symbol]
        # Reverse the data list
        data = data[::-1]
        
        return int(data[1]['t'])

    def fetch(self, symbol: str, start_timestamp: int, timeframe: str = '1m') -> Union[list, None]:
        dashless_symbol = jh.dashless_symbol(symbol)
        interval = timeframe_to_interval(timeframe)

        payload = {
            'symbol': dashless_symbol,
            'interval': interval,
            'start': int(start_timestamp / 1000),
            'limit': self.count
        }

        response = requests.get(self.endpoint + '/v2/klines', params=payload)
        # check data exist in response.json

        if 'data' not in response.json():
            raise exceptions.ExchangeInMaintenance(response.json()['msg'])
        elif response.json()['data'] == {}:
            raise exceptions.InvalidSymbol('Exchange does not support the entered symbol. Please enter a valid symbol.')
        
        data = response.json()['data'][dashless_symbol]

        return [
            {
                'id': jh.generate_unique_id(),
                'exchange': self.name,
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': int(d['t']),
                'open': float(d['o']),
                'close': float(d['c']),
                'high': float(d['h']),
                'low': float(d['l']),
                'volume': float(d['v'])
            } for d in data
        ]