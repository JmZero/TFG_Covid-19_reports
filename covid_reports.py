import logging
import os
import sys
import pandas as pd
from datetime import date, timedelta, datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler

# Enabling logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

WELCOME, INICIO, HELP, STATUS_INFO, WELCOME_BAD, NOT_IMPLEMENTED, \
INFO_ANDALUCIA, INFO_ANDALUCIA_INCREMENT, INFO_ANDALUCIA_CUMULATIVE, INFO_ANDALUCIA_DEATH, INFO_ANDALUCIA_HOSPITAL, \
INFO_ANDALUCIA_ALL, INFO_ARAGON, INFO_ARAGON_INCREMENT, INFO_ARAGON_CUMULATIVE, INFO_ARAGON_DEATH, \
INFO_ARAGON_HOSPITAL, INFO_ARAGON_ALL, INFO_ASTURIAS, INFO_ASTURIAS_INCREMENT, INFO_ASTURIAS_CUMULATIVE, \
INFO_ASTURIAS_DEATH, INFO_ASTURIAS_HOSPITAL, INFO_ASTURIAS_ALL, INFO_CVALENCIANA, INFO_CVALENCIANA_INCREMENT, \
INFO_CVALENCIANA_CUMULATIVE, INFO_CVALENCIANA_DEATH, INFO_CVALENCIANA_HOSPITAL, INFO_CVALENCIANA_ALL, INFO_CANARIAS, \
INFO_CANARIAS_INCREMENT, INFO_CANARIAS_CUMULATIVE, INFO_CANARIAS_DEATH, INFO_CANARIAS_HOSPITAL, INFO_CANARIAS_ALL, \
INFO_CANTABRIA, INFO_CANTABRIA_INCREMENT, INFO_CANTABRIA_CUMULATIVE, INFO_CANTABRIA_DEATH, INFO_CANTABRIA_HOSPITAL, \
INFO_CANTABRIA_ALL, INFO_CASTILLALAMANCHA, INFO_CASTILLALAMANCHA_INCREMENT, INFO_CASTILLALAMANCHA_CUMULATIVE, \
INFO_CASTILLALAMANCHA_DEATH, INFO_CASTILLALAMANCHA_HOSPITAL, INFO_CASTILLALAMANCHA_ALL, INFO_CASTILLAYLEON, \
INFO_CASTILLAYLEON_INCREMENT, INFO_CASTILLAYLEON_CUMULATIVE, INFO_CASTILLAYLEON_DEATH, INFO_CASTILLAYLEON_HOSPITAL, \
INFO_CASTILLAYLEON_ALL, INFO_CATALUÑA, INFO_CATALUÑA_INCREMENT, INFO_CATALUÑA_CUMULATIVE, INFO_CATALUÑA_DEATH, \
INFO_CATALUÑA_HOSPITAL, INFO_CATALUÑA_ALL, INFO_CEUTA, INFO_CEUTA_INCREMENT, INFO_CEUTA_CUMULATIVE, INFO_CEUTA_DEATH, \
INFO_CEUTA_HOSPITAL, INFO_CEUTA_ALL, INFO_EXTREMADURA, INFO_EXTREMADURA_INCREMENT, INFO_EXTREMADURA_CUMULATIVE, \
INFO_EXTREMADURA_DEATH, INFO_EXTREMADURA_HOSPITAL, INFO_EXTREMADURA_ALL, INFO_GALICIA, INFO_GALICIA_INCREMENT, \
INFO_GALICIA_CUMULATIVE, INFO_GALICIA_DEATH, INFO_GALICIA_HOSPITAL, INFO_GALICIA_ALL, INFO_BALEARES, \
INFO_BALEARES_INCREMENT, INFO_BALEARES_CUMULATIVE, INFO_BALEARES_DEATH, INFO_BALEARES_HOSPITAL, INFO_BALEARES_ALL,  \
INFO_LARIOJA, INFO_LARIOJA_INCREMENT, INFO_LARIOJA_CUMULATIVE, INFO_LARIOJA_DEATH, INFO_LARIOJA_HOSPITAL, \
INFO_LARIOJA_ALL, INFO_MADRID, INFO_MADRID_INCREMENT, INFO_MADRID_CUMULATIVE, INFO_MADRID_DEATH, INFO_MADRID_HOSPITAL, \
INFO_MADRID_ALL, INFO_MELILLA, INFO_MELILLA_INCREMENT, INFO_MELILLA_CUMULATIVE, INFO_MELILLA_DEATH, \
INFO_MELILLA_HOSPITAL, INFO_MELILLA_ALL, INFO_MURCIA, INFO_MURCIA_INCREMENT, INFO_MURCIA_CUMULATIVE, INFO_MURCIA_DEATH, \
INFO_MURCIA_HOSPITAL, INFO_MURCIA_ALL = range(108)


# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")

# Database used in proyect
url_casos = 'https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_datos_isciii_nueva_serie.csv'
util_cols = ['fecha', 'ccaa', 'num_casos']
df_ccaa_casos = pd.read_csv(url_casos, sep=',', usecols=util_cols)

url_muertes = 'https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_fallecidos_por_fecha_defuncion_nueva_serie_original.csv'
df_ccaa_muertes = pd.read_csv(url_muertes, sep=',')

url_hospital = 'https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_ingresos_camas_convencionales_uci.csv'
util_cols = ['Fecha', 'CCAA', 'Total Pacientes COVID ingresados', '% Camas Ocupadas COVID',
             'Total pacientes COVID en UCI', '% Camas Ocupadas UCI COVID', 'Ingresos COVID últimas 24 h',
             'Altas COVID últimas 24 h']
df_ccaa_hospital = pd.read_csv(url_hospital, sep=',', usecols=util_cols)

global current_state, conv_handler, current_autonomy

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
                                       "Gracias a este bot podrás conocer el estado de la situación actual provocada "
                                       "por el Covid-19.".format(username),
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
        [InlineKeyboardButton("Andalucía", callback_data='andalucia_info'),
         InlineKeyboardButton("Aragón", callback_data='aragon_info'),
         InlineKeyboardButton("Asturias", callback_data='asturias_info')],

        [InlineKeyboardButton("C. Valenciana", callback_data='cvalenciana_info'),
         InlineKeyboardButton("Canarias", callback_data='canarias_info'),
         InlineKeyboardButton("Cantabria", callback_data='cantabria_info')],

        [InlineKeyboardButton("Castilla La Mancha", callback_data='castillalamancha_info'),
         InlineKeyboardButton("Castilla y León", callback_data='castillayleon_info'),
         InlineKeyboardButton("Cataluña", callback_data='cataluña_info')],

        [InlineKeyboardButton("Ceuta", callback_data='ceuta_info'),
         InlineKeyboardButton("Extremadura", callback_data='extremadura_info'),
         InlineKeyboardButton("Galicia", callback_data='galicia_info')],

        [InlineKeyboardButton("Islas Baleares", callback_data='baleares_info'),
         InlineKeyboardButton("La Rioja", callback_data='larioja_info'),
         InlineKeyboardButton("Madrid", callback_data='madrid_info')],

        [InlineKeyboardButton("Melilla", callback_data='melilla_info'),
         InlineKeyboardButton("Murcia", callback_data='murcia_info'),
         InlineKeyboardButton("Navarra", callback_data='navarra_info')],

        [InlineKeyboardButton("País Vasco", callback_data='paisvasco_info'),
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


def show_andalucia_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='andalucia_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='andalucia_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='andalucia_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='andalucia_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='andalucia_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_andalucia.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_ANDALUCIA"
    current_autonomy = "Andalucía"
    return INFO_ANDALUCIA


def show_aragon_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='aragon_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='aragon_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='aragon_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='aragon_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='aragon_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_aragon.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_ARAGON"
    current_autonomy = "Aragón"
    return INFO_ARAGON


def show_asturias_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='asturias_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='asturias_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='asturias_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='asturias_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='asturias_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_asturias.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_ASTURIAS"
    current_autonomy = "Asturias"
    return INFO_ASTURIAS


def show_cvalenciana_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='cvalenciana_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='cvalenciana_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='cvalenciana_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='cvalenciana_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='cvalenciana_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_cvalenciana.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_CVALENCIANA"
    current_autonomy = "C. Valenciana"
    return INFO_CVALENCIANA


def show_canarias_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='canarias_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='canarias_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='canarias_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='canarias_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='canarias_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_canarias.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_CANARIAS"
    current_autonomy = "Canarias"
    return INFO_CANARIAS


def show_cantabria_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='cantabria_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='cantabria_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='cantabria_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='cantabria_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='cantabria_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_cantabria.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_CANTABRIA"
    current_autonomy = "Cantabria"
    return INFO_CANTABRIA


def show_castillalamancha_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='castillalamancha_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='castillalamancha_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='castillalamancha_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='castillalamancha_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='castillalamancha_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_castillalamancha.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_CASTILLALAMANCHA"
    current_autonomy = "Castilla La Mancha"
    return INFO_CASTILLALAMANCHA


def show_castillayleon_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='castillayleon_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='castillayleon_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='castillayleon_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='castillayleon_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='castillayleon_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_castillayleon.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_CASTILLAYLEON"
    current_autonomy = "Castilla y León"
    return INFO_CASTILLAYLEON


def show_cataluña_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='cataluña_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='cataluña_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='cataluña_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='cataluña_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='cataluña_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_cataluña.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_CATALUÑA"
    current_autonomy = "Cataluña"
    return INFO_CATALUÑA


def show_ceuta_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='ceuta_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='ceuta_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='ceuta_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='ceuta_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='ceuta_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_ceuta.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_CEUTA"
    current_autonomy = "Ceuta"
    return INFO_CEUTA


def show_extremadura_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='extremadura_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='extremadura_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='extremadura_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='extremadura_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='extremadura_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_extremadura.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_EXTREMADURA"
    current_autonomy = "Extremadura"
    return INFO_EXTREMADURA


def show_galicia_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='galicia_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='galicia_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='galicia_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='galicia_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='galicia_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_galicia.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_GALICIA"
    current_autonomy = "Galicia"
    return INFO_GALICIA


def show_baleares_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='baleares_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='baleares_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='baleares_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='baleares_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='baleares_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_baleares.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_BALEARES"
    current_autonomy = "Baleares"
    return INFO_BALEARES


def show_larioja_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='larioja_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='larioja_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='larioja_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='larioja_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='larioja_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_larioja.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_LARIOJA"
    current_autonomy = "La Rioja"
    return INFO_LARIOJA


def show_madrid_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='madrid_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='madrid_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='madrid_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='madrid_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='madrid_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_madrid.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_MADRID"
    current_autonomy = "Madrid"
    return INFO_MADRID


def show_melilla_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='melilla_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='melilla_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='melilla_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='melilla_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='melilla_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_melilla.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_MELILLA"
    current_autonomy = "Melilla"
    return INFO_MELILLA


def show_murcia_info(update, context):
    global current_state, current_autonomy

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='murcia_increment'),
         InlineKeyboardButton("Casos acumulados", callback_data='murcia_cumulative'),
         InlineKeyboardButton("Fallecimientos", callback_data='murcia_death')],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='murcia_hospital'),
         InlineKeyboardButton("Ver todo", callback_data='murcia_all'),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_murcia.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_MURCIA"
    current_autonomy = "Murcia"
    return INFO_MURCIA


