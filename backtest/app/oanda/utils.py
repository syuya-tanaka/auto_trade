"""various utilities."""
import datetime
from typing import Optional


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


def generate_date(days_offset: int = 0):
    """Calclulate the date backwards.
    Args:
        days_offset(int): The number of days to subtract.

    Returns:
        days_ago(datetime): Calculated date.
    """
    ten_years_ago = datetime.datetime(year=2013, month=7, day=18)
    days_ago = ten_years_ago + datetime.timedelta(days=days_offset)
    return days_ago


def get_diff_in_days(data):
    """jsonからデータを取得して一番古い日付を取得。(DBの方で"time"カラムがprimary-keyなので重複は無し)

    一旦保留

    """
    pass


def get_daily_quantity(granularity: int):
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
    # 時間ごとの最大リクエスト回数
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
    """"""
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
    if time == 1440:
        return 2

    return func(time) // (days * quantity)
