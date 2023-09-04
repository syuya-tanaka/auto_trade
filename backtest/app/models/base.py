"""Database-related."""
from contextlib import contextmanager
from typing import Any
from typing import Callable
from typing import Generator
import logging.config
from threading import RLock

from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import insert

from app.settings import engine
from app.settings import Base
from app.settings import Session
from app.settings import _S
from app.settings import LOGGING_CONFIG


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('models_base')


def init_db() -> None:
    from app.models import candlesticks
    if not inspect_db():
        Base.metadata.create_all(bind=engine)
        logger.debug({
            'action': 'create_table',
            'status': 'success'
        })


def delete_db() -> None:
    from app.models import candlesticks
    Base.metadata.drop_all(bind=engine)
    logger.debug({
        'action': 'delete_table',
        'status': 'success'
    })


def inspect_db() -> bool:
    inspector = inspect(engine)
    inspection_results = inspector.has_table('usd_jpy_5m')
    logger.debug({
        'action': 'inspect db',
        'status': inspection_results
    })
    return bool(inspection_results)


def count_candles_data(model) -> int:
    session = Session()
    data_count = session.query(model).count()
    return data_count


def bulk_upsert(model, granularity, rlock, insert_list):
    with session_scope(rlock) as session:
        if granularity == 'H4':
            insert_stmt = insert(model).values(insert_list)
            insert_stmt = insert_stmt.on_conflict_do_update(
                constraint='usd_jpy_4h_pkey',
                set_={'time': insert_stmt.excluded.time}
                )
            session.execute(insert_stmt)
            insert_list.clear()

        else:
            session.execute(
                insert(model),
                insert_list,
            )
            insert_list.clear()


def fetch_desc_data_from_data(granularity: str,
                              func: Callable,
                              rlock: RLock):
    """Fetch data from DB in descending order.
    Args:
        granularity (str): granularity.
        func (callable): A function that returns a table by 'granularity'.
                         (app.oanda.utils.from_granularity_to_model)

    Returns:
        Descending data for each table.
    """
    match granularity:
        case granularity if granularity == 'M5':
            model = func(granularity)
            count = count_candles_data(model)
            return model.fetch_data_in_desc_order(rlock), count
        case granularity if granularity == 'M15':
            model = func(granularity)
            count = count_candles_data(model)
            return model.fetch_data_in_desc_order(rlock), count
        case granularity if granularity == 'M30':
            model = func(granularity)
            count = count_candles_data(model)
            return model.fetch_data_in_desc_order(rlock), count
        case granularity if granularity == 'H1':
            model = func(granularity)
            count = count_candles_data(model)
            return model.fetch_data_in_desc_order(rlock), count
        case granularity if granularity == 'H4':
            model = func(granularity)
            count = count_candles_data(model)
            return model.fetch_data_in_desc_order(rlock), count
        case granularity if granularity == 'D':
            model = func(granularity)
            count = count_candles_data(model)
            return model.fetch_data_in_desc_order(rlock), count

    raise ValueError('One of "M5", "M15", "M30", "H1", "H4", "D"')


@contextmanager
def session_scope(rlock: RLock) -> Generator[_S, Any, Any]:
    session = Session()
    rlock.acquire()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.info(f'{e}')
    finally:
        session.close()
        rlock.release()