def show_increment(update, context):
    global current_state, current_autonomy

    message = update.callback_query.message

    autonomy_lower = normalize(current_autonomy).lower()
    autonomy_upper = normalize(current_autonomy).upper()

    keyboard = [
        [InlineKeyboardButton("Casos acumulados", callback_data='{}_cumulative'.format(autonomy_lower)),
         InlineKeyboardButton("Fallecimientos", callback_data='{}_death'.format(autonomy_lower)),
         InlineKeyboardButton("Hospitalizaciones", callback_data='{}_hospital'.format(autonomy_lower))],

        [InlineKeyboardButton("Ver todo", callback_data='{}_all'.format(autonomy_lower)),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # message.reply_photo(
    #     photo=open('./img/mapa_andalucia.png', 'rb')
    # )

    message.reply_text(
        text="Incremento de casos en {}\n\n"
             "\t - Casos acumulados: <b>{}</b>.\n"
             "\t - Incremento de casos últimas 24h: <b>{}</b>.\n"
             "\t - Media del incremento de casos semanal: <b>{}</b>.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(current_autonomy,
                                                                         casos_acumulados(current_autonomy),
                                                                         incremento_ultimo_dia(current_autonomy),
                                                                         media_casos_semana(current_autonomy),
                                                                         format_date(fecha_actualizacion(current_autonomy))),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    current_state = "INFO_{}_INCREMENT".format(autonomy_upper)


def show_cumulative(update, context):
    global current_state, current_autonomy

    message = update.callback_query.message

    autonomy_lower = normalize(current_autonomy).lower()
    autonomy_upper = normalize(current_autonomy).upper()

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='{}_increment'.format(autonomy_lower)),
         InlineKeyboardButton("Fallecimientos", callback_data='{}_death'.format(autonomy_lower)),
         InlineKeyboardButton("Hospitalizaciones", callback_data='{}_hospital'.format(autonomy_lower))],

        [InlineKeyboardButton("Ver todo", callback_data='{}_all'.format(autonomy_lower)),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # message.reply_photo(
    #     photo=open('./img/mapa_andalucia.png', 'rb')
    # )

    message.reply_text(
        text="Incremento de casos en {}\n\n"
             "\t - Casos acumulados: <b>{}</b>.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(current_autonomy,
                                                                         casos_acumulados(current_autonomy),
                                                                         format_date(fecha_actualizacion(current_autonomy))),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    current_state = "INFO_{}_CUMULATIVE".format(autonomy_upper)


def show_death(update, context):
    global current_state, current_autonomy

    message = update.callback_query.message

    autonomy_lower = normalize(current_autonomy).lower()
    autonomy_upper = normalize(current_autonomy).upper()

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='{}_increment'.format(autonomy_lower)),
         InlineKeyboardButton("Casos acumulados", callback_data='{}_cumulative'.format(autonomy_lower)),
         InlineKeyboardButton("Hospitalizaciones", callback_data='{}_hospital'.format(autonomy_lower))],

        [InlineKeyboardButton("Ver todo", callback_data='{}_all'.format(autonomy_lower)),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # message.reply_photo(
    #     photo=open('./img/mapa_andalucia.png', 'rb')
    # )

    message.reply_text(
        text="Evolución de fallecimientos en {}\n\n"
             "\t - Fallecimientos totales: <b>{}</b>.\n"
             "\t - Fallecidos últimas 24h: <b>{}</b>.\n"
             "\t - Media fallecimientos semanal: <b>{}</b>.\n"
             "\t - Tasa de letalidad: <b>{}</b>.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(current_autonomy,
                                                                         muertes_totales(current_autonomy),
                                                                         muertes_ultimo_dia(current_autonomy),
                                                                         media_muertes_semana(current_autonomy),
                                                                         tasa_letalidad(current_autonomy),
                                                                         format_date(fecha_actualizacion_muertes())),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    current_state = "INFO_{}_DEATH".format(autonomy_upper)


def show_hospital(update, context):
    global current_state, current_autonomy

    message = update.callback_query.message

    autonomy_lower = normalize(current_autonomy).lower()
    autonomy_upper = normalize(current_autonomy).upper()

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='{}_increment'.format(autonomy_lower)),
         InlineKeyboardButton("Casos acumulados", callback_data='{}_cumulative'.format(autonomy_lower)),
         InlineKeyboardButton("Fallecimientos", callback_data='{}_death'.format(autonomy_lower))],

        [InlineKeyboardButton("Ver todo", callback_data='{}_all'.format(autonomy_lower)),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # message.reply_photo(
    #     photo=open('./img/mapa_andalucia.png', 'rb')
    # )

    message.reply_text(
        text="Datos de hospitalización por COVID en {}\n\n"
             "\t - Pacientes ingresados actualmente: <b>{}</b>.\n"
             "\t - Camas ocupadas actualmente (%): <b>{}</b>.\n"
             "\t - Pacientes ingresados en UCI actualmente: <b>{}</b>.\n"
             "\t - Camas ocupadas en UCI actualmente (%): <b>{}</b>.\n"
             "\t - Pacientes ingresados últimas 24h: <b>{}</b>.\n"
             "\t - Pacientes dados de alta últimas 24h: <b>{}</b>.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(current_autonomy,
                                                                         pacientes_ingresados(current_autonomy),
                                                                         porcentaje_camas_ocupadas(current_autonomy),
                                                                         pacientes_ingresados_uci(current_autonomy),
                                                                         porcentaje_camas_uci_ocupadas(current_autonomy),
                                                                         ingresados_ultimo_dia(current_autonomy),
                                                                         altas_ultimo_dia(current_autonomy),
                                                                         format_date(fecha_actualizacion_hospital(current_autonomy))),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    current_state = "INFO_{}_HOSPITAL".format(autonomy_upper)


def show_all_info(update, context):
    global current_state, current_autonomy

    message = update.callback_query.message

    autonomy_lower = normalize(current_autonomy).lower()
    autonomy_upper = normalize(current_autonomy).upper()

    keyboard = [
        [InlineKeyboardButton("Incremento", callback_data='{}_increment'.format(autonomy_lower)),
         InlineKeyboardButton("Casos acumulados", callback_data='{}_cumulative'.format(autonomy_lower)),
         InlineKeyboardButton("Fallecimientos", callback_data='{}_death'.format(autonomy_lower))],

        [InlineKeyboardButton("Hospitalizaciones", callback_data='{}_hospital'.format(autonomy_lower)),
         InlineKeyboardButton("Consultar por provincia", callback_data='show_not_implemented')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # message.reply_photo(
    #     photo=open('./img/mapa_andalucia.png', 'rb')
    # )

    message.reply_text(
        text="Incremento de casos en {}\n\n"
             "\t - Casos acumulados: <b>{}</b>.\n"
             "\t - Incremento de casos últimas 24h: <b>{}</b>.\n"
             "\t - Media del incremento de casos semanal: <b>{}</b>.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(current_autonomy,
                                                                         casos_acumulados(current_autonomy),
                                                                         incremento_ultimo_dia(current_autonomy),
                                                                         media_casos_semana(current_autonomy),
                                                                         format_date(fecha_actualizacion(current_autonomy))),
        parse_mode='HTML',
    )

    # message.reply_photo(
    #     photo=open('./img/mapa_andalucia.png', 'rb')
    # )

    message.reply_text(
        text="Incremento de casos en {}\n\n"
             "\t - Casos acumulados: <b>{}</b>.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(current_autonomy,
                                                                         casos_acumulados(current_autonomy),
                                                                         format_date(fecha_actualizacion(current_autonomy))),
        parse_mode='HTML',
    )

    # message.reply_photo(
    #     photo=open('./img/mapa_andalucia.png', 'rb')
    # )

    message.reply_text(
        text="Evolución de fallecimientos en {}\n\n"
             "\t - Fallecimientos totales: <b>{}</b>.\n"
             "\t - Fallecidos últimas 24h: <b>{}</b>.\n"
             "\t - Media fallecimientos semanal: <b>{}</b>.\n"
             "\t - Tasa de letalidad: <b>{}</b>.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(current_autonomy,
                                                                         muertes_totales(current_autonomy),
                                                                         muertes_ultimo_dia(current_autonomy),
                                                                         media_muertes_semana(current_autonomy),
                                                                         tasa_letalidad(current_autonomy),
                                                                         format_date(fecha_actualizacion_muertes())),
        parse_mode='HTML',
    )

    # message.reply_photo(
    #     photo=open('./img/mapa_andalucia.png', 'rb')
    # )

    message.reply_text(
        text="Datos de hospitalización por COVID en {}\n\n"
             "\t - Pacientes ingresados actualmente: <b>{}</b>.\n"
             "\t - Camas ocupadas actualmente (%): <b>{}</b>.\n"
             "\t - Pacientes ingresados en UCI actualmente: <b>{}</b>.\n"
             "\t - Camas ocupadas en UCI actualmente (%): <b>{}</b>.\n"
             "\t - Pacientes ingresados últimas 24h: <b>{}</b>.\n"
             "\t - Pacientes dados de alta últimas 24h: <b>{}</b>.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(current_autonomy,
                                                                         pacientes_ingresados(current_autonomy),
                                                                         porcentaje_camas_ocupadas(current_autonomy),
                                                                         pacientes_ingresados_uci(current_autonomy),
                                                                         porcentaje_camas_uci_ocupadas(current_autonomy),
                                                                         ingresados_ultimo_dia(current_autonomy),
                                                                         altas_ultimo_dia(current_autonomy),
                                                                         format_date(fecha_actualizacion_hospital(current_autonomy))),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    current_state = "INFO_{}_ALL".format(autonomy_upper)


# ANDALUCÍA
def show_andalucia_increment(update, context):
    show_increment(update, context)

    return INFO_ANDALUCIA_INCREMENT


def show_andalucia_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_ANDALUCIA_CUMULATIVE


def show_andalucia_death(update, context):
    show_death(update, context)

    return INFO_ANDALUCIA_DEATH


