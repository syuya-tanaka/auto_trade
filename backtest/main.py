import concurrent.futures
from concurrent.futures import as_completed
import json

from app.models.candlesticks import candle_class
from app.oanda.oanda import RequestAPI
from app.oanda.utils import get_max_days_each_once
from app.oanda.utils import from_granularity_to_time
from app.oanda.utils import get_daily_quantity
from app.oanda.utils import get_limit
from app.oanda.utils import hand_the_class
from app.oanda.utils import stopper_for_each_time


if __name__ == "__main__":
    print("this is main.py")
    api_client = RequestAPI()
    # time = from_granularity_to_time('M5')
    # r = api_client.request_data('M5',
    #                             api_client.get_from_time,
    #                             api_client.get_to_time,
    #                             1,
    #                             get_max_days_each_once(time),
    #                             time)

    # gen_candles = (candle_data for candle_data in (json.loads(r)['candles']))
    # for data in gen_candles:
    #     print(data)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as exec:
        for granularity, usd_jpy in hand_the_class(**candle_class):
            time = from_granularity_to_time(granularity)
            daily_quantity = get_daily_quantity(time)
            days = get_max_days_each_once(time)
            # limit = stopper_for_each_time(time) // (days * daily_quantity)
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
                print(result, time)
            print(granularity)
