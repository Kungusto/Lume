import pytest
from src.database import async_session_maker_null_pool

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.database import async_session_maker_null_pool
from src.utils.dbmanager import DBManager
from src.config import settings, Settings

from dotenv import load_dotenv
import os

os.environ["MODE"] = "TEST"
load_dotenv(".env-test", override=True)

settings = Settings()

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    assert settings.MODE == "TEST"


async def get_db_null_pull() :
    return DBManager(session_factory=async_session_maker_null_pool)

async def db() :
    async for db in get_db_null_pull() :
        yield db
        