def show_andalucia_hospital(update, context):
    show_hospital(update, context)

    return INFO_ANDALUCIA_HOSPITAL


def show_andalucia_all(update, context):
    show_all_info(update, context)

    return INFO_ANDALUCIA_ALL


# ARAGÓN
def show_aragon_increment(update, context):
    show_increment(update, context)

    return INFO_ARAGON_INCREMENT


def show_aragon_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_ARAGON_CUMULATIVE


def show_aragon_death(update, context):
    show_death(update, context)

    return INFO_ARAGON_DEATH


def show_aragon_hospital(update, context):
    show_hospital(update, context)

    return INFO_ARAGON_HOSPITAL


def show_aragon_all(update, context):
    show_all_info(update, context)

    return INFO_ARAGON_ALL


# ASTURIAS
def show_asturias_increment(update, context):
    show_increment(update, context)

    return INFO_ASTURIAS_INCREMENT


def show_asturias_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_ASTURIAS_CUMULATIVE


def show_asturias_death(update, context):
    show_death(update, context)

    return INFO_ASTURIAS_DEATH


def show_asturias_hospital(update, context):
    show_hospital(update, context)

    return INFO_ASTURIAS_HOSPITAL


def show_asturias_all(update, context):
    show_all_info(update, context)

    return INFO_ASTURIAS_ALL


# C. VALENCIANA
def show_cvalenciana_increment(update, context):
    show_increment(update, context)

    return INFO_CVALENCIANA_INCREMENT


def show_cvalenciana_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_CVALENCIANA_CUMULATIVE


def show_cvalenciana_death(update, context):
    show_death(update, context)

    return INFO_CVALENCIANA_DEATH


def show_cvalenciana_hospital(update, context):
    show_hospital(update, context)

    return INFO_CVALENCIANA_HOSPITAL


def show_cvalenciana_all(update, context):
    show_all_info(update, context)

    return INFO_CVALENCIANA_ALL


# CANARIAS
def show_canarias_increment(update, context):
    show_increment(update, context)

    return INFO_CANARIAS_INCREMENT


def show_canarias_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_CANARIAS_CUMULATIVE


def show_canarias_death(update, context):
    show_death(update, context)

    return INFO_CANARIAS_DEATH


def show_canarias_hospital(update, context):
    show_hospital(update, context)

    return INFO_CANARIAS_HOSPITAL


def show_canarias_all(update, context):
    show_all_info(update, context)

    return INFO_CANARIAS_ALL


# CANTABRIA
def show_cantabria_increment(update, context):
    show_increment(update, context)

    return INFO_CANTABRIA_INCREMENT


def show_cantabria_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_CANTABRIA_CUMULATIVE


def show_cantabria_death(update, context):
    show_death(update, context)

    return INFO_CANTABRIA_DEATH


def show_cantabria_hospital(update, context):
    show_hospital(update, context)

    return INFO_CANTABRIA_HOSPITAL


def show_cantabria_all(update, context):
    show_all_info(update, context)

    return INFO_CANTABRIA_ALL


# CASTILLA LA MANCHA
def show_castillalamancha_increment(update, context):
    show_increment(update, context)

    return INFO_CASTILLALAMANCHA_INCREMENT


def show_castillalamancha_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_CASTILLALAMANCHA_CUMULATIVE


def show_castillalamancha_death(update, context):
    show_death(update, context)

    return INFO_CASTILLALAMANCHA_DEATH


def show_castillalamancha_hospital(update, context):
    show_hospital(update, context)

    return INFO_CASTILLALAMANCHA_HOSPITAL


def show_castillalamancha_all(update, context):
    show_all_info(update, context)

    return INFO_CASTILLALAMANCHA_ALL


# CASTILLA Y LEON
def show_castillayleon_increment(update, context):
    show_increment(update, context)

    return INFO_CASTILLAYLEON_INCREMENT


def show_castillayleon_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_CASTILLAYLEON_CUMULATIVE


def show_castillayleon_death(update, context):
    show_death(update, context)

    return INFO_CASTILLAYLEON_DEATH


def show_castillayleon_hospital(update, context):
    show_hospital(update, context)

    return INFO_CASTILLAYLEON_HOSPITAL


def show_castillayleon_all(update, context):
    show_all_info(update, context)

    return INFO_CASTILLAYLEON_ALL


# CATALUÑA
def show_cataluña_increment(update, context):
    show_increment(update, context)

    return INFO_CATALUÑA_INCREMENT


def show_cataluña_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_CATALUÑA_CUMULATIVE


def show_cataluña_death(update, context):
    show_death(update, context)

    return INFO_CATALUÑA_DEATH


def show_cataluña_hospital(update, context):
    show_hospital(update, context)

    return INFO_CATALUÑA_HOSPITAL


def show_cataluña_all(update, context):
    show_all_info(update, context)

    return INFO_CATALUÑA_ALL


# CEUTA
def show_ceuta_increment(update, context):
    show_increment(update, context)

    return INFO_CEUTA_INCREMENT


def show_ceuta_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_CEUTA_CUMULATIVE


def show_ceuta_death(update, context):
    show_death(update, context)

    return INFO_CEUTA_DEATH


def show_ceuta_hospital(update, context):
    show_hospital(update, context)

    return INFO_CEUTA_HOSPITAL


def show_ceuta_all(update, context):
    show_all_info(update, context)

    return INFO_CEUTA_ALL


# EXTREMADURA
def show_extremadura_increment(update, context):
    show_increment(update, context)

    return INFO_EXTREMADURA_INCREMENT


def show_extremadura_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_EXTREMADURA_CUMULATIVE


def show_extremadura_death(update, context):
    show_death(update, context)

    return INFO_EXTREMADURA_DEATH


def show_extremadura_hospital(update, context):
    show_hospital(update, context)

    return INFO_EXTREMADURA_HOSPITAL


def show_extremadura_all(update, context):
    show_all_info(update, context)

    return INFO_EXTREMADURA_ALL


# GALICIA
def show_galicia_increment(update, context):
    show_increment(update, context)

    return INFO_GALICIA_INCREMENT


def show_galicia_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_GALICIA_CUMULATIVE


def show_galicia_death(update, context):
    show_death(update, context)

    return INFO_GALICIA_DEATH


def show_galicia_hospital(update, context):
    show_hospital(update, context)

    return INFO_GALICIA_HOSPITAL


def show_galicia_all(update, context):
    show_all_info(update, context)

    return INFO_GALICIA_ALL


# BALEARES
def show_baleares_increment(update, context):
    show_increment(update, context)

    return INFO_BALEARES_INCREMENT


def show_baleares_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_BALEARES_CUMULATIVE


def show_baleares_death(update, context):
    show_death(update, context)

    return INFO_BALEARES_DEATH


def show_baleares_hospital(update, context):
    show_hospital(update, context)

    return INFO_BALEARES_HOSPITAL


def show_baleares_all(update, context):
    show_all_info(update, context)

    return INFO_BALEARES_ALL


# LA RIOJA
def show_larioja_increment(update, context):
    show_increment(update, context)

    return INFO_LARIOJA_INCREMENT


def show_larioja_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_LARIOJA_CUMULATIVE


def show_larioja_death(update, context):
    show_death(update, context)

    return INFO_LARIOJA_DEATH


def show_larioja_hospital(update, context):
    show_hospital(update, context)

    return INFO_LARIOJA_HOSPITAL


def show_larioja_all(update, context):
    show_all_info(update, context)

    return INFO_LARIOJA_ALL


# MADRID
def show_madrid_increment(update, context):
    show_increment(update, context)

    return INFO_MADRID_INCREMENT


def show_madrid_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_MADRID_CUMULATIVE


def show_madrid_death(update, context):
    show_death(update, context)

    return INFO_MADRID_DEATH


def show_madrid_hospital(update, context):
    show_hospital(update, context)

    return INFO_MADRID_HOSPITAL


def show_madrid_all(update, context):
    show_all_info(update, context)

    return INFO_MADRID_ALL


# MELILLA
def show_melilla_increment(update, context):
    show_increment(update, context)

    return INFO_MELILLA_INCREMENT


def show_melilla_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_MELILLA_CUMULATIVE


def show_melilla_death(update, context):
    show_death(update, context)

    return INFO_MELILLA_DEATH


def show_melilla_hospital(update, context):
    show_hospital(update, context)

    return INFO_MELILLA_HOSPITAL


def show_melilla_all(update, context):
    show_all_info(update, context)

    return INFO_MELILLA_ALL


# MURCIA
def show_murcia_increment(update, context):
    show_increment(update, context)

    return INFO_MURCIA_INCREMENT


def show_murcia_cumulative(update, context):
    show_cumulative(update, context)

    return INFO_MURCIA_CUMULATIVE


def show_murcia_death(update, context):
    show_death(update, context)

    return INFO_MURCIA_DEATH


def show_murcia_hospital(update, context):
    show_hospital(update, context)

    return INFO_MURCIA_HOSPITAL


def show_murcia_all(update, context):
    show_all_info(update, context)

    return INFO_MURCIA_ALL


