import asyncio
import logging
from pathlib import Path

import pytest
from decouple import config
from pyrogram import Client

from tgintegration import BotController

test_dir = Path(__file__).parent.absolute()

# Enabling logging
logger = logging.getLogger("test")
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@pytest.yield_fixture(scope="session", autouse=True)
def event_loop(request):
    """ Create an instance of the default event loop for the session. """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client() -> Client:
    client = Client(
        config("SESSION_STRING", default=None) or "test_covid_reports",
        workdir=test_dir,
        config_file=str(test_dir / "config.ini")
    )
    await client.start()
    yield client
    await client.stop()


@pytest.fixture(scope="module")
async def controller(client):
    c = BotController(
        client=client,
        peer="@CovidReportsBot",    # We are going to run tests on https://t.me/CovidReportsBot
        max_wait=10.0,              # Maximum timeout for responses (optional)
        wait_consecutive=0.8,       # Minimum time to wait for more/consecutive messages (optional)
    )

    await c.clear_chat()
    await c.initialize(start_client=False)
    yield c