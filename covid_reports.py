import logging
import os
import sys

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler

# Enabling logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

WELCOME, INICIO, HELP, STATUS_INFO, WELCOME_BAD, NOT_IMPLEMENTED = range(6)

# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")

global current_state, conv_handler

if mode == "dev":
    def run(updater):
        # Start the Bot
        updater.start_polling()

        # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT
        updater.idle()

elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        # Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)


def start_handler(update, context):
    # Handler-function for /random command
    global current_state

    chat_id = update.effective_user["id"]
    username = update.message.chat.username

    if username is None:
        logger.info("User {} started bot".format('None:' + str(chat_id)))
        update.message.reply_text("¡Bienvenido a Covid-19 Report! Parece que no tienes usuario de Telegram."
                                  " Ve a ajustes, ponte un nombre de usuario y podremos empezar.")
    else:
        logger.info("User {} started bot".format(username + ':' + str(chat_id)))

        main_menu_keyboard = [[KeyboardButton("Menú"),
                               KeyboardButton("🆘 Ayuda"),
                               KeyboardButton("Información")]]

        reply_kb_markup = ReplyKeyboardMarkup(main_menu_keyboard,
                                              resize_keyboard=True,
                                              one_time_keyboard=False)

        # Sends message with languages menu
        update.message.reply_text(text="¡Bienvenido a Covid-19 Report! {}\n"
                                       "Gracias a este bot podrás conocer el estado de la situación actual provocada por "
                                       "el Covid-19.".format(username),
                                  reply_markup=reply_kb_markup)

    current_state = 'WELCOME'
    return WELCOME


def help_handler(update, context):
    global current_state

    update.message.reply_text(text="Actualmente la ayuda no está disponible")

    current_state = 'HELP'
    return HELP


def any_message_start(update, context):
    update.message.reply_text("Usa /start para iniciar el bot")


def any_message(update, context):
    global current_state

    if current_state == "WELCOME":
        keyboard = [
            [InlineKeyboardButton("Menú Inicial", callback_data='start_menu')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            text="Pulsa el botón para empezar",
            reply_markup=reply_markup
        )
        current_state = 'WELCOME_BAD'
        return WELCOME_BAD
    else:
        update.message.reply_text("No te he entendido. Si es necesario, puedes reiniciarme usando /start")


def show_inicio(update, context):
    global current_state

    if current_state == "WELCOME_BAD" or current_state == "NOT_IMPLEMENTED":
        username = update.callback_query.message.chat.username
        message = update.callback_query.message
    else:
        username = update.message.chat.username
        message = update.message

    keyboard = [
        [InlineKeyboardButton("Andalucía", callback_data='show_not_implemented'),
         InlineKeyboardButton("Aragón", callback_data='show_not_implemented'),
         InlineKeyboardButton("Asturias", callback_data='show_not_implemented')],

        [InlineKeyboardButton("C. Valenciana", callback_data='show_not_implemented'),
         InlineKeyboardButton("Canarias", callback_data='show_not_implemented'),
         InlineKeyboardButton("Cantabria", callback_data='show_not_implemented')],

        [InlineKeyboardButton("Castilla La Mancha", callback_data='show_not_implemented'),
         InlineKeyboardButton("Castilla y León", callback_data='show_not_implemented'),
         InlineKeyboardButton("Cataluña", callback_data='show_not_implemented')],

        [InlineKeyboardButton("Ceuta", callback_data='show_not_implemented'),
         InlineKeyboardButton("Extremadura", callback_data='show_not_implemented'),
         InlineKeyboardButton("Galicia", callback_data='show_not_implemented')],

        [InlineKeyboardButton("Islas Baleares", callback_data='show_not_implemented'),
         InlineKeyboardButton("La Rioja", callback_data='show_not_implemented'),
         InlineKeyboardButton("Madrid", callback_data='show_not_implemented')],

        [InlineKeyboardButton("Melilla", callback_data='show_not_implemented'),
         InlineKeyboardButton("Murcia", callback_data='show_not_implemented'),
         InlineKeyboardButton("Navarra", callback_data='show_not_implemented')],

        [InlineKeyboardButton("País Vasco", callback_data='show_not_implemented'),
         InlineKeyboardButton("Toda España", callback_data='show_not_implemented')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_espana.png', 'rb')
    )

    message.reply_text(
        text="{} elige la provincia de la que quieres consultar datos.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INICIO"
    return INICIO


def show_info(update, context):
    global current_state

    username = update.message.chat.username

    update.message.reply_text(
        text="Este proyecto ha sido desarrollado como Trabajo Fin de Grado\n\n"
             "Este proyecto cuenta con una licencia AGPL, por lo que podeis usarlo si os es útil\n\n"
             "<b>Fuentes de datos</b>\n"
             "Fuentes de datos para España y sus provincias de <a href='https://github.com/datadista/datasets/'>Datadista</a>\n\n"
             "<b>Contacto</b>\n"
             "Puedes ponerte en contacto con el desarrollador @JmZero\n\n"
             "<b>Código Fuente</b>\n"
             "<a href='https://github.com/JmZero/TFG_Covid-19_reports'>Covid-19 Reports</a>\n\n"
        ,
        parse_mode='HTML',
        disable_web_page_preview=True
    )

    current_state = "STATUS_INFO"
    return STATUS_INFO

def usuario_pulsa_boton_anterior(update, context):
    update.callback_query.message.reply_text(
        text="<b>🚫 Acción no permitida. Pulsa un botón del menu actual 🚫</b>",
        parse_mode='HTML'
    )


def show_not_implemented(update, context):
    global current_state

    keyboard = [
        [InlineKeyboardButton("Back", callback_data='start_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_text(
        text="Página no implementada, por favor vuelve atrás",
        reply_markup=reply_markup
    )

    current_state = "NOT_IMPLEMENTED"
    return NOT_IMPLEMENTED


def main():
    global conv_handler

    logger.info("Starting bot")
    updater = Updater(TOKEN)

    conv_handler = ConversationHandler(entry_points=[CommandHandler('start', start_handler),
                                                     MessageHandler(Filters.text & (~Filters.command), any_message_start)],
                                       states={
                                           WELCOME: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_inicio, pattern='start_menu')
                                           ],
                                           WELCOME_BAD: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_inicio, pattern='start_menu')
                                           ],
                                           INICIO: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_not_implemented, pattern='show_not_implemented')
                                           ],
                                           HELP: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           STATUS_INFO: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_not_implemented, pattern='show_not_implemented')
                                           ],
                                           NOT_IMPLEMENTED: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_inicio, pattern='start_menu')
                                           ]
                                       },
                                       fallbacks=[
                                           CommandHandler('start', start_handler),
                                           CommandHandler('help', help_handler),
                                           CommandHandler('info', show_info),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior, pattern='start_menu'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior, pattern='show_not_implemented'),
                                       ])

    updater.dispatcher.add_handler(conv_handler)

    run(updater)


if __name__ == '__main__':
    main()