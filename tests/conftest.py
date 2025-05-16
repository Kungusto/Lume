import pytest

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
