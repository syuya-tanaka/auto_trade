"""Database definition."""
import logging.config

from app.settings import Base
from app.settings import engine
from app.settings import session
from app.settings import LOGGING_CONFIG


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('models_base')


def init_db() -> None:
    Base.metadata.create_all(engine)


init_db()