def show_info(update, context):
    global current_state

    update.message.reply_text(
        text="Este proyecto ha sido desarrollado como Trabajo Fin de Grado\n\n"
             "Este proyecto cuenta con una licencia AGPL, por lo que podeis usarlo si os es útil\n\n"
             "<b>Fuentes de datos</b>\n"
             "Fuentes de datos para España y sus provincias de "
             "<a href='https://github.com/datadista/datasets/'>Datadista</a>\n\n"
             "<b>Contacto</b>\n"
             "Puedes ponerte en contacto con el desarrollador @JmZero\n\n"
             "<b>Código Fuente</b>\n"
             "<a href='https://github.com/JmZero/TFG_Covid-19_reports'>Covid-19 Reports</a>\n\n",
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


def normalize(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        (" ", ""),
        (".", ""),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s


def main():
    global conv_handler

    logger.info("Starting bot")
    updater = Updater(TOKEN)

    conv_handler = ConversationHandler(entry_points=[CommandHandler('start', start_handler),
                                                     MessageHandler(Filters.text & (~Filters.command),
                                                                    any_message_start)],
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
                                               CallbackQueryHandler(show_andalucia_info, pattern='andalucia_info'),
                                               CallbackQueryHandler(show_aragon_info, pattern='aragon_info'),
                                               CallbackQueryHandler(show_asturias_info, pattern='asturias_info'),
                                               CallbackQueryHandler(show_cvalenciana_info, pattern='cvalenciana_info'),
                                               CallbackQueryHandler(show_canarias_info, pattern='canarias_info'),
                                               CallbackQueryHandler(show_cantabria_info, pattern='cantabria_info'),
                                               CallbackQueryHandler(show_castillalamancha_info, pattern='castillalamancha_info'),
                                               CallbackQueryHandler(show_castillayleon_info, pattern='castillayleon_info'),
                                               CallbackQueryHandler(show_cataluña_info, pattern='cataluña_info'),
                                               CallbackQueryHandler(show_ceuta_info, pattern='ceuta_info'),
                                               CallbackQueryHandler(show_extremadura_info, pattern='extremadura_info'),
                                               CallbackQueryHandler(show_galicia_info, pattern='galicia_info'),
                                               CallbackQueryHandler(show_baleares_info, pattern='baleares_info'),
                                               CallbackQueryHandler(show_larioja_info, pattern='larioja_info'),
                                               CallbackQueryHandler(show_madrid_info, pattern='madrid_info'),
                                               CallbackQueryHandler(show_melilla_info, pattern='melilla_info'),
                                               CallbackQueryHandler(show_murcia_info, pattern='murcia_info'),
                                               # CallbackQueryHandler(show_navarra_info, pattern='navarra_info'),
                                               # CallbackQueryHandler(show_paisvasco_info, pattern='paisvasco_info'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           HELP: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_not_implemented, pattern='show_not_implemented')
                                           ],
                                           STATUS_INFO: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_not_implemented, pattern='show_not_implemented')
                                           ],
                                           INFO_ANDALUCIA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_andalucia_increment,
                                                                    pattern='andalucia_increment'),
                                               CallbackQueryHandler(show_andalucia_cumulative,
                                                                    pattern='andalucia_cumulative'),
                                               CallbackQueryHandler(show_andalucia_death,
                                                                    pattern='andalucia_death'),
                                               CallbackQueryHandler(show_andalucia_hospital,
                                                                    pattern='andalucia_hospital'),
                                               CallbackQueryHandler(show_andalucia_all,
                                                                    pattern='andalucia_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ANDALUCIA_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_andalucia_cumulative,
                                                                    pattern='andalucia_cumulative'),
                                               CallbackQueryHandler(show_andalucia_death,
                                                                    pattern='andalucia_death'),
                                               CallbackQueryHandler(show_andalucia_hospital,
                                                                    pattern='andalucia_hospital'),
                                               CallbackQueryHandler(show_andalucia_all,
                                                                    pattern='andalucia_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ANDALUCIA_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_andalucia_increment,
                                                                    pattern='andalucia_increment'),
                                               CallbackQueryHandler(show_andalucia_death,
                                                                    pattern='andalucia_death'),
                                               CallbackQueryHandler(show_andalucia_hospital,
                                                                    pattern='andalucia_hospital'),
                                               CallbackQueryHandler(show_andalucia_all,
                                                                    pattern='andalucia_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ANDALUCIA_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_andalucia_increment,
                                                                    pattern='andalucia_increment'),
                                               CallbackQueryHandler(show_andalucia_cumulative,
                                                                    pattern='andalucia_cumulative'),
                                               CallbackQueryHandler(show_andalucia_hospital,
                                                                    pattern='andalucia_hospital'),
                                               CallbackQueryHandler(show_andalucia_all,
                                                                    pattern='andalucia_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ANDALUCIA_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_andalucia_increment,
                                                                    pattern='andalucia_increment'),
                                               CallbackQueryHandler(show_andalucia_cumulative,
                                                                    pattern='andalucia_cumulative'),
                                               CallbackQueryHandler(show_andalucia_death,
                                                                    pattern='andalucia_death'),
                                               CallbackQueryHandler(show_andalucia_all,
                                                                    pattern='andalucia_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ANDALUCIA_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_andalucia_increment,
                                                                    pattern='andalucia_increment'),
                                               CallbackQueryHandler(show_andalucia_cumulative,
                                                                    pattern='andalucia_cumulative'),
                                               CallbackQueryHandler(show_andalucia_death,
                                                                    pattern='andalucia_death'),
                                               CallbackQueryHandler(show_andalucia_hospital,
                                                                    pattern='andalucia_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ARAGON: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_aragon_increment,
                                                                    pattern='aragon_increment'),
                                               CallbackQueryHandler(show_aragon_cumulative,
                                                                    pattern='aragon_cumulative'),
                                               CallbackQueryHandler(show_aragon_death,
                                                                    pattern='aragon_death'),
                                               CallbackQueryHandler(show_aragon_hospital,
                                                                    pattern='aragon_hospital'),
                                               CallbackQueryHandler(show_aragon_all,
                                                                    pattern='aragon_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ARAGON_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_aragon_cumulative,
                                                                    pattern='aragon_cumulative'),
                                               CallbackQueryHandler(show_aragon_death,
                                                                    pattern='aragon_death'),
                                               CallbackQueryHandler(show_aragon_hospital,
                                                                    pattern='aragon_hospital'),
                                               CallbackQueryHandler(show_aragon_all,
                                                                    pattern='aragon_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ARAGON_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_aragon_increment,
                                                                    pattern='aragon_increment'),
                                               CallbackQueryHandler(show_aragon_death,
                                                                    pattern='aragon_death'),
                                               CallbackQueryHandler(show_aragon_hospital,
                                                                    pattern='aragon_hospital'),
                                               CallbackQueryHandler(show_aragon_all,
                                                                    pattern='aragon_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ARAGON_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_aragon_increment,
                                                                    pattern='aragon_increment'),
                                               CallbackQueryHandler(show_aragon_cumulative,
                                                                    pattern='aragon_cumulative'),
                                               CallbackQueryHandler(show_aragon_hospital,
                                                                    pattern='aragon_hospital'),
                                               CallbackQueryHandler(show_aragon_all,
                                                                    pattern='aragon_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ARAGON_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_aragon_increment,
                                                                    pattern='aragon_increment'),
                                               CallbackQueryHandler(show_aragon_cumulative,
                                                                    pattern='aragon_cumulative'),
                                               CallbackQueryHandler(show_aragon_death,
                                                                    pattern='aragon_death'),
                                               CallbackQueryHandler(show_aragon_all,
                                                                    pattern='aragon_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ARAGON_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_aragon_increment,
                                                                    pattern='aragon_increment'),
                                               CallbackQueryHandler(show_aragon_cumulative,
                                                                    pattern='aragon_cumulative'),
                                               CallbackQueryHandler(show_aragon_death,
                                                                    pattern='aragon_death'),
                                               CallbackQueryHandler(show_aragon_hospital,
                                                                    pattern='aragon_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ASTURIAS: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_asturias_increment,
                                                                    pattern='asturias_increment'),
                                               CallbackQueryHandler(show_asturias_cumulative,
                                                                    pattern='asturias_cumulative'),
                                               CallbackQueryHandler(show_asturias_death,
                                                                    pattern='asturias_death'),
                                               CallbackQueryHandler(show_asturias_hospital,
                                                                    pattern='asturias_hospital'),
                                               CallbackQueryHandler(show_asturias_all,
                                                                    pattern='asturias_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ASTURIAS_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_asturias_cumulative,
                                                                    pattern='asturias_cumulative'),
                                               CallbackQueryHandler(show_asturias_death,
                                                                    pattern='asturias_death'),
                                               CallbackQueryHandler(show_asturias_hospital,
                                                                    pattern='asturias_hospital'),
                                               CallbackQueryHandler(show_asturias_all,
                                                                    pattern='asturias_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ASTURIAS_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_asturias_increment,
                                                                    pattern='asturias_increment'),
                                               CallbackQueryHandler(show_asturias_death,
                                                                    pattern='asturias_death'),
                                               CallbackQueryHandler(show_asturias_hospital,
                                                                    pattern='asturias_hospital'),
                                               CallbackQueryHandler(show_asturias_all,
                                                                    pattern='asturias_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ASTURIAS_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_asturias_increment,
                                                                    pattern='asturias_increment'),
                                               CallbackQueryHandler(show_asturias_cumulative,
                                                                    pattern='asturias_cumulative'),
                                               CallbackQueryHandler(show_asturias_hospital,
                                                                    pattern='asturias_hospital'),
                                               CallbackQueryHandler(show_asturias_all,
                                                                    pattern='asturias_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ASTURIAS_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_asturias_increment,
                                                                    pattern='asturias_increment'),
                                               CallbackQueryHandler(show_asturias_cumulative,
                                                                    pattern='asturias_cumulative'),
                                               CallbackQueryHandler(show_asturias_death,
                                                                    pattern='asturias_death'),
                                               CallbackQueryHandler(show_asturias_all,
                                                                    pattern='asturias_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_ASTURIAS_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_asturias_increment,
                                                                    pattern='asturias_increment'),
                                               CallbackQueryHandler(show_asturias_cumulative,
                                                                    pattern='asturias_cumulative'),
                                               CallbackQueryHandler(show_asturias_death,
                                                                    pattern='asturias_death'),
                                               CallbackQueryHandler(show_asturias_hospital,
                                                                    pattern='asturias_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CVALENCIANA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cvalenciana_increment,
                                                                    pattern='cvalenciana_increment'),
                                               CallbackQueryHandler(show_cvalenciana_cumulative,
                                                                    pattern='cvalenciana_cumulative'),
                                               CallbackQueryHandler(show_cvalenciana_death,
                                                                    pattern='cvalenciana_death'),
                                               CallbackQueryHandler(show_cvalenciana_hospital,
                                                                    pattern='cvalenciana_hospital'),
                                               CallbackQueryHandler(show_cvalenciana_all,
                                                                    pattern='cvalenciana_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CVALENCIANA_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cvalenciana_cumulative,
                                                                    pattern='cvalenciana_cumulative'),
                                               CallbackQueryHandler(show_cvalenciana_death,
                                                                    pattern='cvalenciana_death'),
                                               CallbackQueryHandler(show_cvalenciana_hospital,
                                                                    pattern='cvalenciana_hospital'),
                                               CallbackQueryHandler(show_cvalenciana_all,
                                                                    pattern='cvalenciana_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CVALENCIANA_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cvalenciana_increment,
                                                                    pattern='cvalenciana_increment'),
                                               CallbackQueryHandler(show_cvalenciana_death,
                                                                    pattern='cvalenciana_death'),
                                               CallbackQueryHandler(show_cvalenciana_hospital,
                                                                    pattern='cvalenciana_hospital'),
                                               CallbackQueryHandler(show_cvalenciana_all,
                                                                    pattern='cvalenciana_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CVALENCIANA_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cvalenciana_increment,
                                                                    pattern='cvalenciana_increment'),
                                               CallbackQueryHandler(show_cvalenciana_cumulative,
                                                                    pattern='cvalenciana_cumulative'),
                                               CallbackQueryHandler(show_cvalenciana_hospital,
                                                                    pattern='cvalenciana_hospital'),
                                               CallbackQueryHandler(show_cvalenciana_all,
                                                                    pattern='cvalenciana_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CVALENCIANA_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cvalenciana_increment,
                                                                    pattern='cvalenciana_increment'),
                                               CallbackQueryHandler(show_cvalenciana_cumulative,
                                                                    pattern='cvalenciana_cumulative'),
                                               CallbackQueryHandler(show_cvalenciana_death,
                                                                    pattern='cvalenciana_death'),
                                               CallbackQueryHandler(show_cvalenciana_all,
                                                                    pattern='cvalenciana_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CVALENCIANA_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cvalenciana_increment,
                                                                    pattern='cvalenciana_increment'),
                                               CallbackQueryHandler(show_cvalenciana_cumulative,
                                                                    pattern='cvalenciana_cumulative'),
                                               CallbackQueryHandler(show_cvalenciana_death,
                                                                    pattern='cvalenciana_death'),
                                               CallbackQueryHandler(show_cvalenciana_hospital,
                                                                    pattern='cvalenciana_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CANARIAS: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_canarias_increment,
                                                                    pattern='canarias_increment'),
                                               CallbackQueryHandler(show_canarias_cumulative,
                                                                    pattern='canarias_cumulative'),
                                               CallbackQueryHandler(show_canarias_death,
                                                                    pattern='canarias_death'),
                                               CallbackQueryHandler(show_canarias_hospital,
                                                                    pattern='canarias_hospital'),
                                               CallbackQueryHandler(show_canarias_all,
                                                                    pattern='canarias_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CANARIAS_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_canarias_cumulative,
                                                                    pattern='canarias_cumulative'),
                                               CallbackQueryHandler(show_canarias_death,
                                                                    pattern='canarias_death'),
                                               CallbackQueryHandler(show_canarias_hospital,
                                                                    pattern='canarias_hospital'),
                                               CallbackQueryHandler(show_canarias_all,
                                                                    pattern='canarias_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CANARIAS_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_canarias_increment,
                                                                    pattern='canarias_increment'),
                                               CallbackQueryHandler(show_canarias_death,
                                                                    pattern='canarias_death'),
                                               CallbackQueryHandler(show_canarias_hospital,
                                                                    pattern='canarias_hospital'),
                                               CallbackQueryHandler(show_canarias_all,
                                                                    pattern='canarias_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CANARIAS_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_canarias_increment,
                                                                    pattern='canarias_increment'),
                                               CallbackQueryHandler(show_canarias_cumulative,
                                                                    pattern='canarias_cumulative'),
                                               CallbackQueryHandler(show_canarias_hospital,
                                                                    pattern='canarias_hospital'),
                                               CallbackQueryHandler(show_canarias_all,
                                                                    pattern='canarias_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CANARIAS_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_canarias_increment,
                                                                    pattern='canarias_increment'),
                                               CallbackQueryHandler(show_canarias_cumulative,
                                                                    pattern='canarias_cumulative'),
                                               CallbackQueryHandler(show_canarias_death,
                                                                    pattern='canarias_death'),
                                               CallbackQueryHandler(show_canarias_all,
                                                                    pattern='canarias_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CANARIAS_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_canarias_increment,
                                                                    pattern='canarias_increment'),
                                               CallbackQueryHandler(show_canarias_cumulative,
                                                                    pattern='canarias_cumulative'),
                                               CallbackQueryHandler(show_canarias_death,
                                                                    pattern='canarias_death'),
                                               CallbackQueryHandler(show_canarias_hospital,
                                                                    pattern='canarias_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CANTABRIA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cantabria_increment,
                                                                    pattern='cantabria_increment'),
                                               CallbackQueryHandler(show_cantabria_cumulative,
                                                                    pattern='cantabria_cumulative'),
                                               CallbackQueryHandler(show_cantabria_death,
                                                                    pattern='cantabria_death'),
                                               CallbackQueryHandler(show_cantabria_hospital,
                                                                    pattern='cantabria_hospital'),
                                               CallbackQueryHandler(show_cantabria_all,
                                                                    pattern='cantabria_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CANTABRIA_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cantabria_cumulative,
                                                                    pattern='cantabria_cumulative'),
                                               CallbackQueryHandler(show_cantabria_death,
                                                                    pattern='cantabria_death'),
                                               CallbackQueryHandler(show_cantabria_hospital,
                                                                    pattern='cantabria_hospital'),
                                               CallbackQueryHandler(show_cantabria_all,
                                                                    pattern='cantabria_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CANTABRIA_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cantabria_increment,
                                                                    pattern='cantabria_increment'),
                                               CallbackQueryHandler(show_cantabria_death,
                                                                    pattern='cantabria_death'),
                                               CallbackQueryHandler(show_cantabria_hospital,
                                                                    pattern='cantabria_hospital'),
                                               CallbackQueryHandler(show_cantabria_all,
                                                                    pattern='cantabria_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CANTABRIA_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cantabria_increment,
                                                                    pattern='cantabria_increment'),
                                               CallbackQueryHandler(show_cantabria_cumulative,
                                                                    pattern='cantabria_cumulative'),
                                               CallbackQueryHandler(show_cantabria_hospital,
                                                                    pattern='cantabria_hospital'),
                                               CallbackQueryHandler(show_cantabria_all,
                                                                    pattern='cantabria_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CANTABRIA_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cantabria_increment,
                                                                    pattern='cantabria_increment'),
                                               CallbackQueryHandler(show_cantabria_cumulative,
                                                                    pattern='cantabria_cumulative'),
                                               CallbackQueryHandler(show_cantabria_death,
                                                                    pattern='cantabria_death'),
                                               CallbackQueryHandler(show_cantabria_all,
                                                                    pattern='cantabria_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CANTABRIA_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cantabria_increment,
                                                                    pattern='cantabria_increment'),
                                               CallbackQueryHandler(show_cantabria_cumulative,
                                                                    pattern='cantabria_cumulative'),
                                               CallbackQueryHandler(show_cantabria_death,
                                                                    pattern='cantabria_death'),
                                               CallbackQueryHandler(show_cantabria_hospital,
                                                                    pattern='cantabria_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CASTILLALAMANCHA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_castillalamancha_increment,
                                                                    pattern='castillalamancha_increment'),
                                               CallbackQueryHandler(show_castillalamancha_cumulative,
                                                                    pattern='castillalamancha_cumulative'),
                                               CallbackQueryHandler(show_castillalamancha_death,
                                                                    pattern='castillalamancha_death'),
                                               CallbackQueryHandler(show_castillalamancha_hospital,
                                                                    pattern='castillalamancha_hospital'),
                                               CallbackQueryHandler(show_castillalamancha_all,
                                                                    pattern='castillalamancha_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CASTILLALAMANCHA_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_castillalamancha_cumulative,
                                                                    pattern='castillalamancha_cumulative'),
                                               CallbackQueryHandler(show_castillalamancha_death,
                                                                    pattern='castillalamancha_death'),
                                               CallbackQueryHandler(show_castillalamancha_hospital,
                                                                    pattern='castillalamancha_hospital'),
                                               CallbackQueryHandler(show_castillalamancha_all,
                                                                    pattern='castillalamancha_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CASTILLALAMANCHA_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_castillalamancha_increment,
                                                                    pattern='castillalamancha_increment'),
                                               CallbackQueryHandler(show_castillalamancha_death,
                                                                    pattern='castillalamancha_death'),
                                               CallbackQueryHandler(show_castillalamancha_hospital,
                                                                    pattern='castillalamancha_hospital'),
                                               CallbackQueryHandler(show_castillalamancha_all,
                                                                    pattern='castillalamancha_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CASTILLALAMANCHA_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_castillalamancha_increment,
                                                                    pattern='castillalamancha_increment'),
                                               CallbackQueryHandler(show_castillalamancha_cumulative,
                                                                    pattern='castillalamancha_cumulative'),
                                               CallbackQueryHandler(show_castillalamancha_hospital,
                                                                    pattern='castillalamancha_hospital'),
                                               CallbackQueryHandler(show_castillalamancha_all,
                                                                    pattern='castillalamancha_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CASTILLALAMANCHA_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_castillalamancha_increment,
                                                                    pattern='castillalamancha_increment'),
                                               CallbackQueryHandler(show_castillalamancha_cumulative,
                                                                    pattern='castillalamancha_cumulative'),
                                               CallbackQueryHandler(show_castillalamancha_death,
                                                                    pattern='castillalamancha_death'),
                                               CallbackQueryHandler(show_castillalamancha_all,
                                                                    pattern='castillalamancha_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CASTILLALAMANCHA_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_castillalamancha_increment,
                                                                    pattern='castillalamancha_increment'),
                                               CallbackQueryHandler(show_castillalamancha_cumulative,
                                                                    pattern='castillalamancha_cumulative'),
                                               CallbackQueryHandler(show_castillalamancha_death,
                                                                    pattern='castillalamancha_death'),
                                               CallbackQueryHandler(show_castillalamancha_hospital,
                                                                    pattern='castillalamancha_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CASTILLAYLEON: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_castillayleon_increment,
                                                                    pattern='castillayleon_increment'),
                                               CallbackQueryHandler(show_castillayleon_cumulative,
                                                                    pattern='castillayleon_cumulative'),
                                               CallbackQueryHandler(show_castillayleon_death,
                                                                    pattern='castillayleon_death'),
                                               CallbackQueryHandler(show_castillayleon_hospital,
                                                                    pattern='castillayleon_hospital'),
                                               CallbackQueryHandler(show_castillayleon_all,
                                                                    pattern='castillayleon_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CASTILLAYLEON_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_castillayleon_cumulative,
                                                                    pattern='castillayleon_cumulative'),
                                               CallbackQueryHandler(show_castillayleon_death,
                                                                    pattern='castillayleon_death'),
                                               CallbackQueryHandler(show_castillayleon_hospital,
                                                                    pattern='castillayleon_hospital'),
                                               CallbackQueryHandler(show_castillayleon_all,
                                                                    pattern='castillayleon_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CASTILLAYLEON_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_castillayleon_increment,
                                                                    pattern='castillayleon_increment'),
                                               CallbackQueryHandler(show_castillayleon_death,
                                                                    pattern='castillayleon_death'),
                                               CallbackQueryHandler(show_castillayleon_hospital,
                                                                    pattern='castillayleon_hospital'),
                                               CallbackQueryHandler(show_castillayleon_all,
                                                                    pattern='castillayleon_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CASTILLAYLEON_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_castillayleon_increment,
                                                                    pattern='castillayleon_increment'),
                                               CallbackQueryHandler(show_castillayleon_cumulative,
                                                                    pattern='castillayleon_cumulative'),
                                               CallbackQueryHandler(show_castillayleon_hospital,
                                                                    pattern='castillayleon_hospital'),
                                               CallbackQueryHandler(show_castillayleon_all,
                                                                    pattern='castillayleon_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CASTILLAYLEON_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_castillayleon_increment,
                                                                    pattern='castillayleon_increment'),
                                               CallbackQueryHandler(show_castillayleon_cumulative,
                                                                    pattern='castillayleon_cumulative'),
                                               CallbackQueryHandler(show_castillayleon_death,
                                                                    pattern='castillayleon_death'),
                                               CallbackQueryHandler(show_castillayleon_all,
                                                                    pattern='castillayleon_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CASTILLAYLEON_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_castillayleon_increment,
                                                                    pattern='castillayleon_increment'),
                                               CallbackQueryHandler(show_castillayleon_cumulative,
                                                                    pattern='castillayleon_cumulative'),
                                               CallbackQueryHandler(show_castillayleon_death,
                                                                    pattern='castillayleon_death'),
                                               CallbackQueryHandler(show_castillayleon_hospital,
                                                                    pattern='castillayleon_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CATALUÑA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cataluña_increment,
                                                                    pattern='cataluña_increment'),
                                               CallbackQueryHandler(show_cataluña_cumulative,
                                                                    pattern='cataluña_cumulative'),
                                               CallbackQueryHandler(show_cataluña_death,
                                                                    pattern='cataluña_death'),
                                               CallbackQueryHandler(show_cataluña_hospital,
                                                                    pattern='cataluña_hospital'),
                                               CallbackQueryHandler(show_cataluña_all,
                                                                    pattern='cataluña_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CATALUÑA_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cataluña_cumulative,
                                                                    pattern='cataluña_cumulative'),
                                               CallbackQueryHandler(show_cataluña_death,
                                                                    pattern='cataluña_death'),
                                               CallbackQueryHandler(show_cataluña_hospital,
                                                                    pattern='cataluña_hospital'),
                                               CallbackQueryHandler(show_cataluña_all,
                                                                    pattern='cataluña_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CATALUÑA_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cataluña_increment,
                                                                    pattern='cataluña_increment'),
                                               CallbackQueryHandler(show_cataluña_death,
                                                                    pattern='cataluña_death'),
                                               CallbackQueryHandler(show_cataluña_hospital,
                                                                    pattern='cataluña_hospital'),
                                               CallbackQueryHandler(show_cataluña_all,
                                                                    pattern='cataluña_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CATALUÑA_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cataluña_increment,
                                                                    pattern='cataluña_increment'),
                                               CallbackQueryHandler(show_cataluña_cumulative,
                                                                    pattern='cataluña_cumulative'),
                                               CallbackQueryHandler(show_cataluña_hospital,
                                                                    pattern='cataluña_hospital'),
                                               CallbackQueryHandler(show_cataluña_all,
                                                                    pattern='cataluña_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CATALUÑA_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cataluña_increment,
                                                                    pattern='cataluña_increment'),
                                               CallbackQueryHandler(show_cataluña_cumulative,
                                                                    pattern='cataluña_cumulative'),
                                               CallbackQueryHandler(show_cataluña_death,
                                                                    pattern='cataluña_death'),
                                               CallbackQueryHandler(show_cataluña_all,
                                                                    pattern='cataluña_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CATALUÑA_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cataluña_increment,
                                                                    pattern='cataluña_increment'),
                                               CallbackQueryHandler(show_cataluña_cumulative,
                                                                    pattern='cataluña_cumulative'),
                                               CallbackQueryHandler(show_cataluña_death,
                                                                    pattern='cataluña_death'),
                                               CallbackQueryHandler(show_cataluña_hospital,
                                                                    pattern='cataluña_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CEUTA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_ceuta_increment,
                                                                    pattern='ceuta_increment'),
                                               CallbackQueryHandler(show_ceuta_cumulative,
                                                                    pattern='ceuta_cumulative'),
                                               CallbackQueryHandler(show_ceuta_death,
                                                                    pattern='ceuta_death'),
                                               CallbackQueryHandler(show_ceuta_hospital,
                                                                    pattern='ceuta_hospital'),
                                               CallbackQueryHandler(show_ceuta_all,
                                                                    pattern='ceuta_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CEUTA_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_ceuta_cumulative,
                                                                    pattern='ceuta_cumulative'),
                                               CallbackQueryHandler(show_ceuta_death,
                                                                    pattern='ceuta_death'),
                                               CallbackQueryHandler(show_ceuta_hospital,
                                                                    pattern='ceuta_hospital'),
                                               CallbackQueryHandler(show_ceuta_all,
                                                                    pattern='ceuta_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CEUTA_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_ceuta_increment,
                                                                    pattern='ceuta_increment'),
                                               CallbackQueryHandler(show_ceuta_death,
                                                                    pattern='ceuta_death'),
                                               CallbackQueryHandler(show_ceuta_hospital,
                                                                    pattern='ceuta_hospital'),
                                               CallbackQueryHandler(show_ceuta_all,
                                                                    pattern='ceuta_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CEUTA_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_ceuta_increment,
                                                                    pattern='ceuta_increment'),
                                               CallbackQueryHandler(show_ceuta_cumulative,
                                                                    pattern='ceuta_cumulative'),
                                               CallbackQueryHandler(show_ceuta_hospital,
                                                                    pattern='ceuta_hospital'),
                                               CallbackQueryHandler(show_ceuta_all,
                                                                    pattern='ceuta_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CEUTA_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_ceuta_increment,
                                                                    pattern='ceuta_increment'),
                                               CallbackQueryHandler(show_ceuta_cumulative,
                                                                    pattern='ceuta_cumulative'),
                                               CallbackQueryHandler(show_ceuta_death,
                                                                    pattern='ceuta_death'),
                                               CallbackQueryHandler(show_ceuta_all,
                                                                    pattern='ceuta_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_CEUTA_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_ceuta_increment,
                                                                    pattern='ceuta_increment'),
                                               CallbackQueryHandler(show_ceuta_cumulative,
                                                                    pattern='ceuta_cumulative'),
                                               CallbackQueryHandler(show_ceuta_death,
                                                                    pattern='ceuta_death'),
                                               CallbackQueryHandler(show_ceuta_hospital,
                                                                    pattern='ceuta_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_EXTREMADURA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_extremadura_increment,
                                                                    pattern='extremadura_increment'),
                                               CallbackQueryHandler(show_extremadura_cumulative,
                                                                    pattern='extremadura_cumulative'),
                                               CallbackQueryHandler(show_extremadura_death,
                                                                    pattern='extremadura_death'),
                                               CallbackQueryHandler(show_extremadura_hospital,
                                                                    pattern='extremadura_hospital'),
                                               CallbackQueryHandler(show_extremadura_all,
                                                                    pattern='extremadura_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_EXTREMADURA_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_extremadura_cumulative,
                                                                    pattern='extremadura_cumulative'),
                                               CallbackQueryHandler(show_extremadura_death,
                                                                    pattern='extremadura_death'),
                                               CallbackQueryHandler(show_extremadura_hospital,
                                                                    pattern='extremadura_hospital'),
                                               CallbackQueryHandler(show_extremadura_all,
                                                                    pattern='extremadura_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_EXTREMADURA_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_extremadura_increment,
                                                                    pattern='extremadura_increment'),
                                               CallbackQueryHandler(show_extremadura_death,
                                                                    pattern='extremadura_death'),
                                               CallbackQueryHandler(show_extremadura_hospital,
                                                                    pattern='extremadura_hospital'),
                                               CallbackQueryHandler(show_extremadura_all,
                                                                    pattern='extremadura_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_EXTREMADURA_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_extremadura_increment,
                                                                    pattern='extremadura_increment'),
                                               CallbackQueryHandler(show_extremadura_cumulative,
                                                                    pattern='extremadura_cumulative'),
                                               CallbackQueryHandler(show_extremadura_hospital,
                                                                    pattern='extremadura_hospital'),
                                               CallbackQueryHandler(show_extremadura_all,
                                                                    pattern='extremadura_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_EXTREMADURA_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_extremadura_increment,
                                                                    pattern='extremadura_increment'),
                                               CallbackQueryHandler(show_extremadura_cumulative,
                                                                    pattern='extremadura_cumulative'),
                                               CallbackQueryHandler(show_extremadura_death,
                                                                    pattern='extremadura_death'),
                                               CallbackQueryHandler(show_extremadura_all,
                                                                    pattern='extremadura_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_EXTREMADURA_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_extremadura_increment,
                                                                    pattern='extremadura_increment'),
                                               CallbackQueryHandler(show_extremadura_cumulative,
                                                                    pattern='extremadura_cumulative'),
                                               CallbackQueryHandler(show_extremadura_death,
                                                                    pattern='extremadura_death'),
                                               CallbackQueryHandler(show_extremadura_hospital,
                                                                    pattern='extremadura_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_GALICIA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_galicia_increment,
                                                                    pattern='galicia_increment'),
                                               CallbackQueryHandler(show_galicia_cumulative,
                                                                    pattern='galicia_cumulative'),
                                               CallbackQueryHandler(show_galicia_death,
                                                                    pattern='galicia_death'),
                                               CallbackQueryHandler(show_galicia_hospital,
                                                                    pattern='galicia_hospital'),
                                               CallbackQueryHandler(show_galicia_all,
                                                                    pattern='galicia_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_GALICIA_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_galicia_cumulative,
                                                                    pattern='galicia_cumulative'),
                                               CallbackQueryHandler(show_galicia_death,
                                                                    pattern='galicia_death'),
                                               CallbackQueryHandler(show_galicia_hospital,
                                                                    pattern='galicia_hospital'),
                                               CallbackQueryHandler(show_galicia_all,
                                                                    pattern='galicia_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_GALICIA_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_galicia_increment,
                                                                    pattern='galicia_increment'),
                                               CallbackQueryHandler(show_galicia_death,
                                                                    pattern='galicia_death'),
                                               CallbackQueryHandler(show_galicia_hospital,
                                                                    pattern='galicia_hospital'),
                                               CallbackQueryHandler(show_galicia_all,
                                                                    pattern='galicia_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_GALICIA_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_galicia_increment,
                                                                    pattern='galicia_increment'),
                                               CallbackQueryHandler(show_galicia_cumulative,
                                                                    pattern='galicia_cumulative'),
                                               CallbackQueryHandler(show_galicia_hospital,
                                                                    pattern='galicia_hospital'),
                                               CallbackQueryHandler(show_galicia_all,
                                                                    pattern='galicia_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_GALICIA_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_galicia_increment,
                                                                    pattern='galicia_increment'),
                                               CallbackQueryHandler(show_galicia_cumulative,
                                                                    pattern='galicia_cumulative'),
                                               CallbackQueryHandler(show_galicia_death,
                                                                    pattern='galicia_death'),
                                               CallbackQueryHandler(show_galicia_all,
                                                                    pattern='galicia_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_GALICIA_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_galicia_increment,
                                                                    pattern='galicia_increment'),
                                               CallbackQueryHandler(show_galicia_cumulative,
                                                                    pattern='galicia_cumulative'),
                                               CallbackQueryHandler(show_galicia_death,
                                                                    pattern='galicia_death'),
                                               CallbackQueryHandler(show_galicia_hospital,
                                                                    pattern='galicia_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_BALEARES: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_baleares_increment,
                                                                    pattern='baleares_increment'),
                                               CallbackQueryHandler(show_baleares_cumulative,
                                                                    pattern='baleares_cumulative'),
                                               CallbackQueryHandler(show_baleares_death,
                                                                    pattern='baleares_death'),
                                               CallbackQueryHandler(show_baleares_hospital,
                                                                    pattern='baleares_hospital'),
                                               CallbackQueryHandler(show_baleares_all,
                                                                    pattern='baleares_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_BALEARES_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_baleares_cumulative,
                                                                    pattern='baleares_cumulative'),
                                               CallbackQueryHandler(show_baleares_death,
                                                                    pattern='baleares_death'),
                                               CallbackQueryHandler(show_baleares_hospital,
                                                                    pattern='baleares_hospital'),
                                               CallbackQueryHandler(show_baleares_all,
                                                                    pattern='baleares_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_BALEARES_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_baleares_increment,
                                                                    pattern='baleares_increment'),
                                               CallbackQueryHandler(show_baleares_death,
                                                                    pattern='baleares_death'),
                                               CallbackQueryHandler(show_baleares_hospital,
                                                                    pattern='baleares_hospital'),
                                               CallbackQueryHandler(show_baleares_all,
                                                                    pattern='baleares_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_BALEARES_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_baleares_increment,
                                                                    pattern='baleares_increment'),
                                               CallbackQueryHandler(show_baleares_cumulative,
                                                                    pattern='baleares_cumulative'),
                                               CallbackQueryHandler(show_baleares_hospital,
                                                                    pattern='baleares_hospital'),
                                               CallbackQueryHandler(show_baleares_all,
                                                                    pattern='baleares_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_BALEARES_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_baleares_increment,
                                                                    pattern='baleares_increment'),
                                               CallbackQueryHandler(show_baleares_cumulative,
                                                                    pattern='baleares_cumulative'),
                                               CallbackQueryHandler(show_baleares_death,
                                                                    pattern='baleares_death'),
                                               CallbackQueryHandler(show_baleares_all,
                                                                    pattern='baleares_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_BALEARES_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_baleares_increment,
                                                                    pattern='baleares_increment'),
                                               CallbackQueryHandler(show_baleares_cumulative,
                                                                    pattern='baleares_cumulative'),
                                               CallbackQueryHandler(show_baleares_death,
                                                                    pattern='baleares_death'),
                                               CallbackQueryHandler(show_baleares_hospital,
                                                                    pattern='baleares_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_LARIOJA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_larioja_increment,
                                                                    pattern='larioja_increment'),
                                               CallbackQueryHandler(show_larioja_cumulative,
                                                                    pattern='larioja_cumulative'),
                                               CallbackQueryHandler(show_larioja_death,
                                                                    pattern='larioja_death'),
                                               CallbackQueryHandler(show_larioja_hospital,
                                                                    pattern='larioja_hospital'),
                                               CallbackQueryHandler(show_larioja_all,
                                                                    pattern='larioja_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_LARIOJA_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_larioja_cumulative,
                                                                    pattern='larioja_cumulative'),
                                               CallbackQueryHandler(show_larioja_death,
                                                                    pattern='larioja_death'),
                                               CallbackQueryHandler(show_larioja_hospital,
                                                                    pattern='larioja_hospital'),
                                               CallbackQueryHandler(show_larioja_all,
                                                                    pattern='larioja_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_LARIOJA_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_larioja_increment,
                                                                    pattern='larioja_increment'),
                                               CallbackQueryHandler(show_larioja_death,
                                                                    pattern='larioja_death'),
                                               CallbackQueryHandler(show_larioja_hospital,
                                                                    pattern='larioja_hospital'),
                                               CallbackQueryHandler(show_larioja_all,
                                                                    pattern='larioja_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_LARIOJA_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_larioja_increment,
                                                                    pattern='larioja_increment'),
                                               CallbackQueryHandler(show_larioja_cumulative,
                                                                    pattern='larioja_cumulative'),
                                               CallbackQueryHandler(show_larioja_hospital,
                                                                    pattern='larioja_hospital'),
                                               CallbackQueryHandler(show_larioja_all,
                                                                    pattern='larioja_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_LARIOJA_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_larioja_increment,
                                                                    pattern='larioja_increment'),
                                               CallbackQueryHandler(show_larioja_cumulative,
                                                                    pattern='larioja_cumulative'),
                                               CallbackQueryHandler(show_larioja_death,
                                                                    pattern='larioja_death'),
                                               CallbackQueryHandler(show_larioja_all,
                                                                    pattern='larioja_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_LARIOJA_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_larioja_increment,
                                                                    pattern='larioja_increment'),
                                               CallbackQueryHandler(show_larioja_cumulative,
                                                                    pattern='larioja_cumulative'),
                                               CallbackQueryHandler(show_larioja_death,
                                                                    pattern='larioja_death'),
                                               CallbackQueryHandler(show_larioja_hospital,
                                                                    pattern='larioja_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MADRID: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_madrid_increment,
                                                                    pattern='madrid_increment'),
                                               CallbackQueryHandler(show_madrid_cumulative,
                                                                    pattern='madrid_cumulative'),
                                               CallbackQueryHandler(show_madrid_death,
                                                                    pattern='madrid_death'),
                                               CallbackQueryHandler(show_madrid_hospital,
                                                                    pattern='madrid_hospital'),
                                               CallbackQueryHandler(show_madrid_all,
                                                                    pattern='madrid_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MADRID_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_madrid_cumulative,
                                                                    pattern='madrid_cumulative'),
                                               CallbackQueryHandler(show_madrid_death,
                                                                    pattern='madrid_death'),
                                               CallbackQueryHandler(show_madrid_hospital,
                                                                    pattern='madrid_hospital'),
                                               CallbackQueryHandler(show_madrid_all,
                                                                    pattern='madrid_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MADRID_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_madrid_increment,
                                                                    pattern='madrid_increment'),
                                               CallbackQueryHandler(show_madrid_death,
                                                                    pattern='madrid_death'),
                                               CallbackQueryHandler(show_madrid_hospital,
                                                                    pattern='madrid_hospital'),
                                               CallbackQueryHandler(show_madrid_all,
                                                                    pattern='madrid_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MADRID_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_madrid_increment,
                                                                    pattern='madrid_increment'),
                                               CallbackQueryHandler(show_madrid_cumulative,
                                                                    pattern='madrid_cumulative'),
                                               CallbackQueryHandler(show_madrid_hospital,
                                                                    pattern='madrid_hospital'),
                                               CallbackQueryHandler(show_madrid_all,
                                                                    pattern='madrid_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MADRID_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_madrid_increment,
                                                                    pattern='madrid_increment'),
                                               CallbackQueryHandler(show_madrid_cumulative,
                                                                    pattern='madrid_cumulative'),
                                               CallbackQueryHandler(show_madrid_death,
                                                                    pattern='madrid_death'),
                                               CallbackQueryHandler(show_madrid_all,
                                                                    pattern='madrid_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MADRID_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_madrid_increment,
                                                                    pattern='madrid_increment'),
                                               CallbackQueryHandler(show_madrid_cumulative,
                                                                    pattern='madrid_cumulative'),
                                               CallbackQueryHandler(show_madrid_death,
                                                                    pattern='madrid_death'),
                                               CallbackQueryHandler(show_madrid_hospital,
                                                                    pattern='madrid_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MELILLA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_melilla_increment,
                                                                    pattern='melilla_increment'),
                                               CallbackQueryHandler(show_melilla_cumulative,
                                                                    pattern='melilla_cumulative'),
                                               CallbackQueryHandler(show_melilla_death,
                                                                    pattern='melilla_death'),
                                               CallbackQueryHandler(show_melilla_hospital,
                                                                    pattern='melilla_hospital'),
                                               CallbackQueryHandler(show_melilla_all,
                                                                    pattern='melilla_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MELILLA_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_melilla_cumulative,
                                                                    pattern='melilla_cumulative'),
                                               CallbackQueryHandler(show_melilla_death,
                                                                    pattern='melilla_death'),
                                               CallbackQueryHandler(show_melilla_hospital,
                                                                    pattern='melilla_hospital'),
                                               CallbackQueryHandler(show_melilla_all,
                                                                    pattern='melilla_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MELILLA_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_melilla_increment,
                                                                    pattern='melilla_increment'),
                                               CallbackQueryHandler(show_melilla_death,
                                                                    pattern='melilla_death'),
                                               CallbackQueryHandler(show_melilla_hospital,
                                                                    pattern='melilla_hospital'),
                                               CallbackQueryHandler(show_melilla_all,
                                                                    pattern='melilla_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MELILLA_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_melilla_increment,
                                                                    pattern='melilla_increment'),
                                               CallbackQueryHandler(show_melilla_cumulative,
                                                                    pattern='melilla_cumulative'),
                                               CallbackQueryHandler(show_melilla_hospital,
                                                                    pattern='melilla_hospital'),
                                               CallbackQueryHandler(show_melilla_all,
                                                                    pattern='melilla_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MELILLA_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_melilla_increment,
                                                                    pattern='melilla_increment'),
                                               CallbackQueryHandler(show_melilla_cumulative,
                                                                    pattern='melilla_cumulative'),
                                               CallbackQueryHandler(show_melilla_death,
                                                                    pattern='melilla_death'),
                                               CallbackQueryHandler(show_melilla_all,
                                                                    pattern='melilla_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MELILLA_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_melilla_increment,
                                                                    pattern='melilla_increment'),
                                               CallbackQueryHandler(show_melilla_cumulative,
                                                                    pattern='melilla_cumulative'),
                                               CallbackQueryHandler(show_melilla_death,
                                                                    pattern='melilla_death'),
                                               CallbackQueryHandler(show_melilla_hospital,
                                                                    pattern='melilla_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MURCIA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_murcia_increment,
                                                                    pattern='murcia_increment'),
                                               CallbackQueryHandler(show_murcia_cumulative,
                                                                    pattern='murcia_cumulative'),
                                               CallbackQueryHandler(show_murcia_death,
                                                                    pattern='murcia_death'),
                                               CallbackQueryHandler(show_murcia_hospital,
                                                                    pattern='murcia_hospital'),
                                               CallbackQueryHandler(show_murcia_all,
                                                                    pattern='murcia_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MURCIA_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_murcia_cumulative,
                                                                    pattern='murcia_cumulative'),
                                               CallbackQueryHandler(show_murcia_death,
                                                                    pattern='murcia_death'),
                                               CallbackQueryHandler(show_murcia_hospital,
                                                                    pattern='murcia_hospital'),
                                               CallbackQueryHandler(show_murcia_all,
                                                                    pattern='murcia_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MURCIA_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_murcia_increment,
                                                                    pattern='murcia_increment'),
                                               CallbackQueryHandler(show_murcia_death,
                                                                    pattern='murcia_death'),
                                               CallbackQueryHandler(show_murcia_hospital,
                                                                    pattern='murcia_hospital'),
                                               CallbackQueryHandler(show_murcia_all,
                                                                    pattern='murcia_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MURCIA_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_murcia_increment,
                                                                    pattern='murcia_increment'),
                                               CallbackQueryHandler(show_murcia_cumulative,
                                                                    pattern='murcia_cumulative'),
                                               CallbackQueryHandler(show_murcia_hospital,
                                                                    pattern='murcia_hospital'),
                                               CallbackQueryHandler(show_murcia_all,
                                                                    pattern='murcia_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MURCIA_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_murcia_increment,
                                                                    pattern='murcia_increment'),
                                               CallbackQueryHandler(show_murcia_cumulative,
                                                                    pattern='murcia_cumulative'),
                                               CallbackQueryHandler(show_murcia_death,
                                                                    pattern='murcia_death'),
                                               CallbackQueryHandler(show_murcia_all,
                                                                    pattern='murcia_all'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           INFO_MURCIA_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_murcia_increment,
                                                                    pattern='murcia_increment'),
                                               CallbackQueryHandler(show_murcia_cumulative,
                                                                    pattern='murcia_cumulative'),
                                               CallbackQueryHandler(show_murcia_death,
                                                                    pattern='murcia_death'),
                                               CallbackQueryHandler(show_murcia_hospital,
                                                                    pattern='murcia_hospital'),
                                               CallbackQueryHandler(show_not_implemented,
                                                                    pattern='show_not_implemented')
                                           ],
                                           NOT_IMPLEMENTED: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_inicio,
                                                                    pattern='start_menu')
                                           ]
                                       },
                                       fallbacks=[
                                           CommandHandler('start', start_handler),
                                           CommandHandler('help', help_handler),
                                           CommandHandler('info', show_info),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='start_menu'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='andalucia_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='andalucia_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='andalucia_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='andalucia_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='andalucia_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='andalucia_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='aragon_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='aragon_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='aragon_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='aragon_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='aragon_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='aragon_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='asturias_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='asturias_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='asturias_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='asturias_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='asturias_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='asturias_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cvalenciana_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cvalenciana_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cvalenciana_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cvalenciana_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cvalenciana_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cvalenciana_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='canarias_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='canarias_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='canarias_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='canarias_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='canarias_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='canarias_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cantabria_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cantabria_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cantabria_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cantabria_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cantabria_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cantabria_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='castillalamancha_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='castillalamancha_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='castillalamancha_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='castillalamancha_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='castillalamancha_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='castillalamancha_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='castillayleon_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='castillayleon_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='castillayleon_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='castillayleon_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='castillayleon_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='castillayleon_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cataluña_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cataluña_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cataluña_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cataluña_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cataluña_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cataluña_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='ceuta_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='ceuta_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='ceuta_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='ceuta_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='ceuta_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='ceuta_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='extremadura_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='extremadura_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='extremadura_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='extremadura_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='extremadura_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='extremadura_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='galicia_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='galicia_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='galicia_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='galicia_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='galicia_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='galicia_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='baleares_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='baleares_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='baleares_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='baleares_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='baleares_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='baleares_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='larioja_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='larioja_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='larioja_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='larioja_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='larioja_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='larioja_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='madrid_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='madrid_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='madrid_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='madrid_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='madrid_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='madrid_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='melilla_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='melilla_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='melilla_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='melilla_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='melilla_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='melilla_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='murcia_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='murcia_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='murcia_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='murcia_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='murcia_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='murcia_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='show_not_implemented'),
                                       ])

    updater.dispatcher.add_handler(conv_handler)

    run(updater)


