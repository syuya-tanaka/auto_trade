import concurrent.futures
from concurrent.futures import as_completed
import logging
import logging.config
from queue import Queue
import sys
from threading import RLock

from app.controllers.socket_server import socket_server_run
from app.models.base import bulk_upsert
from app.models.base import count_candles_data
from app.models.base import fetch_desc_data_from_data
from app.models.base import init_db
from app.models.candlesticks import candle_class
from app.oanda.oanda import RequestAPI
from app.oanda.utils import _size_queue
from app.oanda.utils import data_extraction
from app.oanda.utils import get_daily_quantity
from app.oanda.utils import get_max_days_each_once
from app.oanda.utils import get_limit
from app.oanda.utils import fetch_from_queue
from app.oanda.utils import from_granularity_to_model
from app.oanda.utils import from_granularity_to_time
from app.oanda.utils import hand_the_class
from app.oanda.utils import stopper_for_each_time
from app.oanda.utils import to_upsert_data
from app.settings import LOGGING_CONFIG


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('dev')


def save_in_bulk_db_data():
    init_db()
    queue = Queue()
    rlock = RLock()
    api_client = RequestAPI()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as exec_1:
        for granularity, usd_jpy in hand_the_class(**candle_class):
            time = from_granularity_to_time(granularity)
            daily_quantity = get_daily_quantity(time)
            days = get_max_days_each_once(time)
            limit = get_limit(stopper_for_each_time,
                              time,
                              days,
                              daily_quantity)
            futures = [
                exec_1.submit(
                    api_client.request_data,
                    granularity,
                    api_client.get_from_time,
                    api_client.get_to_time,
                    count,
                    days,
                    time,
                    queue
                )
                for count in range(1, limit)
            ]

            for future in as_completed(futures):
                result = future.result()

                insert_list = []
                size = _size_queue(queue)
                for formatted_list in to_upsert_data(
                    func_1=fetch_from_queue,
                    func_2=data_extraction,
                    queue=queue,
                    size=size,
                    rlock=rlock):
                    bulk_upsert(usd_jpy, granularity, rlock, formatted_list)

            print(granularity)
    exec_1.shutdown(wait=True)


def main():
    # ここでsocketで外部サーバーからのデータを受信する。
    if count_candles_data(candle_class['M5']) >= 300000:
        socket_server_run()

    else:
        # oanda apiを使用してデータをフェッチ。
        save_in_bulk_db_data()

if __name__ == "__main__":
    main()

