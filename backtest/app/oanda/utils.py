"""various utilities."""
import datetime
import logging.config
import json
from threading import RLock
from queue import Queue
from typing import Callable
from typing import Generator
from typing import List
from typing import Optional
from typing import Tuple

from app.models.candlesticks import UsdJpyBaseCandle5m
from app.models.candlesticks import UsdJpyBaseCandle15m
from app.models.candlesticks import UsdJpyBaseCandle30m
from app.models.candlesticks import UsdJpyBaseCandle1h
from app.models.candlesticks import UsdJpyBaseCandle4h
from app.models.candlesticks import UsdJpyBaseCandle1d
from app.settings import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('dev')


def endpoint(url: str):
    """Specify the endpoint of the api-server.
    Args:
        url (str): The path to add below the hostname.
        method (str): Specify the HTTP method.

    Returns:
        deco (callable): inner function.
    """
    def deco(obj):
        obj.ENDPOINT = url
        # obj.METHOD = method
        # obj.EXPECTED_STATUS = method
        return obj
    return deco


def hand_the_class(class_name: Optional[str] = None, **kwargs):
    """Take out the ORMed classes in the dictionary one by one.
    Args:
        class_name (Optional[str] = None): Extract only the specified class.
        kwargs (dict): Contains the expanded dictionary.

    Returns:
        key (str): Granularity.
        value (class): The class itself.
    """
    for key, value in kwargs.items():
        if class_name and class_name == value.__name__:
            return value
        yield key, value


def from_granularity_to_time(granularity: str) -> int:
    """Changed string granularity to int granularity.
    Args:
        granularity (str): String granularity.

    Returns:
        Granularity to minute of int.
    """
    match granularity:
        case granularity if granularity == 'M5':
            return 5
        case granularity if granularity == 'M15':
            return 15
        case granularity if granularity == 'M30':
            return 30
        case granularity if granularity == 'H1':
            return 60
        case granularity if granularity == 'H4':
            return 240
        case granularity if granularity == 'D':
            return 1440
    raise ValueError('Something other than "granularity" came in.')


def from_granularity_to_model(granularity: str):
    """Changed string granularity to model.
    Args:
        granularity (str): String granularity.

    Returns:
        From granularity to model.
    """
    match granularity:
        case granularity if granularity == 'M5':
            return UsdJpyBaseCandle5m
        case granularity if granularity == 'M15':
            return UsdJpyBaseCandle15m
        case granularity if granularity == 'M30':
            return UsdJpyBaseCandle30m
        case granularity if granularity == 'H1':
            return UsdJpyBaseCandle1h
        case granularity if granularity == 'H4':
            return UsdJpyBaseCandle4h
        case granularity if granularity == 'D':
            return UsdJpyBaseCandle1d
    raise ValueError('Something other than "granularity" came in.')


def generate_date(days_offset: int = 0) -> datetime.datetime:
    """Calculate the date backwards.
    Args:
        days_offset(int): The number of days to subtract.

    Returns:
        days_ago(datetime): Calculated date.
    """
    ten_years_ago = datetime.datetime(year=2013, month=7, day=18)
    days_ago = ten_years_ago + datetime.timedelta(days=days_offset)
    return days_ago


def get_daily_quantity(granularity: int) -> int:
    """Returns the number of hours in a day divided by granularity.
    Args:
        granularity (int): e.g. 5, 15, 30, 60, 360, 1440

    Returns:
        daily_quantity (int): The number of hours in a day
                                    divided by granularity.
    """
    daily_quantity = 24 * 60 // granularity
    return daily_quantity


def get_max_days_each_once(granularity: int,
                           upper_limit: int = 5000) -> int:
    """Calculate the maximum number of times per hour.
    Args:
        time (int): e.g. 5, 15, 30, 60, 360, 1440
        upper_limit (int): The maximum number of requests that
                            can be made at one time is 5000.

    Returns:
        a_few_days (int): The maximum number of requests that
                            can run at once, converted to days.
    """
    # 時間ごとの１日分のリクエスト回数
    daily_quantity = get_daily_quantity(granularity)
    # granularity==1440は例外
    if granularity == 1440:
        return 3650

    # その最大リクエスト回数を"日数"に変換
    a_few_days = upper_limit // daily_quantity
    return a_few_days


def stopper_for_each_time(time: int) -> int:
    """Indicator to stop the request.
    Args:
        time (int): Int granularity. e.g. 5, 15, 30, 60, 240, 1440.

    Returns:
        total_times (int): Stop limit.
    """
    ten_years = 365 * 10 * 60 * 24
    total_times = ten_years // time
    return total_times