########################  FUNCIONALIDAD BBDD  ########################
def format_date(fecha):
    return datetime.strptime(fecha, "%Y-%m-%d").strftime("%d-%m-%Y")


def casos_acumulados(provincia):
    return str(df_ccaa_casos.groupby(['ccaa'])['num_casos'].sum()[provincia])


def incremento_ultimo_dia(provincia):
    df_loc = df_ccaa_casos.loc[(df_ccaa_casos['fecha'] == fecha_actualizacion(provincia)) &
                               (df_ccaa_casos['ccaa'] == provincia)]
    return str(df_loc['num_casos'].values[0])


def media_casos_semana(provincia):
    ultima_fecha = fecha_actualizacion(provincia)
    fecha = datetime.strptime(ultima_fecha, "%Y-%m-%d")

    total = 0
    for i in range(7):
        fecha2 = fecha - timedelta(days=i)
        fecha_semana_antes = fecha2.strftime("%Y-%m-%d")

        df_loc = df_ccaa_casos.loc[(df_ccaa_casos['fecha'] == fecha_semana_antes) &
                                   (df_ccaa_casos['ccaa'] == provincia)]
        total += int(df_loc['num_casos'].values[0])

    return str(round(total/7, 1))


def fecha_actualizacion(provincia):
    actual_day = date.today()
    dias_antes = 0
    day_before = timedelta(days=dias_antes)

    # La primera fecha de la que se tiene datos
    while df_ccaa_casos.loc[df_ccaa_casos['fecha'] == str(actual_day-day_before)].empty:
        dias_antes += 1
        day_before = timedelta(days=dias_antes)

    # Los ultimos datos de la provincia
    df_loc = df_ccaa_casos.loc[(df_ccaa_casos['fecha'] == str(actual_day-day_before)) &
                               (df_ccaa_casos['ccaa'] == provincia)]

    while df_loc['num_casos'].values[0] == 0:
        dias_antes += 1
        day_before = timedelta(days=dias_antes)
        df_loc = df_ccaa_casos.loc[(df_ccaa_casos['fecha'] == str(actual_day-day_before)) &
                                   (df_ccaa_casos['ccaa'] == provincia)]

    return str(actual_day-day_before)


