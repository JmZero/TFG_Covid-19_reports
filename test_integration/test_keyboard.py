import pytest
from tgintegration import Response

pytestmark = pytest.mark.asyncio

# Ping to bot
async def test_ping(controller):
    assert await controller.ping_bot()


# Click "Menu" keyboard button
async def test_menu_button(controller):
    async with controller.collect(count=2) as res:  # type: Response
        await controller.send_command("📖 Menú")

    assert not res.is_empty, 'Pressing the "📖 Menú" button had no effect'
    keyboard = res.inline_keyboards[0]
    # Necesario revisar los botones
    # for i in range(keyboard.num_buttons):
    #     print(i)
    #     button = await keyboard.click(index=i)
    #     assert button.is_empty

    for i in range(len(keyboard.rows)):
        if i == 6:
            assert len(keyboard.rows[i]) == 2
        else:
            assert len(keyboard.rows[i]) == 3


# Click "Información" keyboard button
async def test_info(controller):
    async with controller.collect(count=1) as res:  # type: Response
        await controller.send_command("ℹ Información")


    assert res.num_messages == 1
    assert not res.is_empty, 'Pressing the "ℹ Información" button had no effect'
    assert "este proyecto ha sido desarrollado como trabajo fin de grado" in res.full_text.lower()

# Pendiente de revisión
# # Click "Ayuda" keyboard button
# async def test_help_button(controller):
#     async with controller.collect(count=1) as res:  # type: Response
#         await controller.send_command("🆘 Ayuda")
#
#         assert res.num_messages == 1
#         assert not res.is_empty, 'Pressing the "Menu" button had no effect'