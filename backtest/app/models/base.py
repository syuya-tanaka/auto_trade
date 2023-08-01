"""Database definition."""
from typing import Any
from typing import Generator
from contextlib import contextmanager
import logging.config
from threading import RLock

from sqlalchemy import inspect
from sqlalchemy import insert

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


def bulk_insertion(model, rlock, insert_list):
    with session_scope(rlock) as session:
        session.execute(
            insert(model),
            insert_list,
        )
        insert_list.clear()


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


init_db()
# delete_db()
