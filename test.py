import pandas as pd
import requests 


def fetch_btc_bars(bar_interval,bar_nums):
    interval_dict={
        'minute':60,
        'hour':3600,
        'day':86400
        }

    url = 'https://www.bitstamp.net/api/v2/ohlc/btcusd/'
    params = {
        'step': interval_dict[bar_interval],
        'limit': bar_nums,
    }
    data = requests.get(url, params=params).json()['data']['ohlc']
    data = pd.DataFrame(
        data,
        columns=[
            'timestamp',
            'open',
            'high',
            'low',
            'close'])
    data.timestamp = data.timestamp.astype(int)
    data.timestamp = pd.to_datetime(data.timestamp, unit='s')
    return data


print(fetch_btc_bars('day',30))