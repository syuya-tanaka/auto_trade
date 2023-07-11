"""Database definition."""
from typing import Any
from typing import Generator
from contextlib import contextmanager
import logging.config
import threading

from sqlalchemy import inspect

from app.settings import engine
from app.settings import Base
from app.settings import Session
from app.settings import _S
from app.settings import LOGGING_CONFIG


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('models_base')


lock = threading.Lock()


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


@contextmanager
def session_scope() -> Generator[_S, Any, Any]:
    session = Session()
    lock.acquire()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.info(f'{e}')
    finally:
        session.close()
        lock.release()


init_db()
# delete_db()
