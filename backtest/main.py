import json

from app.oanda.oanda import AccountAPI
from app.oanda.oanda import RequestAPI
from app.oanda.utils import calculate_max_times_each_time
from app.oanda.utils import from_granularity_to_time


if __name__ == '__main__':
    print('this is main.py')
    response = AccountAPI.access_account()
    print(response)
    api_client = RequestAPI()
    time = from_granularity_to_time('M5')
    r = api_client.request_data('M5',
                                api_client.get_from_time,
                                api_client.get_to_time,
                                1,
                                calculate_max_times_each_time(time),
                                time)
    candle_dict = json.loads(r)
    for count, value in enumerate(candle_dict['candles']):
        print(value)
    print(count)