def count_each_granularity(granularity: str) -> int | ValueError:
    """Returns the maximum number of requests per granularity.
    Args:
        granularity (str): A string representing the time.

    Returns:
        max_times_5m (int): Maximum number of requests per 5-minute interval.
        max_times_15m (int): Maximum number of requests per 15-minute interval.
        max_times_30m (int): Maximum number of requests per 30-minute interval.
        max_times_1h (int):  Maximum number of requests per 1-hour interval.
        max_times_4h (int):  Maximum number of requests per 4-hour interval.
        max_times_1d (int):  Maximum number of requests per day interval.
    """
    match granularity:
        case granularity if granularity == 'M5':
            max_times_5m = get_max_days_each_once(5)
            return max_times_5m
        case granularity if granularity == 'M15':
            max_times_15m = get_max_days_each_once(15)
            return max_times_15m
        case granularity if granularity == 'M30':
            max_times_30m = get_max_days_each_once(30)
            return max_times_30m
        case granularity if granularity == 'H1':
            max_times_1h = get_max_days_each_once(60)
            return max_times_1h
        case granularity if granularity == 'H4':
            max_times_4h = get_max_days_each_once(240)
            return max_times_4h
        case granularity if granularity == 'D':
            max_times_1d = get_max_days_each_once(1440)
            return max_times_1d
    raise ValueError('granularity did not match any.')


def get_limit(func, time, days, quantity):
    """Limit number of requests per granularity.
    Args:
        func (callable): Contains stopper_for_each_time method.
        time (int): A value that converts granularity to int type minute.
        days (int): Maximum number of requests per granularity.
        quantity (int): Number of daily requests per granularity.
    """
    if time == 1440:
        return 2
    return func(time) // (days * quantity)


def _size_queue(queue: "Queue") -> int:
    """Queue size.
    Args:
        queue (Queue): A queue containing request data.

    Returns:
        size (int): Number of data in queue.
    """
    size = queue.qsize()
    return size


def fetch_from_queue(queue: "Queue", size: int) -> Generator[
                                                Generator[dict, None, None],
                                                None,
                                                None]:
    """Fetch data from queue.
    Args:
        queue (Queue): Fetch queued data.
        size (int): number of data in queue.

    Returns: candles_data (Generator): Contains request data for one time.
    """
    for i in range(size):
        candles_data = gen_candle_data(queue.get())
        yield candles_data


def gen_candle_data(candles_data: dict) -> Generator[dict, None, None]:
    """The data in the queue is further fetched by the generator.
    Args:
        candles_data (dict): A piece of data retrieved from the queue.

    Returns:
        candle_data (generator): One candle-stick."""
    candle_data = (data for data in candles_data['candles'])
    logger.debug({
        'action': 'test',
        'status': 'success',
        'value': candle_data
        })
    return candle_data


def convert_datetime_format(time: str) -> datetime.datetime:
    """Arrange the datetime to be stored in the DB.
    Args:
        time (str): datetime of the response data.

    Returns:
        formatted_time (datetime): Formatted datetime to put in DB.
    """
    datetime_time = datetime.datetime.fromisoformat(time)
    str_time = datetime_time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_time = datetime.datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S")
    return formatted_time


def data_extraction(**kwargs) -> Tuple[datetime.datetime,
                                       float,
                                       float,
                                       float,
                                       float,
                                       int]:
    """Extract data to put in DB.
    Args:
        kwargs : Data to put in DB.

    Returns:
        time (datetime.datetime): Date and time.
        open (float): Opening price.
        close (float): Closing price.
        high (float): High price.
        low (float): Low price.
        volume (int): Volume.
    """
    time_string = kwargs['time'][:-4]
    time = convert_datetime_format(time_string)
    open = float(kwargs['mid']['o'])
    close = float(kwargs['mid']['c'])
    high = float(kwargs['mid']['h'])
    low = float(kwargs['mid']['l'])
    volume = int(kwargs['volume'])
    return time, open, close, high, low, volume


def to_upsert_data(func_1: Callable,
                   func_2: Callable,
                   queue: "Queue",
                   size: int,
                   rlock: RLock,
                   list: Optional[List] = None) -> Generator[
                       Tuple[List[dict[str, str]]],
                       None,
                       None
                       ]:
    """Create a block for insertion each block into the DB.
    Args:
        func_1 (callable): fetch_from_queue method.
        func_2 (callable): data_extraction method.
        queue (Queue): A queue containing the requested data.
        size (int): Queue size.
        rlock (RLock): An instance of RLock.
        list (List): Always None.

    Returns:
        insert_list (Generator[List, None, None]): One block to insert into DB.
    """
    insert_list = []
    rlock.acquire()
    large_candles_data = func_1(queue, size)
    for candles_data in large_candles_data:
        # candles_dataはdictが沢山入ったList。
        gen = (candle_data for candle_data in candles_data)
        for candle_data in gen:
            time, open, close, high, low, volume = func_2(**candle_data)
            formatted_dict = {
                'time': time,
                'open': open,
                'close': close,
                'high': high,
                'low': low,
                'volume': volume
            }
            insert_list.append(formatted_dict)
        logger.debug({
            'action': 'preparing to store data together.',
            'status': 'success'
        })
        yield insert_list
    rlock.release()