def muertes_totales(provincia):
    return str(df_ccaa_muertes.groupby(['CCAA'])['Fallecidos'].sum()[provincia])


def muertes_ultimo_dia(provincia):
    df_loc = df_ccaa_muertes.loc[(df_ccaa_muertes['Fecha'] == fecha_actualizacion_muertes()) &
                                 (df_ccaa_muertes['CCAA'] == provincia)]
    return str(df_loc['Fallecidos'].values[0])


def media_muertes_semana(provincia):
    ultima_fecha = fecha_actualizacion_muertes()
    fecha = datetime.strptime(ultima_fecha, "%Y-%m-%d")

    total = 0
    for i in range(7):
        fecha2 = fecha - timedelta(days=i)
        fecha_semana_antes = fecha2.strftime("%Y-%m-%d")

        df_loc = df_ccaa_muertes.loc[(df_ccaa_muertes['Fecha'] == fecha_semana_antes) &
                                     (df_ccaa_muertes['CCAA'] == provincia)]
        total += int(df_loc['Fallecidos'].values[0])

    return str(round(total/7, 1))


def tasa_letalidad(provincia):
    return str(round(int(muertes_totales(provincia))*100/int(casos_acumulados(provincia)), 2))


def fecha_actualizacion_muertes():
    actual_day = date.today()
    dias_antes = 0
    day_before = timedelta(days=dias_antes)

    # La primera fecha de la que se tiene datos
    while df_ccaa_muertes.loc[df_ccaa_muertes['Fecha'] == str(actual_day - day_before)].empty:
        dias_antes += 1
        day_before = timedelta(days=dias_antes)

    return str(actual_day-day_before)


