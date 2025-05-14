import pytest

from src.database import async_session_maker_null_pool
from src.utils.dbmanager import DBManager
from src.config import settings

@pytest.fixture(scope="session")
def check_mode() :
    assert settings.MODE == "TEST"
