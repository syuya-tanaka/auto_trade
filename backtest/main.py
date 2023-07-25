import concurrent.futures
from concurrent.futures import as_completed
import json

from app.models.candlesticks import candle_class
from app.oanda.oanda import RequestAPI
from app.oanda.utils import convert_from_bytes_to_dict
from app.oanda.utils import data_extraction
from app.oanda.utils import get_max_days_each_once
from app.oanda.utils import from_granularity_to_time
from app.oanda.utils import get_daily_quantity
from app.oanda.utils import get_limit
from app.oanda.utils import hand_the_class
from app.oanda.utils import stopper_for_each_time


if __name__ == "__main__":
    print("this is main.py")
    api_client = RequestAPI()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as exec:
        for granularity, usd_jpy in hand_the_class(**candle_class):
            time = from_granularity_to_time(granularity)
            daily_quantity = get_daily_quantity(time)
            days = get_max_days_each_once(time)
            limit = get_limit(stopper_for_each_time,
                              time,
                              days,
                              daily_quantity)
            futures = [
                exec.submit(
                    api_client.request_data,
                    granularity,
                    api_client.get_from_time,
                    api_client.get_to_time,
                    count,
                    days,
                    time,
                )
                for count in range(1, limit)
            ]

            for future in as_completed(futures):
                result = future.result()
                usd_jpy = candle_class[granularity]
                response_dict = convert_from_bytes_to_dict(result)
                print(type(response_dict), f'response_dict: {response_dict}')
                for data in response_dict:
                    time, open, close, high, low, volume = data_extraction(**data)
                    print(type(data), f'data: {data}')
                    usd_jpy.create(time, open, close, high, low, volume)
            print(granularity)