def pacientes_ingresados(provincia):
    df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == fecha_actualizacion_hospital(provincia)) &
                                  (df_ccaa_hospital['CCAA'] == provincia)]
    return str(int(df_loc['Total Pacientes COVID ingresados']))


def porcentaje_camas_ocupadas(provincia):
    df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == fecha_actualizacion_hospital(provincia)) &
                                  (df_ccaa_hospital['CCAA'] == provincia)]
    return str(df_loc['% Camas Ocupadas COVID'].values[0])


def pacientes_ingresados_uci(provincia):
    df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == fecha_actualizacion_hospital(provincia)) &
                                  (df_ccaa_hospital['CCAA'] == provincia)]
    return str(int(df_loc['Total pacientes COVID en UCI']))


def porcentaje_camas_uci_ocupadas(provincia):
    df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == fecha_actualizacion_hospital(provincia)) &
                                  (df_ccaa_hospital['CCAA'] == provincia)]
    return str(df_loc['% Camas Ocupadas UCI COVID'].values[0])


def ingresados_ultimo_dia(provincia):
    df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == fecha_actualizacion_hospital(provincia)) &
                                  (df_ccaa_hospital['CCAA'] == provincia)]
    return str(int(df_loc['Ingresos COVID últimas 24 h']))


def altas_ultimo_dia(provincia):
    df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == fecha_actualizacion_hospital(provincia)) &
                                  (df_ccaa_hospital['CCAA'] == provincia)]
    return str(int(df_loc['Altas COVID últimas 24 h']))


def fecha_actualizacion_hospital(provincia):
    actual_day = date.today()
    dias_antes = 0
    day_before = timedelta(days=dias_antes)

    # La primera fecha de la que se tiene datos
    while df_ccaa_hospital.loc[df_ccaa_hospital['Fecha'] == str(actual_day-day_before)].empty:
        dias_antes += 1
        day_before = timedelta(days=dias_antes)

    # Los ultimos datos de la provincia
    df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == str(actual_day-day_before)) &
                                  (df_ccaa_hospital['CCAA'] == provincia)]

    while df_loc['Total Pacientes COVID ingresados'].values[0] == 0:
        dias_antes += 1
        day_before = timedelta(days=dias_antes)
        df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == str(actual_day-day_before)) &
                                      (df_ccaa_hospital['CCAA'] == provincia)]

    return str(actual_day-day_before)


if __name__ == '__main__':
    main()