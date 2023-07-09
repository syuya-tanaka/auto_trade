"""Database definition."""
from contextlib import contextmanager
import logging.config
import threading

from app.settings import Base
from app.settings import engine
from app.settings import session
from app.settings import LOGGING_CONFIG


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('models_base')

lock = threading.Lock()

def init_db() -> None:
    from app.models import candlesticks
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


@contextmanager
def session_scope(session):
    session = session.Session()
    lock.acquire()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise Exception('It did not work.')
    finally:
        session.close()
        lock.release()


init_db()
# delete_db()

