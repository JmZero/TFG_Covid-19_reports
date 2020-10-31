import pytest
from tgintegration import Response

pytestmark = pytest.mark.asyncio


# Ping to bot
async def test_ping(controller):
    assert await controller.ping_bot()


# Send /start and wait for one message
async def test_start(controller):
    async with controller.collect(count=1) as res:  # type: Response
        await controller.send_command("/start")

    assert not res.is_empty, "Bot did not respond to /start command"
    assert res.num_messages == 1
    assert "¡bienvenido a covid-19 report!" in res.full_text.lower()
    keyboard = res.keyboard_buttons
    assert len(keyboard) == 3   # 3 buttons in keyboard


# Send /help and wait for one message
async def test_help(controller):
    async with controller.collect(count=1) as res:  # type: Response
        await controller.send_command("/help")

    assert res.num_messages == 1
    assert not res.is_empty, "Bot did not respond to /help command"


# Send /help and wait for one message
async def test_info(controller):
    async with controller.collect(count=1) as res:  # type: Response
        await controller.send_command("/info")

    assert res.num_messages == 1
    assert not res.is_empty, "Bot did not respond to /help command"
    assert "este proyecto ha sido desarrollado como trabajo fin de grado" in res.full_text.lower()