import pytest
from tgintegration import Response

pytestmark = pytest.mark.asyncio


async def test_start(controller, client):
    async with controller.collect(count=1) as res:  # type: Response

        await controller.send_command("/start")
        print("Punto1")

    assert res.num_messages == 1
    #assert res[0].sticker  # First message is a sticker