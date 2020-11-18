import logging
import os
import sys
from graphics import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler

# Enabling logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# POSSIBLE STATES
WELCOME, INICIO, HELP, STATUS_INFO, WELCOME_BAD, \
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
INFO_CASTILLAYLEON_ALL, INFO_CATALUNA, INFO_CATALUNA_INCREMENT, INFO_CATALUNA_CUMULATIVE, INFO_CATALUNA_DEATH, \
INFO_CATALUNA_HOSPITAL, INFO_CATALUNA_ALL, INFO_CEUTA, INFO_CEUTA_INCREMENT, INFO_CEUTA_CUMULATIVE, INFO_CEUTA_DEATH, \
INFO_CEUTA_HOSPITAL, INFO_CEUTA_ALL, INFO_EXTREMADURA, INFO_EXTREMADURA_INCREMENT, INFO_EXTREMADURA_CUMULATIVE, \
INFO_EXTREMADURA_DEATH, INFO_EXTREMADURA_HOSPITAL, INFO_EXTREMADURA_ALL, INFO_GALICIA, INFO_GALICIA_INCREMENT, \
INFO_GALICIA_CUMULATIVE, INFO_GALICIA_DEATH, INFO_GALICIA_HOSPITAL, INFO_GALICIA_ALL, INFO_BALEARES, \
INFO_BALEARES_INCREMENT, INFO_BALEARES_CUMULATIVE, INFO_BALEARES_DEATH, INFO_BALEARES_HOSPITAL, INFO_BALEARES_ALL,  \
INFO_LARIOJA, INFO_LARIOJA_INCREMENT, INFO_LARIOJA_CUMULATIVE, INFO_LARIOJA_DEATH, INFO_LARIOJA_HOSPITAL, \
INFO_LARIOJA_ALL, INFO_MADRID, INFO_MADRID_INCREMENT, INFO_MADRID_CUMULATIVE, INFO_MADRID_DEATH, INFO_MADRID_HOSPITAL, \
INFO_MADRID_ALL, INFO_MELILLA, INFO_MELILLA_INCREMENT, INFO_MELILLA_CUMULATIVE, INFO_MELILLA_DEATH, \
INFO_MELILLA_HOSPITAL, INFO_MELILLA_ALL, INFO_MURCIA, INFO_MURCIA_INCREMENT, INFO_MURCIA_CUMULATIVE, INFO_MURCIA_DEATH, \
INFO_MURCIA_HOSPITAL, INFO_MURCIA_ALL, INFO_NAVARRA, INFO_NAVARRA_INCREMENT, INFO_NAVARRA_CUMULATIVE, \
INFO_NAVARRA_DEATH, INFO_NAVARRA_HOSPITAL, INFO_NAVARRA_ALL, INFO_PAISVASCO, INFO_PAISVASCO_INCREMENT, \
INFO_PAISVASCO_CUMULATIVE, INFO_PAISVASCO_DEATH, INFO_PAISVASCO_HOSPITAL, INFO_PAISVASCO_ALL, INFO_ESPANA, \
INFO_ESPANA_INCREMENT, INFO_ESPANA_AGE, INFO_ESPANA_CUMULATIVE, INFO_ESPANA_DEATH, INFO_ESPANA_REGION, \
INFO_ESPANA_100_CUMULATIVE, INFO_ESPANA_100_CUMULATIVE_MEDIA, INFO_ESPANA_100_DEATH, \
INFO_ESPANA_100_DEATH_MEDIA, INFO_ESPANA_ALL = range(130)


# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")

global current_state

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

        main_menu_keyboard = [[KeyboardButton("📖 Menú"),
                               KeyboardButton("🆘 Ayuda"),
                               KeyboardButton("ℹ Información")]]

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

    update.message.reply_text(
        text="<b>Botones generales:</b>\n\n"
             "\t <b>📈 Incremento</b> - Incremento de los casos\n"
             "\t <b>➕ Casos acumulados</b> - Total de casos acumulados\n"
             "\t <b>☠ Fallecimientos</b> - Datos fallecidos\n"
             "\t <b>🏥 Hospitalizaciones</b> - Datos hospitalizaciones\n"
             "\t <b>⬇ Ver todo</b> - Ver toda la información disponible\n\n"
             "<b>Botones España:</b>\n\n"
             "\t <b>📈 Incremento</b> - Incremento de los casos\n"
             "\t <b>🧔👩 Casos por edad</b> - Casos/muertes por sexo y edad\n"
             "\t <b>➕ Casos acumulados</b> - Total de casos acumulados\n"
             "\t <b>☠ Fallecimientos</b> - Datos fallecidos\n"
             "\t <b>🗺 Casos por Región</b> - Datos casos por comunidad\n"
             "\t <b>📈💯 Casos 100mil</b> - Casos por cada 100mil habitantes por comunidad\n"
             "\t <b>📈🆕 Casos 100mil semana</b> - Media semanal casos por cada 100mil habitantes por comunidad\n"
             "\t <b>☠💯 Fallecimientos 100mil</b> - Fallecimientos por cada 100mil habitantes por comunidad\n"
             "\t <b>☠🆕 Fallecimientos 100mil</b> semana - Media semanal fallecimientos por cada 100mil habitantes por comunidad\n"
             "\t <b>⬇ Ver todo</b> - Ver toda la información disponible\n",
        parse_mode='HTML',
        disable_web_page_preview=True
    )

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
        update.message.reply_text(text="No te he entendido. El comando <b>{}</b> no está en mi registro."
                                  " Si es necesario, puedes reiniciarme usando /start".format(update.message.text),
                                  parse_mode='HTML')


def show_inicio(update, context):
    global current_state

    if current_state == "WELCOME_BAD":
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
         InlineKeyboardButton("Cataluña", callback_data='cataluna_info')],

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
         InlineKeyboardButton("Toda España 🇪🇸", callback_data='espana_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_espana.png', 'rb')
    )

    message.reply_text(
        text="{} elige la comunidad de la que quieres consultar datos.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INICIO"
    return INICIO


def show_main_info(update, context, current_autonomy):
    global current_state

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    autonomy_lower = normalize(current_autonomy).lower()
    autonomy_upper = normalize(current_autonomy).upper()

    keyboard = [
        [InlineKeyboardButton("📈 Incremento", callback_data='{}_increment'.format(autonomy_lower)),
         InlineKeyboardButton("➕ Casos acumulados", callback_data='{}_cumulative'.format(autonomy_lower)),
         InlineKeyboardButton("☠ Fallecimientos", callback_data='{}_death'.format(autonomy_lower))],

        [InlineKeyboardButton("🏥 Hospitalizaciones", callback_data='{}_hospital'.format(autonomy_lower)),
         InlineKeyboardButton("⬇ Ver todo", callback_data='{}_all'.format(autonomy_lower))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_{}.png'.format(autonomy_lower), 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_{}".format(autonomy_upper)


def show_andalucia_info(update, context):
    global current_state

    show_main_info(update, context, "Andalucía")

    return INFO_ANDALUCIA


def show_aragon_info(update, context):
    global current_state

    show_main_info(update, context, "Aragón")

    return INFO_ARAGON


def show_asturias_info(update, context):
    global current_state

    show_main_info(update, context, "Asturias")

    return INFO_ASTURIAS


def show_cvalenciana_info(update, context):
    global current_state

    show_main_info(update, context, "C. Valenciana")

    return INFO_CVALENCIANA


def show_canarias_info(update, context):
    global current_state

    show_main_info(update, context, "Canarias")

    return INFO_CANARIAS


def show_cantabria_info(update, context):
    global current_state

    show_main_info(update, context, "Cantabria")

    return INFO_CANTABRIA


def show_castillalamancha_info(update, context):
    global current_state

    show_main_info(update, context, "Castilla La Mancha")

    return INFO_CASTILLALAMANCHA


def show_castillayleon_info(update, context):
    global current_state

    show_main_info(update, context, "Castilla y León")

    return INFO_CASTILLAYLEON


def show_cataluna_info(update, context):
    global current_state

    show_main_info(update, context, "Cataluña")

    return INFO_CATALUNA


def show_ceuta_info(update, context):
    global current_state

    show_main_info(update, context, "Ceuta")

    return INFO_CEUTA


def show_extremadura_info(update, context):
    global current_state

    show_main_info(update, context, "Extremadura")

    return INFO_EXTREMADURA


def show_galicia_info(update, context):
    global current_state

    show_main_info(update, context, "Galicia")

    return INFO_GALICIA


def show_baleares_info(update, context):
    global current_state

    show_main_info(update, context, "Baleares")

    return INFO_BALEARES


def show_larioja_info(update, context):
    global current_state

    show_main_info(update, context, "La Rioja")

    return INFO_LARIOJA


def show_madrid_info(update, context):
    global current_state

    show_main_info(update, context, "Madrid")

    return INFO_MADRID


def show_melilla_info(update, context):
    global current_state

    show_main_info(update, context, "Melilla")

    return INFO_MELILLA


def show_murcia_info(update, context):
    global current_state

    show_main_info(update, context, "Murcia")

    return INFO_MURCIA


def show_navarra_info(update, context):
    global current_state

    show_main_info(update, context, "Navarra")

    return INFO_NAVARRA


def show_paisvasco_info(update, context):
    global current_state

    show_main_info(update, context, "País Vasco")

    return INFO_PAISVASCO


def show_espana_info(update, context):
    global current_state

    username = update.callback_query.message.chat.username
    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("📈 Incremento", callback_data='espana_increment'),
         InlineKeyboardButton("🧔👩 Casos por edad", callback_data='espana_age'),
         InlineKeyboardButton("➕ Casos acumulados", callback_data='espana_cumulative')],

        [InlineKeyboardButton("☠ Fallecimientos", callback_data='espana_death'),
         InlineKeyboardButton("🗺 Casos por Región", callback_data='espana_region')],

        [InlineKeyboardButton("📈💯 Casos 100mil", callback_data='espana_100_cumulative'),
         InlineKeyboardButton("📈🆕 Casos 100mil semana", callback_data='espana_100_cumulative_media')],

         [InlineKeyboardButton("☠💯 Fallecimientos 100mil", callback_data='espana_100_death'),
          InlineKeyboardButton("☠🆕 Fallecimientos 100mil semana", callback_data='espana_100_death_media')],

        [InlineKeyboardButton("⬇ Ver todo", callback_data='espana_all')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img/mapa_espana.png', 'rb')
    )

    message.reply_text(
        text="{} elige los datos que quieres consultar.".format(username),
        reply_markup=reply_markup
    )

    current_state = "INFO_ESPANA"
    return INFO_ESPANA


def show_increment(update, context, current_autonomy):
    global current_state

    message = update.callback_query.message

    autonomy_lower = normalize(current_autonomy).lower()
    autonomy_upper = normalize(current_autonomy).upper()

    keyboard = [
        [InlineKeyboardButton("➕ Casos acumulados", callback_data='{}_cumulative'.format(autonomy_lower)),
         InlineKeyboardButton("☠ Fallecimientos", callback_data='{}_death'.format(autonomy_lower))],

        [InlineKeyboardButton("🏥 Hospitalizaciones", callback_data='{}_hospital'.format(autonomy_lower)),
         InlineKeyboardButton("⬇ Ver todo", callback_data='{}_all'.format(autonomy_lower))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    grafica_incremento(current_autonomy)

    message.reply_photo(
        photo=open('./img_graficas/incremento_{}.png'.format(autonomy_lower), 'rb')
    )

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


def show_cumulative(update, context, current_autonomy):
    global current_state

    message = update.callback_query.message

    autonomy_lower = normalize(current_autonomy).lower()
    autonomy_upper = normalize(current_autonomy).upper()

    keyboard = [
        [InlineKeyboardButton("📈 Incremento", callback_data='{}_increment'.format(autonomy_lower)),
         InlineKeyboardButton("☠ Fallecimientos", callback_data='{}_death'.format(autonomy_lower))],

        [InlineKeyboardButton("🏥 Hospitalizaciones", callback_data='{}_hospital'.format(autonomy_lower)),
         InlineKeyboardButton("⬇ Ver todo", callback_data='{}_all'.format(autonomy_lower))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    grafica_acumulado(current_autonomy)

    message.reply_photo(
        photo=open('./img_graficas/acumulado_{}.png'.format(autonomy_lower), 'rb')
    )

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


def show_death(update, context, current_autonomy):
    global current_state

    message = update.callback_query.message

    autonomy_lower = normalize(current_autonomy).lower()
    autonomy_upper = normalize(current_autonomy).upper()

    keyboard = [
        [InlineKeyboardButton("📈 Incremento", callback_data='{}_increment'.format(autonomy_lower)),
         InlineKeyboardButton("➕ Casos acumulados", callback_data='{}_cumulative'.format(autonomy_lower))],

        [InlineKeyboardButton("🏥 Hospitalizaciones", callback_data='{}_hospital'.format(autonomy_lower)),
         InlineKeyboardButton("⬇ Ver todo", callback_data='{}_all'.format(autonomy_lower))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    grafica_muertes(current_autonomy)

    message.reply_photo(
        photo=open('./img_graficas/fallecidos_{}.png'.format(autonomy_lower), 'rb')
    )

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


def show_hospital(update, context, current_autonomy):
    global current_state

    message = update.callback_query.message

    autonomy_lower = normalize(current_autonomy).lower()
    autonomy_upper = normalize(current_autonomy).upper()

    keyboard = [
        [InlineKeyboardButton("📈 Incremento", callback_data='{}_increment'.format(autonomy_lower)),
         InlineKeyboardButton("➕ Casos acumulados", callback_data='{}_cumulative'.format(autonomy_lower))],

        [InlineKeyboardButton("☠ Fallecimientos", callback_data='{}_death'.format(autonomy_lower)),
         InlineKeyboardButton("⬇ Ver todo", callback_data='{}_all'.format(autonomy_lower))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    grafica_hospitales(current_autonomy)

    message.reply_photo(
        photo=open('./img_graficas/hospital_{}.png'.format(autonomy_lower), 'rb')
    )

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


def show_all_info(update, context, current_autonomy):
    global current_state

    message = update.callback_query.message

    autonomy_lower = normalize(current_autonomy).lower()
    autonomy_upper = normalize(current_autonomy).upper()

    keyboard = [
        [InlineKeyboardButton("📈 Incremento", callback_data='{}_increment'.format(autonomy_lower)),
         InlineKeyboardButton("➕ Casos acumulados", callback_data='{}_cumulative'.format(autonomy_lower))],

        [InlineKeyboardButton("☠ Fallecimientos", callback_data='{}_death'.format(autonomy_lower)),
         InlineKeyboardButton("🏥 Hospitalizaciones", callback_data='{}_hospital'.format(autonomy_lower))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message.reply_photo(
        photo=open('./img_graficas/incremento_{}.png'.format(autonomy_lower), 'rb')
    )

    grafica_incremento(current_autonomy)

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

    grafica_acumulado(current_autonomy)

    message.reply_photo(
        photo=open('./img_graficas/acumulado_{}.png'.format(autonomy_lower), 'rb')
    )

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

    grafica_muertes(current_autonomy)

    message.reply_photo(
        photo=open('./img_graficas/fallecidos_{}.png'.format(autonomy_lower), 'rb')
    )

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

    grafica_hospitales(current_autonomy)

    message.reply_photo(
        photo=open('./img_graficas/hospital_{}.png'.format(autonomy_lower), 'rb')
    )

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
    show_increment(update, context, "Andalucía")

    return INFO_ANDALUCIA_INCREMENT


def show_andalucia_cumulative(update, context):
    show_cumulative(update, context, "Andalucía")

    return INFO_ANDALUCIA_CUMULATIVE


def show_andalucia_death(update, context):
    show_death(update, context, "Andalucía")

    return INFO_ANDALUCIA_DEATH


def show_andalucia_hospital(update, context):
    show_hospital(update, context, "Andalucía")

    return INFO_ANDALUCIA_HOSPITAL


def show_andalucia_all(update, context):
    show_all_info(update, context, "Andalucía")

    return INFO_ANDALUCIA_ALL


# ARAGÓN
def show_aragon_increment(update, context):
    show_increment(update, context, "Aragón")

    return INFO_ARAGON_INCREMENT


def show_aragon_cumulative(update, context):
    show_cumulative(update, context, "Aragón")

    return INFO_ARAGON_CUMULATIVE


def show_aragon_death(update, context):
    show_death(update, context, "Aragón")

    return INFO_ARAGON_DEATH


def show_aragon_hospital(update, context):
    show_hospital(update, context, "Aragón")

    return INFO_ARAGON_HOSPITAL


def show_aragon_all(update, context):
    show_all_info(update, context, "Aragón")

    return INFO_ARAGON_ALL


# ASTURIAS
def show_asturias_increment(update, context):
    show_increment(update, context, "Asturias")

    return INFO_ASTURIAS_INCREMENT


def show_asturias_cumulative(update, context):
    show_cumulative(update, context, "Asturias")

    return INFO_ASTURIAS_CUMULATIVE


def show_asturias_death(update, context):
    show_death(update, context, "Asturias")

    return INFO_ASTURIAS_DEATH


def show_asturias_hospital(update, context):
    show_hospital(update, context, "Asturias")

    return INFO_ASTURIAS_HOSPITAL


def show_asturias_all(update, context):
    show_all_info(update, context, "Asturias")

    return INFO_ASTURIAS_ALL


# C. VALENCIANA
def show_cvalenciana_increment(update, context):
    show_increment(update, context, "C. Valenciana")

    return INFO_CVALENCIANA_INCREMENT


def show_cvalenciana_cumulative(update, context):
    show_cumulative(update, context, "C. Valenciana")

    return INFO_CVALENCIANA_CUMULATIVE


def show_cvalenciana_death(update, context):
    show_death(update, context, "C. Valenciana")

    return INFO_CVALENCIANA_DEATH


def show_cvalenciana_hospital(update, context):
    show_hospital(update, context, "C Valenciana")

    return INFO_CVALENCIANA_HOSPITAL


def show_cvalenciana_all(update, context):
    show_all_info(update, context, "C. Valenciana")

    return INFO_CVALENCIANA_ALL


# CANARIAS
def show_canarias_increment(update, context):
    show_increment(update, context, "Canarias")

    return INFO_CANARIAS_INCREMENT


def show_canarias_cumulative(update, context):
    show_cumulative(update, context, "Canarias")

    return INFO_CANARIAS_CUMULATIVE


def show_canarias_death(update, context):
    show_death(update, context, "Canarias")

    return INFO_CANARIAS_DEATH


def show_canarias_hospital(update, context):
    show_hospital(update, context, "Canarias")

    return INFO_CANARIAS_HOSPITAL


def show_canarias_all(update, context):
    show_all_info(update, context, "Canarias")

    return INFO_CANARIAS_ALL


# CANTABRIA
def show_cantabria_increment(update, context):
    show_increment(update, context, "Cantabria")

    return INFO_CANTABRIA_INCREMENT


def show_cantabria_cumulative(update, context):
    show_cumulative(update, context, "Cantabria")

    return INFO_CANTABRIA_CUMULATIVE


def show_cantabria_death(update, context):
    show_death(update, context, "Cantabria")

    return INFO_CANTABRIA_DEATH


def show_cantabria_hospital(update, context):
    show_hospital(update, context, "Cantabria")

    return INFO_CANTABRIA_HOSPITAL


def show_cantabria_all(update, context):
    show_all_info(update, context, "Cantabria")

    return INFO_CANTABRIA_ALL


# CASTILLA LA MANCHA
def show_castillalamancha_increment(update, context):
    show_increment(update, context, "Castilla La Mancha")

    return INFO_CASTILLALAMANCHA_INCREMENT


def show_castillalamancha_cumulative(update, context):
    show_cumulative(update, context, "Castilla La Mancha")

    return INFO_CASTILLALAMANCHA_CUMULATIVE


def show_castillalamancha_death(update, context):
    show_death(update, context, "Castilla La Mancha")

    return INFO_CASTILLALAMANCHA_DEATH


def show_castillalamancha_hospital(update, context):
    show_hospital(update, context, "Castilla La Mancha")

    return INFO_CASTILLALAMANCHA_HOSPITAL


def show_castillalamancha_all(update, context):
    show_all_info(update, context, "Castilla La Mancha")

    return INFO_CASTILLALAMANCHA_ALL


# CASTILLA Y LEON
def show_castillayleon_increment(update, context):
    show_increment(update, context, "Castilla y León")

    return INFO_CASTILLAYLEON_INCREMENT


def show_castillayleon_cumulative(update, context):
    show_cumulative(update, context, "Castilla y León")

    return INFO_CASTILLAYLEON_CUMULATIVE


def show_castillayleon_death(update, context):
    show_death(update, context, "Castilla y León")

    return INFO_CASTILLAYLEON_DEATH


def show_castillayleon_hospital(update, context):
    show_hospital(update, context, "Castilla y León")

    return INFO_CASTILLAYLEON_HOSPITAL


def show_castillayleon_all(update, context):
    show_all_info(update, context, "Castilla y León")

    return INFO_CASTILLAYLEON_ALL


# CATALUÑA
def show_cataluna_increment(update, context):
    show_increment(update, context, "Cataluña")

    return INFO_CATALUNA_INCREMENT


def show_cataluna_cumulative(update, context):
    show_cumulative(update, context, "Cataluña")

    return INFO_CATALUNA_CUMULATIVE


def show_cataluna_death(update, context):
    show_death(update, context, "Cataluña")

    return INFO_CATALUNA_DEATH


def show_cataluna_hospital(update, context):
    show_hospital(update, context, "Cataluña")

    return INFO_CATALUNA_HOSPITAL


def show_cataluna_all(update, context):
    show_all_info(update, context, "Cataluña")

    return INFO_CATALUNA_ALL


# CEUTA
def show_ceuta_increment(update, context):
    show_increment(update, context, "Ceuta")

    return INFO_CEUTA_INCREMENT


def show_ceuta_cumulative(update, context):
    show_cumulative(update, context, "Ceuta")

    return INFO_CEUTA_CUMULATIVE


def show_ceuta_death(update, context):
    show_death(update, context, "Ceuta")

    return INFO_CEUTA_DEATH


def show_ceuta_hospital(update, context):
    show_hospital(update, context, "Ceuta")

    return INFO_CEUTA_HOSPITAL


def show_ceuta_all(update, context):
    show_all_info(update, context, "Ceuta")

    return INFO_CEUTA_ALL


# EXTREMADURA
def show_extremadura_increment(update, context):
    show_increment(update, context, "Extremadura")

    return INFO_EXTREMADURA_INCREMENT


def show_extremadura_cumulative(update, context):
    show_cumulative(update, context, "Extremadura")

    return INFO_EXTREMADURA_CUMULATIVE


def show_extremadura_death(update, context):
    show_death(update, context, "Extremadura")

    return INFO_EXTREMADURA_DEATH


def show_extremadura_hospital(update, context):
    show_hospital(update, context, "Extremadura")

    return INFO_EXTREMADURA_HOSPITAL


def show_extremadura_all(update, context):
    show_all_info(update, context, "Extremadura")

    return INFO_EXTREMADURA_ALL


# GALICIA
def show_galicia_increment(update, context):
    show_increment(update, context, "Galicia")

    return INFO_GALICIA_INCREMENT


def show_galicia_cumulative(update, context):
    show_cumulative(update, context, "Galicia")

    return INFO_GALICIA_CUMULATIVE


def show_galicia_death(update, context):
    show_death(update, context, "Galicia")

    return INFO_GALICIA_DEATH


def show_galicia_hospital(update, context):
    show_hospital(update, context, "Galicia")

    return INFO_GALICIA_HOSPITAL


def show_galicia_all(update, context):
    show_all_info(update, context, "Galicia")

    return INFO_GALICIA_ALL


# BALEARES
def show_baleares_increment(update, context):
    show_increment(update, context, "Baleares")

    return INFO_BALEARES_INCREMENT


def show_baleares_cumulative(update, context):
    show_cumulative(update, context, "Baleares")

    return INFO_BALEARES_CUMULATIVE


def show_baleares_death(update, context):
    show_death(update, context, "Baleares")

    return INFO_BALEARES_DEATH


def show_baleares_hospital(update, context):
    show_hospital(update, context, "Baleares")

    return INFO_BALEARES_HOSPITAL


def show_baleares_all(update, context):
    show_all_info(update, context, "Baleares")

    return INFO_BALEARES_ALL


# LA RIOJA
def show_larioja_increment(update, context):
    show_increment(update, context, "La Rioja")

    return INFO_LARIOJA_INCREMENT


def show_larioja_cumulative(update, context):
    show_cumulative(update, context, "La Rioja")

    return INFO_LARIOJA_CUMULATIVE


def show_larioja_death(update, context):
    show_death(update, context, "La Rioja")

    return INFO_LARIOJA_DEATH


def show_larioja_hospital(update, context):
    show_hospital(update, context, "La Rioja")

    return INFO_LARIOJA_HOSPITAL


def show_larioja_all(update, context):
    show_all_info(update, context, "La Rioja")

    return INFO_LARIOJA_ALL


# MADRID
def show_madrid_increment(update, context):
    show_increment(update, context, "Madrid")

    return INFO_MADRID_INCREMENT


def show_madrid_cumulative(update, context):
    show_cumulative(update, context, "Madrid")

    return INFO_MADRID_CUMULATIVE


def show_madrid_death(update, context):
    show_death(update, context, "Madrid")

    return INFO_MADRID_DEATH


def show_madrid_hospital(update, context):
    show_hospital(update, context, "Madrid")

    return INFO_MADRID_HOSPITAL


def show_madrid_all(update, context):
    show_all_info(update, context, "Madrid")

    return INFO_MADRID_ALL


# MELILLA
def show_melilla_increment(update, context):
    show_increment(update, context, "Melilla")

    return INFO_MELILLA_INCREMENT


def show_melilla_cumulative(update, context):
    show_cumulative(update, context, "Melilla")

    return INFO_MELILLA_CUMULATIVE


def show_melilla_death(update, context):
    show_death(update, context, "Melilla")

    return INFO_MELILLA_DEATH


def show_melilla_hospital(update, context):
    show_hospital(update, context, "Melilla")

    return INFO_MELILLA_HOSPITAL


def show_melilla_all(update, context):
    show_all_info(update, context, "Melilla")

    return INFO_MELILLA_ALL


# MURCIA
def show_murcia_increment(update, context):
    show_increment(update, context, "Murcia")

    return INFO_MURCIA_INCREMENT


def show_murcia_cumulative(update, context):
    show_cumulative(update, context, "Murcia")

    return INFO_MURCIA_CUMULATIVE


def show_murcia_death(update, context):
    show_death(update, context, "Murcia")

    return INFO_MURCIA_DEATH


def show_murcia_hospital(update, context):
    show_hospital(update, context, "Murcia")

    return INFO_MURCIA_HOSPITAL


def show_murcia_all(update, context):
    show_all_info(update, context, "Murcia")

    return INFO_MURCIA_ALL


# NAVARRA
def show_navarra_increment(update, context):
    show_increment(update, context, "Navarra")

    return INFO_NAVARRA_INCREMENT


def show_navarra_cumulative(update, context):
    show_cumulative(update, context, "Navarra")

    return INFO_NAVARRA_CUMULATIVE


def show_navarra_death(update, context):
    show_death(update, context, "Navarra")

    return INFO_NAVARRA_DEATH


def show_navarra_hospital(update, context):
    show_hospital(update, context, "Navarra")

    return INFO_NAVARRA_HOSPITAL


def show_navarra_all(update, context):
    show_all_info(update, context, "Navarra")

    return INFO_NAVARRA_ALL


# PAÍS VASCO
def show_paisvasco_increment(update, context):
    show_increment(update, context, "País Vasco")

    return INFO_PAISVASCO_INCREMENT


def show_paisvasco_cumulative(update, context):
    show_cumulative(update, context, "País Vasco")

    return INFO_PAISVASCO_CUMULATIVE


def show_paisvasco_death(update, context):
    show_death(update, context, "País Vasco")

    return INFO_PAISVASCO_DEATH


def show_paisvasco_hospital(update, context):
    show_hospital(update, context, "País Vasco")

    return INFO_PAISVASCO_HOSPITAL


def show_paisvasco_all(update, context):
    show_all_info(update, context, "País Vasco")

    return INFO_PAISVASCO_ALL


# ESPAÑA
def show_espana_increment(update, context):
    global current_state

    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("🧔👩 Casos por edad", callback_data='espana_age'),
         InlineKeyboardButton("➕ Casos acumulados", callback_data='espana_cumulative')],

        [InlineKeyboardButton("☠ Fallecimientos", callback_data='espana_death'),
         InlineKeyboardButton("🗺 Casos por Región", callback_data='espana_region')],

        [InlineKeyboardButton("📈💯 Casos 100mil", callback_data='espana_100_cumulative'),
         InlineKeyboardButton("📈🆕 Casos 100mil semana ", callback_data='espana_100_cumulative_media')],

         [InlineKeyboardButton("☠💯 Fallecimientos 100mil", callback_data='espana_100_death'),
          InlineKeyboardButton("☠🆕 Fallecimientos 100mil semana", callback_data='espana_100_death_media')],

        [InlineKeyboardButton("⬇ Ver todo", callback_data='espana_all')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    grafica_incremento_espana()

    message.reply_photo(
        photo=open('./img_graficas/incremento_espana.png', 'rb')
    )

    message.reply_text(
        text="Incremento de casos en {}\n\n"
             "\t - Casos acumulados: <b>{}</b>.\n"
             "\t - Incremento de casos últimas 24h: <b>{}</b>.\n"
             "\t - Media del incremento de casos semanal: <b>{}</b>.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format('España',
                                                                         casos_acumulados_espana(),
                                                                         incremento_ultimo_dia_espana(),
                                                                         media_casos_semana_espana(),
                                                                         format_date(fecha_actualizacion_espana())),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    current_state = "INFO_ESPANA_INCREMENT"
    return INFO_ESPANA_INCREMENT


def show_espana_age(update, context):
    global current_state

    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("📈 Incremento", callback_data='espana_increment'),
         InlineKeyboardButton("➕ Casos acumulados", callback_data='espana_cumulative')],

        [InlineKeyboardButton("☠ Fallecimientos", callback_data='espana_death'),
         InlineKeyboardButton("🗺 Casos por Región", callback_data='espana_region')],

        [InlineKeyboardButton("📈💯 Casos 100mil", callback_data='espana_100_cumulative'),
         InlineKeyboardButton("📈🆕 Casos 100mil semana", callback_data='espana_100_cumulative_media')],

         [InlineKeyboardButton("☠💯 Fallecimientos 100mil", callback_data='espana_100_death'),
         InlineKeyboardButton("☠🆕 Fallecimientos 100mil semana", callback_data='espana_100_death_media')],

        [InlineKeyboardButton("⬇ Ver todo", callback_data='espana_all')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    grafica_edades()

    message.reply_photo(
        photo=open('./img_graficas/casos_edad_espana.png', 'rb')
    )

    message.reply_text(
        text="Casos (fallecidos) por edad: \n\n"
             "0-9: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "10-19: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "20-29: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "30-39: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "40-49: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "50-59: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "60-69: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "70-79: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "80-89: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "90 y +: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "Total: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n\n"
             "Datos obtenidos del análisis sobre los casos notificados con información disponible de edad y sexo.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(casos_edad('0-9'), muertos_edad('0-9'), tasa_edad('0-9'),
                                                                         casos_edad('10-19'), muertos_edad('10-19'), tasa_edad('10-19'),
                                                                         casos_edad('20-29'), muertos_edad('20-29'), tasa_edad('20-29'),
                                                                         casos_edad('30-39'), muertos_edad('30-39'), tasa_edad('30-39'),
                                                                         casos_edad('40-49'), muertos_edad('40-49'), tasa_edad('40-49'),
                                                                         casos_edad('50-59'), muertos_edad('50-59'), tasa_edad('50-59'),
                                                                         casos_edad('60-69'), muertos_edad('60-69'), tasa_edad('60-69'),
                                                                         casos_edad('70-79'), muertos_edad('70-79'), tasa_edad('70-79'),
                                                                         casos_edad('80-89'), muertos_edad('80-89'), tasa_edad('80-89'),
                                                                         casos_edad('90 y +'), muertos_edad('90 y +'), tasa_edad('90 y +'),
                                                                         total_casos_edad(), total_muertos_edad(), total_tasa_edad(),
                                                                         format_date(fecha_actualizacion_edad())),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    current_state = "INFO_ESPANA_AGE"
    return INFO_ESPANA_AGE


def show_espana_cumulative(update, context):
    global current_state

    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("📈 Incremento", callback_data='espana_increment'),
         InlineKeyboardButton("🧔👩 Casos por edad", callback_data='espana_age')],

        [InlineKeyboardButton("☠ Fallecimientos", callback_data='espana_death'),
         InlineKeyboardButton("🗺 Casos por Región", callback_data='espana_region')],

        [InlineKeyboardButton("📈💯 Casos 100mil", callback_data='espana_100_cumulative'),
         InlineKeyboardButton("📈🆕 Casos 100mil semana", callback_data='espana_100_cumulative_media')],

        [InlineKeyboardButton("☠💯 Fallecimientos 100mil", callback_data='espana_100_death'),
         InlineKeyboardButton("☠🆕 Fallecimientos 100mil semana", callback_data='espana_100_death_media')],

        [InlineKeyboardButton("⬇ Ver todo", callback_data='espana_all')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    grafica_acumulado_espana()

    message.reply_photo(
        photo=open('./img_graficas/acumulado_espana.png', 'rb')
    )

    message.reply_text(
        text="Incremento de casos en {}\n\n"
             "\t - Casos acumulados: <b>{}</b>.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format('España',
                                                                         casos_acumulados_espana(),
                                                                         format_date(fecha_actualizacion_espana())),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    current_state = "INFO_ESPANA_CUMULATIVE"
    return INFO_ESPANA_CUMULATIVE


def show_espana_death(update, context):
    global current_state

    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("📈 Incremento", callback_data='espana_increment'),
         InlineKeyboardButton("🧔👩 Casos por edad", callback_data='espana_age')],

        [InlineKeyboardButton("➕ Casos acumulados", callback_data='espana_cumulative'),
         InlineKeyboardButton("🗺 Casos por Región", callback_data='espana_region')],

        [InlineKeyboardButton("📈💯 Casos 100mil", callback_data='espana_100_cumulative'),
         InlineKeyboardButton("📈🆕 Casos 100mil semana", callback_data='espana_100_cumulative_media')],

        [InlineKeyboardButton("☠💯 Fallecimientos 100mil", callback_data='espana_100_death'),
         InlineKeyboardButton("☠🆕 Fallecimientos 100mil semana", callback_data='espana_100_death_media')],

        [InlineKeyboardButton("⬇ Ver todo", callback_data='espana_all')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    grafica_muertes_espana()

    message.reply_photo(
        photo=open('./img_graficas/fallecidos_espana.png', 'rb')
    )

    message.reply_text(
        text="Evolución de fallecimientos en {}\n\n"
             "\t - Fallecimientos totales: <b>{}</b>.\n"
             "\t - Fallecidos últimas 24h: <b>{}</b>.\n"
             "\t - Media fallecimientos semanal: <b>{}</b>.\n"
             "\t - Tasa de letalidad: <b>{}</b>.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format('España',
                                                                         muertes_totales_espana(),
                                                                         muertes_ultimo_dia_espana(),
                                                                         media_muertes_semana_espana(),
                                                                         tasa_letalidad_espana(),
                                                                         format_date(fecha_actualizacion_muertes())),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    current_state = "INFO_ESPANA_DEATH"
    return INFO_ESPANA_DEATH


def show_espana_region(update, context):
    global current_state

    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("📈 Incremento", callback_data='espana_increment'),
         InlineKeyboardButton("🧔👩 Casos por edad", callback_data='espana_age')],

        [InlineKeyboardButton("➕ Casos acumulados", callback_data='espana_cumulative'),
         InlineKeyboardButton("☠ Fallecimientos", callback_data='espana_death')],

        [InlineKeyboardButton("📈💯 Casos 100mil", callback_data='espana_100_cumulative'),
         InlineKeyboardButton("📈🆕 Casos 100mil semana", callback_data='espana_100_cumulative_media')],

        [InlineKeyboardButton("☠💯 Fallecimientos 100mil", callback_data='espana_100_death'),
         InlineKeyboardButton("☠🆕 Fallecimientos 100mil semana", callback_data='espana_100_death_media')],

        [InlineKeyboardButton("⬇ Ver todo", callback_data='espana_all')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    grafica_casos_comunidad()

    message.reply_photo(
        photo=open('./img_graficas/casos_comunidad.png', 'rb')
    )

    message.reply_text(
        text="Casos por CCAA: \n\n"
             "{}\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(top_5_casos(),
                                                                         format_date(fecha_actualizacion_espana())),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    current_state = "INFO_ESPANA_REGION"
    return INFO_ESPANA_REGION


def show_espana_100_cumulative(update, context):
    global current_state

    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("📈 Incremento", callback_data='espana_increment'),
         InlineKeyboardButton("🧔👩 Casos por edad", callback_data='espana_age')],

        [InlineKeyboardButton("➕ Casos acumulados", callback_data='espana_cumulative'),
         InlineKeyboardButton("☠ Fallecimientos", callback_data='espana_death')],

        [InlineKeyboardButton("🗺 Casos por Región", callback_data='espana_region'),
         InlineKeyboardButton("📈🆕 Casos 100mil semana", callback_data='espana_100_cumulative_media')],

        [InlineKeyboardButton("☠💯 Fallecimientos 100mil", callback_data='espana_100_death'),
         InlineKeyboardButton("☠🆕 Fallecimientos 100mil semana", callback_data='espana_100_death_media')],

        [InlineKeyboardButton("⬇ Ver todo", callback_data='espana_all')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    grafica_casos_100()

    message.reply_photo(
        photo=open('./img_graficas/casos_100.png', 'rb')
    )

    message.reply_text(
        text="Casos por cada 100mil habitantes: \n\n"
             "{}\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(top_5_casos_100(),
                                                                         format_date(fecha_actualizacion_espana())),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    current_state = "INFO_ESPANA_100_CUMULATIVE"
    return INFO_ESPANA_100_CUMULATIVE


def show_espana_100_cumulative_media(update, context):
    global current_state

    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("📈 Incremento", callback_data='espana_increment'),
         InlineKeyboardButton("🧔👩 Casos por edad", callback_data='espana_age')],

        [InlineKeyboardButton("➕ Casos acumulados", callback_data='espana_cumulative'),
         InlineKeyboardButton("☠ Fallecimientos", callback_data='espana_death')],

        [InlineKeyboardButton("🗺 Casos por Región", callback_data='espana_region'),
         InlineKeyboardButton("📈💯 Casos 100mil", callback_data='espana_100_cumulative')],

        [InlineKeyboardButton("☠💯 Fallecimientos 100mil", callback_data='espana_100_death'),
         InlineKeyboardButton("☠🆕 Fallecimientos 100mil semana", callback_data='espana_100_death_media')],

        [InlineKeyboardButton("⬇ Ver todo", callback_data='espana_all')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    grafica_casos_100_semana()

    message.reply_photo(
        photo=open('./img_graficas/casos_100_semana.png', 'rb')
    )

    message.reply_text(
        text="Media semanal por cada 100mil habitantes: \n\n"
             "{}\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(top_5_casos_100_semana(),
                                                                         format_date(fecha_actualizacion_espana())),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    current_state = "INFO_ESPANA_100_CUMULATIVE_MEDIA"
    return INFO_ESPANA_100_CUMULATIVE_MEDIA


def show_espana_100_death(update, context):
    global current_state

    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("📈 Incremento", callback_data='espana_increment'),
         InlineKeyboardButton("🧔👩 Casos por edad", callback_data='espana_age')],

        [InlineKeyboardButton("➕ Casos acumulados", callback_data='espana_cumulative'),
         InlineKeyboardButton("☠ Fallecimientos", callback_data='espana_death')],

        [InlineKeyboardButton("🗺 Casos por Región", callback_data='espana_region'),
         InlineKeyboardButton("📈💯 Casos 100mil", callback_data='espana_100_cumulative')],

        [InlineKeyboardButton("📈🆕 Casos 100mil semana", callback_data='espana_100_cumulative_media'),
         InlineKeyboardButton("☠🆕 Fallecimientos 100mil semana", callback_data='espana_100_death_media')],

        [InlineKeyboardButton("⬇ Ver todo", callback_data='espana_all')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    grafica_muertes_100()

    message.reply_photo(
        photo=open('./img_graficas/muertes_100.png', 'rb')
    )

    message.reply_text(
        text="Fallecimientos por cada 100mil habitantes: \n\n"
             "{}\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(top_5_muertes_100(),
                                                                         format_date(fecha_actualizacion_muertes())),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    current_state = "INFO_ESPANA_100_DEATH"
    return INFO_ESPANA_100_DEATH


def show_espana_100_death_media(update, context):
    global current_state

    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("📈 Incremento", callback_data='espana_increment'),
         InlineKeyboardButton("🧔👩 Casos por edad", callback_data='espana_age')],

        [InlineKeyboardButton("➕ Casos acumulados", callback_data='espana_cumulative'),
         InlineKeyboardButton("☠ Fallecimientos", callback_data='espana_death')],

        [InlineKeyboardButton("🗺 Casos por Región", callback_data='espana_region'),
         InlineKeyboardButton("📈💯 Casos 100mil", callback_data='espana_100_cumulative')],

        [InlineKeyboardButton("📈🆕 Casos 100mil semana", callback_data='espana_100_cumulative_media'),
         InlineKeyboardButton("☠💯 Fallecimientos 100mil", callback_data='espana_100_death')],

        [InlineKeyboardButton("⬇ Ver todo", callback_data='espana_all')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    grafica_muertes_100_semana()

    message.reply_photo(
        photo=open('./img_graficas/muertes_100_semana.png', 'rb')
    )

    message.reply_text(
        text="Media fallecimientos semanal por cada 100mil habitantes: \n\n"
             "{}\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(top_5_muertes_100_semana(),
                                                                         format_date(fecha_actualizacion_muertes())),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    current_state = "INFO_ESPANA_100_DEATH_MEDIA"
    return INFO_ESPANA_100_DEATH_MEDIA


def show_espana_all(update, context):
    global current_state

    message = update.callback_query.message

    keyboard = [
        [InlineKeyboardButton("📈 Incremento", callback_data='espana_increment'),
         InlineKeyboardButton("🧔👩 Casos por edad", callback_data='espana_age'),
         InlineKeyboardButton("➕ Casos acumulados", callback_data='espana_cumulative')],

        [InlineKeyboardButton("☠ Fallecimientos", callback_data='espana_death'),
         InlineKeyboardButton("🗺 Casos por Región", callback_data='espana_region')],

        [InlineKeyboardButton("📈💯 Casos 100mil", callback_data='espana_100_cumulative'),
         InlineKeyboardButton("📈🆕 Casos 100mil semana", callback_data='espana_100_cumulative_media')],

        [InlineKeyboardButton("☠💯 Fallecimientos 100mil", callback_data='espana_100_death'),
         InlineKeyboardButton("☠🆕 Fallecimientos 100mil semana", callback_data='espana_100_death_media')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    grafica_incremento_espana()

    message.reply_photo(
        photo=open('./img_graficas/incremento_espana.png', 'rb')
    )

    message.reply_text(
        text="Incremento de casos en {}\n\n"
             "\t - Casos acumulados: <b>{}</b>.\n"
             "\t - Incremento de casos últimas 24h: <b>{}</b>.\n"
             "\t - Media del incremento de casos semanal: <b>{}</b>.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format('España',
                                                                         casos_acumulados_espana(),
                                                                         incremento_ultimo_dia_espana(),
                                                                         media_casos_semana_espana(),
                                                                         format_date(fecha_actualizacion_espana())),
        parse_mode='HTML',
    )

    grafica_edades()

    message.reply_photo(
        photo=open('./img_graficas/casos_edad_espana.png', 'rb')
    )

    message.reply_text(
        text="Casos (fallecidos) por edad: \n\n"
             "0-9: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "10-19: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "20-29: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "30-39: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "40-49: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "50-59: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "60-69: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "70-79: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "80-89: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "90 y +: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n"
             "Total: <b>{}</b> (<b>{}</b>) Tasa de letalidad: <b>{}</b>%.\n\n"
             "Datos obtenidos del análisis sobre los casos notificados con información disponible de edad y sexo.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(casos_edad('0-9'), muertos_edad('0-9'),
                                                                         tasa_edad('0-9'),
                                                                         casos_edad('10-19'), muertos_edad('10-19'),
                                                                         tasa_edad('10-19'),
                                                                         casos_edad('20-29'), muertos_edad('20-29'),
                                                                         tasa_edad('20-29'),
                                                                         casos_edad('30-39'), muertos_edad('30-39'),
                                                                         tasa_edad('30-39'),
                                                                         casos_edad('40-49'), muertos_edad('40-49'),
                                                                         tasa_edad('40-49'),
                                                                         casos_edad('50-59'), muertos_edad('50-59'),
                                                                         tasa_edad('50-59'),
                                                                         casos_edad('60-69'), muertos_edad('60-69'),
                                                                         tasa_edad('60-69'),
                                                                         casos_edad('70-79'), muertos_edad('70-79'),
                                                                         tasa_edad('70-79'),
                                                                         casos_edad('80-89'), muertos_edad('80-89'),
                                                                         tasa_edad('80-89'),
                                                                         casos_edad('90 y +'), muertos_edad('90 y +'),
                                                                         tasa_edad('90 y +'),
                                                                         total_casos_edad(), total_muertos_edad(),
                                                                         total_tasa_edad(),
                                                                         format_date(fecha_actualizacion_edad())),
        parse_mode='HTML',
    )

    grafica_acumulado_espana()

    message.reply_photo(
        photo=open('./img_graficas/acumulado_espana.png', 'rb')
    )

    message.reply_text(
        text="Incremento de casos en {}\n\n"
             "\t - Casos acumulados: <b>{}</b>.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format('España',
                                                                         casos_acumulados_espana(),
                                                                         format_date(fecha_actualizacion_espana())),
        parse_mode='HTML',
    )

    grafica_muertes_espana()

    message.reply_photo(
        photo=open('./img_graficas/fallecidos_espana.png', 'rb')
    )

    message.reply_text(
        text="Evolución de fallecimientos en {}\n\n"
             "\t - Fallecimientos totales: <b>{}</b>.\n"
             "\t - Fallecidos últimas 24h: <b>{}</b>.\n"
             "\t - Media fallecimientos semanal: <b>{}</b>.\n"
             "\t - Tasa de letalidad: <b>{}</b>.\n\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format('España',
                                                                         muertes_totales_espana(),
                                                                         muertes_ultimo_dia_espana(),
                                                                         media_muertes_semana_espana(),
                                                                         tasa_letalidad_espana(),
                                                                         format_date(fecha_actualizacion_muertes())),
        parse_mode='HTML',
    )

    grafica_casos_comunidad()

    message.reply_photo(
        photo=open('./img_graficas/casos_comunidad.png', 'rb')
    )

    message.reply_text(
        text="Casos por CCAA: \n\n"
             "{}\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(top_5_casos(),
                                                                         format_date(fecha_actualizacion_espana())),
        parse_mode='HTML',
    )

    grafica_casos_100()

    message.reply_photo(
        photo=open('./img_graficas/casos_100.png', 'rb')
    )

    message.reply_text(
        text="Casos por cada 100mil habitantes: \n\n"
             "{}\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(top_5_casos_100(),
                                                                         format_date(fecha_actualizacion_espana())),
        parse_mode='HTML',
    )

    grafica_casos_100_semana()

    message.reply_photo(
        photo=open('./img_graficas/casos_100_semana.png', 'rb')
    )

    message.reply_text(
        text="Media semanal por cada 100mil habitantes: \n\n"
             "{}\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(top_5_casos_100_semana(),
                                                                         format_date(fecha_actualizacion_espana())),
        parse_mode='HTML',
    )

    grafica_muertes_100()

    message.reply_photo(
        photo=open('./img_graficas/muertes_100.png', 'rb')
    )

    message.reply_text(
        text="Fallecimientos por cada 100mil habitantes: \n\n"
             "{}\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(top_5_muertes_100(),
                                                                         format_date(fecha_actualizacion_muertes())),
        parse_mode='HTML',
    )

    grafica_muertes_100_semana()

    message.reply_photo(
        photo=open('./img_graficas/muertes_100_semana.png', 'rb')
    )

    message.reply_text(
        text="Media fallecimientos semanal por cada 100mil habitantes: \n\n"
             "{}\n"
             "Información actualizada a {}.\n"
             "<b>Los datos pueden tardar unos días en consolidarse y "
             "pueden no estar actualizados a la fecha actual</b>".format(top_5_muertes_100_semana(),
                                                                         format_date(fecha_actualizacion_muertes())),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    current_state = "INFO_ESPANA_ALL"
    return INFO_ESPANA_ALL


def show_info(update, context):
    global current_state

    update.message.reply_text(
        text="Este proyecto ha sido desarrollado como Trabajo Fin de Grado\n\n"
             "Este proyecto cuenta con una licencia AGPL, por lo que podeis usarlo si os es útil\n\n"
             "<b>Fuentes de datos</b>\n"
             "Fuentes de datos para España y sus comunidades de "
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

def main():
    # global conv_handler

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
                                               CallbackQueryHandler(show_cataluna_info, pattern='cataluna_info'),
                                               CallbackQueryHandler(show_ceuta_info, pattern='ceuta_info'),
                                               CallbackQueryHandler(show_extremadura_info, pattern='extremadura_info'),
                                               CallbackQueryHandler(show_galicia_info, pattern='galicia_info'),
                                               CallbackQueryHandler(show_baleares_info, pattern='baleares_info'),
                                               CallbackQueryHandler(show_larioja_info, pattern='larioja_info'),
                                               CallbackQueryHandler(show_madrid_info, pattern='madrid_info'),
                                               CallbackQueryHandler(show_melilla_info, pattern='melilla_info'),
                                               CallbackQueryHandler(show_murcia_info, pattern='murcia_info'),
                                               CallbackQueryHandler(show_navarra_info, pattern='navarra_info'),
                                               CallbackQueryHandler(show_paisvasco_info, pattern='paisvasco_info'),
                                               CallbackQueryHandler(show_espana_info, pattern='espana_info'),
                                           ],
                                           HELP: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                           ],
                                           STATUS_INFO: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
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
                                           ],
                                           INFO_CATALUNA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cataluna_increment,
                                                                    pattern='cataluna_increment'),
                                               CallbackQueryHandler(show_cataluna_cumulative,
                                                                    pattern='cataluna_cumulative'),
                                               CallbackQueryHandler(show_cataluna_death,
                                                                    pattern='cataluna_death'),
                                               CallbackQueryHandler(show_cataluna_hospital,
                                                                    pattern='cataluna_hospital'),
                                               CallbackQueryHandler(show_cataluna_all,
                                                                    pattern='cataluna_all'),
                                           ],
                                           INFO_CATALUNA_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cataluna_cumulative,
                                                                    pattern='cataluna_cumulative'),
                                               CallbackQueryHandler(show_cataluna_death,
                                                                    pattern='cataluna_death'),
                                               CallbackQueryHandler(show_cataluna_hospital,
                                                                    pattern='cataluna_hospital'),
                                               CallbackQueryHandler(show_cataluna_all,
                                                                    pattern='cataluna_all'),
                                           ],
                                           INFO_CATALUNA_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cataluna_increment,
                                                                    pattern='cataluna_increment'),
                                               CallbackQueryHandler(show_cataluna_death,
                                                                    pattern='cataluna_death'),
                                               CallbackQueryHandler(show_cataluna_hospital,
                                                                    pattern='cataluna_hospital'),
                                               CallbackQueryHandler(show_cataluna_all,
                                                                    pattern='cataluna_all'),
                                           ],
                                           INFO_CATALUNA_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cataluna_increment,
                                                                    pattern='cataluna_increment'),
                                               CallbackQueryHandler(show_cataluna_cumulative,
                                                                    pattern='cataluna_cumulative'),
                                               CallbackQueryHandler(show_cataluna_hospital,
                                                                    pattern='cataluna_hospital'),
                                               CallbackQueryHandler(show_cataluna_all,
                                                                    pattern='cataluna_all'),
                                           ],
                                           INFO_CATALUNA_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cataluna_increment,
                                                                    pattern='cataluna_increment'),
                                               CallbackQueryHandler(show_cataluna_cumulative,
                                                                    pattern='cataluna_cumulative'),
                                               CallbackQueryHandler(show_cataluna_death,
                                                                    pattern='cataluna_death'),
                                               CallbackQueryHandler(show_cataluna_all,
                                                                    pattern='cataluna_all'),
                                           ],
                                           INFO_CATALUNA_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_cataluna_increment,
                                                                    pattern='cataluna_increment'),
                                               CallbackQueryHandler(show_cataluna_cumulative,
                                                                    pattern='cataluna_cumulative'),
                                               CallbackQueryHandler(show_cataluna_death,
                                                                    pattern='cataluna_death'),
                                               CallbackQueryHandler(show_cataluna_hospital,
                                                                    pattern='cataluna_hospital'),
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
                                           ],
                                           INFO_NAVARRA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_navarra_increment,
                                                                    pattern='navarra_increment'),
                                               CallbackQueryHandler(show_navarra_cumulative,
                                                                    pattern='navarra_cumulative'),
                                               CallbackQueryHandler(show_navarra_death,
                                                                    pattern='navarra_death'),
                                               CallbackQueryHandler(show_navarra_hospital,
                                                                    pattern='navarra_hospital'),
                                               CallbackQueryHandler(show_navarra_all,
                                                                    pattern='navarra_all'),
                                           ],
                                           INFO_NAVARRA_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_navarra_cumulative,
                                                                    pattern='navarra_cumulative'),
                                               CallbackQueryHandler(show_navarra_death,
                                                                    pattern='navarra_death'),
                                               CallbackQueryHandler(show_navarra_hospital,
                                                                    pattern='navarra_hospital'),
                                               CallbackQueryHandler(show_navarra_all,
                                                                    pattern='navarra_all'),
                                           ],
                                           INFO_NAVARRA_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_navarra_increment,
                                                                    pattern='navarra_increment'),
                                               CallbackQueryHandler(show_navarra_death,
                                                                    pattern='navarra_death'),
                                               CallbackQueryHandler(show_navarra_hospital,
                                                                    pattern='navarra_hospital'),
                                               CallbackQueryHandler(show_navarra_all,
                                                                    pattern='navarra_all'),
                                           ],
                                           INFO_NAVARRA_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_navarra_increment,
                                                                    pattern='navarra_increment'),
                                               CallbackQueryHandler(show_navarra_cumulative,
                                                                    pattern='navarra_cumulative'),
                                               CallbackQueryHandler(show_navarra_hospital,
                                                                    pattern='navarra_hospital'),
                                               CallbackQueryHandler(show_navarra_all,
                                                                    pattern='navarra_all'),
                                           ],
                                           INFO_NAVARRA_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_navarra_increment,
                                                                    pattern='navarra_increment'),
                                               CallbackQueryHandler(show_navarra_cumulative,
                                                                    pattern='navarra_cumulative'),
                                               CallbackQueryHandler(show_navarra_death,
                                                                    pattern='navarra_death'),
                                               CallbackQueryHandler(show_navarra_all,
                                                                    pattern='navarra_all'),
                                           ],
                                           INFO_NAVARRA_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_navarra_increment,
                                                                    pattern='navarra_increment'),
                                               CallbackQueryHandler(show_navarra_cumulative,
                                                                    pattern='navarra_cumulative'),
                                               CallbackQueryHandler(show_navarra_death,
                                                                    pattern='navarra_death'),
                                               CallbackQueryHandler(show_navarra_hospital,
                                                                    pattern='navarra_hospital'),
                                           ],
                                           INFO_PAISVASCO: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_paisvasco_increment,
                                                                    pattern='paisvasco_increment'),
                                               CallbackQueryHandler(show_paisvasco_cumulative,
                                                                    pattern='paisvasco_cumulative'),
                                               CallbackQueryHandler(show_paisvasco_death,
                                                                    pattern='paisvasco_death'),
                                               CallbackQueryHandler(show_paisvasco_hospital,
                                                                    pattern='paisvasco_hospital'),
                                               CallbackQueryHandler(show_paisvasco_all,
                                                                    pattern='paisvasco_all'),
                                           ],
                                           INFO_PAISVASCO_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_paisvasco_cumulative,
                                                                    pattern='paisvasco_cumulative'),
                                               CallbackQueryHandler(show_paisvasco_death,
                                                                    pattern='paisvasco_death'),
                                               CallbackQueryHandler(show_paisvasco_hospital,
                                                                    pattern='paisvasco_hospital'),
                                               CallbackQueryHandler(show_paisvasco_all,
                                                                    pattern='paisvasco_all'),
                                           ],
                                           INFO_PAISVASCO_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_paisvasco_increment,
                                                                    pattern='paisvasco_increment'),
                                               CallbackQueryHandler(show_paisvasco_death,
                                                                    pattern='paisvasco_death'),
                                               CallbackQueryHandler(show_paisvasco_hospital,
                                                                    pattern='paisvasco_hospital'),
                                               CallbackQueryHandler(show_paisvasco_all,
                                                                    pattern='paisvasco_all'),
                                           ],
                                           INFO_PAISVASCO_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_paisvasco_increment,
                                                                    pattern='paisvasco_increment'),
                                               CallbackQueryHandler(show_paisvasco_cumulative,
                                                                    pattern='paisvasco_cumulative'),
                                               CallbackQueryHandler(show_paisvasco_hospital,
                                                                    pattern='paisvasco_hospital'),
                                               CallbackQueryHandler(show_paisvasco_all,
                                                                    pattern='paisvasco_all'),
                                           ],
                                           INFO_PAISVASCO_HOSPITAL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_paisvasco_increment,
                                                                    pattern='paisvasco_increment'),
                                               CallbackQueryHandler(show_paisvasco_cumulative,
                                                                    pattern='paisvasco_cumulative'),
                                               CallbackQueryHandler(show_paisvasco_death,
                                                                    pattern='paisvasco_death'),
                                               CallbackQueryHandler(show_paisvasco_all,
                                                                    pattern='paisvasco_all'),
                                           ],
                                           INFO_PAISVASCO_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_paisvasco_increment,
                                                                    pattern='paisvasco_increment'),
                                               CallbackQueryHandler(show_paisvasco_cumulative,
                                                                    pattern='paisvasco_cumulative'),
                                               CallbackQueryHandler(show_paisvasco_death,
                                                                    pattern='paisvasco_death'),
                                               CallbackQueryHandler(show_paisvasco_hospital,
                                                                    pattern='paisvasco_hospital'),
                                           ],
                                           INFO_ESPANA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_espana_increment,
                                                                    pattern='espana_increment'),
                                               CallbackQueryHandler(show_espana_age,
                                                                    pattern='espana_age'),
                                               CallbackQueryHandler(show_espana_cumulative,
                                                                    pattern='espana_cumulative'),
                                               CallbackQueryHandler(show_espana_death,
                                                                    pattern='espana_death'),
                                               CallbackQueryHandler(show_espana_region,
                                                                    pattern='espana_region'),
                                               CallbackQueryHandler(show_espana_100_cumulative,
                                                                    pattern='espana_100_cumulative'),
                                               CallbackQueryHandler(show_espana_100_cumulative_media,
                                                                    pattern='espana_100_cumulative_media'),
                                               CallbackQueryHandler(show_espana_100_death,
                                                                    pattern='espana_100_death'),
                                               CallbackQueryHandler(show_espana_100_death_media,
                                                                    pattern='espana_100_death_media'),
                                               CallbackQueryHandler(show_espana_all,
                                                                    pattern='espana_all'),
                                           ],
                                           INFO_ESPANA_INCREMENT: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_espana_age,
                                                                    pattern='espana_age'),
                                               CallbackQueryHandler(show_espana_cumulative,
                                                                    pattern='espana_cumulative'),
                                               CallbackQueryHandler(show_espana_death,
                                                                    pattern='espana_death'),
                                               CallbackQueryHandler(show_espana_region,
                                                                    pattern='espana_region'),
                                               CallbackQueryHandler(show_espana_100_cumulative,
                                                                    pattern='espana_100_cumulative'),
                                               CallbackQueryHandler(show_espana_100_cumulative_media,
                                                                    pattern='espana_100_cumulative_media'),
                                               CallbackQueryHandler(show_espana_100_death,
                                                                    pattern='espana_100_death'),
                                               CallbackQueryHandler(show_espana_100_death_media,
                                                                    pattern='espana_100_death_media'),
                                               CallbackQueryHandler(show_espana_all,
                                                                    pattern='espana_all'),
                                           ],
                                           INFO_ESPANA_AGE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_espana_increment,
                                                                    pattern='espana_increment'),
                                               CallbackQueryHandler(show_espana_cumulative,
                                                                    pattern='espana_cumulative'),
                                               CallbackQueryHandler(show_espana_death,
                                                                    pattern='espana_death'),
                                               CallbackQueryHandler(show_espana_region,
                                                                    pattern='espana_region'),
                                               CallbackQueryHandler(show_espana_100_cumulative,
                                                                    pattern='espana_100_cumulative'),
                                               CallbackQueryHandler(show_espana_100_cumulative_media,
                                                                    pattern='espana_100_cumulative_media'),
                                               CallbackQueryHandler(show_espana_100_death,
                                                                    pattern='espana_100_death'),
                                               CallbackQueryHandler(show_espana_100_death_media,
                                                                    pattern='espana_100_death_media'),
                                               CallbackQueryHandler(show_espana_all,
                                                                    pattern='espana_all'),
                                           ],
                                           INFO_ESPANA_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_espana_increment,
                                                                    pattern='espana_increment'),
                                               CallbackQueryHandler(show_espana_age,
                                                                    pattern='espana_age'),
                                               CallbackQueryHandler(show_espana_death,
                                                                    pattern='espana_death'),
                                               CallbackQueryHandler(show_espana_region,
                                                                    pattern='espana_region'),
                                               CallbackQueryHandler(show_espana_100_cumulative,
                                                                    pattern='espana_100_cumulative'),
                                               CallbackQueryHandler(show_espana_100_cumulative_media,
                                                                    pattern='espana_100_cumulative_media'),
                                               CallbackQueryHandler(show_espana_100_death,
                                                                    pattern='espana_100_death'),
                                               CallbackQueryHandler(show_espana_100_death_media,
                                                                    pattern='espana_100_death_media'),
                                               CallbackQueryHandler(show_espana_all,
                                                                    pattern='espana_all'),
                                           ],
                                           INFO_ESPANA_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_espana_increment,
                                                                    pattern='espana_increment'),
                                               CallbackQueryHandler(show_espana_age,
                                                                    pattern='espana_age'),
                                               CallbackQueryHandler(show_espana_cumulative,
                                                                    pattern='espana_cumulative'),
                                               CallbackQueryHandler(show_espana_region,
                                                                    pattern='espana_region'),
                                               CallbackQueryHandler(show_espana_100_cumulative,
                                                                    pattern='espana_100_cumulative'),
                                               CallbackQueryHandler(show_espana_100_cumulative_media,
                                                                    pattern='espana_100_cumulative_media'),
                                               CallbackQueryHandler(show_espana_100_death,
                                                                    pattern='espana_100_death'),
                                               CallbackQueryHandler(show_espana_100_death_media,
                                                                    pattern='espana_100_death_media'),
                                               CallbackQueryHandler(show_espana_all,
                                                                    pattern='espana_all'),
                                           ],
                                           INFO_ESPANA_REGION: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_espana_increment,
                                                                    pattern='espana_increment'),
                                               CallbackQueryHandler(show_espana_age,
                                                                    pattern='espana_age'),
                                               CallbackQueryHandler(show_espana_cumulative,
                                                                    pattern='espana_cumulative'),
                                               CallbackQueryHandler(show_espana_death,
                                                                    pattern='espana_death'),
                                               CallbackQueryHandler(show_espana_100_cumulative,
                                                                    pattern='espana_100_cumulative'),
                                               CallbackQueryHandler(show_espana_100_cumulative_media,
                                                                    pattern='espana_100_cumulative_media'),
                                               CallbackQueryHandler(show_espana_100_death,
                                                                    pattern='espana_100_death'),
                                               CallbackQueryHandler(show_espana_100_death_media,
                                                                    pattern='espana_100_death_media'),
                                               CallbackQueryHandler(show_espana_all,
                                                                    pattern='espana_all'),
                                           ],
                                           INFO_ESPANA_100_CUMULATIVE: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_espana_increment,
                                                                    pattern='espana_increment'),
                                               CallbackQueryHandler(show_espana_age,
                                                                    pattern='espana_age'),
                                               CallbackQueryHandler(show_espana_cumulative,
                                                                    pattern='espana_cumulative'),
                                               CallbackQueryHandler(show_espana_death,
                                                                    pattern='espana_death'),
                                               CallbackQueryHandler(show_espana_region,
                                                                    pattern='espana_region'),
                                               CallbackQueryHandler(show_espana_100_cumulative_media,
                                                                    pattern='espana_100_cumulative_media'),
                                               CallbackQueryHandler(show_espana_100_death,
                                                                    pattern='espana_100_death'),
                                               CallbackQueryHandler(show_espana_100_death_media,
                                                                    pattern='espana_100_death_media'),
                                               CallbackQueryHandler(show_espana_all,
                                                                    pattern='espana_all'),
                                           ],
                                           INFO_ESPANA_100_CUMULATIVE_MEDIA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_espana_increment,
                                                                    pattern='espana_increment'),
                                               CallbackQueryHandler(show_espana_age,
                                                                    pattern='espana_age'),
                                               CallbackQueryHandler(show_espana_cumulative,
                                                                    pattern='espana_cumulative'),
                                               CallbackQueryHandler(show_espana_death,
                                                                    pattern='espana_death'),
                                               CallbackQueryHandler(show_espana_region,
                                                                    pattern='espana_region'),
                                               CallbackQueryHandler(show_espana_100_cumulative,
                                                                    pattern='espana_100_cumulative'),
                                               CallbackQueryHandler(show_espana_100_death,
                                                                    pattern='espana_100_death'),
                                               CallbackQueryHandler(show_espana_100_death_media,
                                                                    pattern='espana_100_death_media'),
                                               CallbackQueryHandler(show_espana_all,
                                                                    pattern='espana_all'),
                                           ],
                                           INFO_ESPANA_100_DEATH: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_espana_increment,
                                                                    pattern='espana_increment'),
                                               CallbackQueryHandler(show_espana_age,
                                                                    pattern='espana_age'),
                                               CallbackQueryHandler(show_espana_cumulative,
                                                                    pattern='espana_cumulative'),
                                               CallbackQueryHandler(show_espana_death,
                                                                    pattern='espana_death'),
                                               CallbackQueryHandler(show_espana_region,
                                                                    pattern='espana_region'),
                                               CallbackQueryHandler(show_espana_100_cumulative,
                                                                    pattern='espana_100_cumulative'),
                                               CallbackQueryHandler(show_espana_100_cumulative_media,
                                                                    pattern='espana_100_cumulative_media'),
                                               CallbackQueryHandler(show_espana_100_death_media,
                                                                    pattern='espana_100_death_media'),
                                               CallbackQueryHandler(show_espana_all,
                                                                    pattern='espana_all'),
                                           ],
                                           INFO_ESPANA_100_DEATH_MEDIA: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_espana_increment,
                                                                    pattern='espana_increment'),
                                               CallbackQueryHandler(show_espana_age,
                                                                    pattern='espana_age'),
                                               CallbackQueryHandler(show_espana_cumulative,
                                                                    pattern='espana_cumulative'),
                                               CallbackQueryHandler(show_espana_death,
                                                                    pattern='espana_death'),
                                               CallbackQueryHandler(show_espana_region,
                                                                    pattern='espana_region'),
                                               CallbackQueryHandler(show_espana_100_cumulative,
                                                                    pattern='espana_100_cumulative'),
                                               CallbackQueryHandler(show_espana_100_cumulative_media,
                                                                    pattern='espana_100_cumulative_media'),
                                               CallbackQueryHandler(show_espana_100_death,
                                                                    pattern='espana_100_death'),
                                               CallbackQueryHandler(show_espana_all,
                                                                    pattern='espana_all'),
                                           ],
                                           INFO_ESPANA_ALL: [
                                               MessageHandler(Filters.regex('Menú'), show_inicio),
                                               MessageHandler(Filters.regex('🆘 Ayuda'), help_handler),
                                               MessageHandler(Filters.regex('Información'), show_info),
                                               MessageHandler(Filters.text & (~Filters.command), any_message),
                                               CallbackQueryHandler(show_espana_increment,
                                                                    pattern='espana_increment'),
                                               CallbackQueryHandler(show_espana_age,
                                                                    pattern='espana_age'),
                                               CallbackQueryHandler(show_espana_cumulative,
                                                                    pattern='espana_cumulative'),
                                               CallbackQueryHandler(show_espana_death,
                                                                    pattern='espana_death'),
                                               CallbackQueryHandler(show_espana_region,
                                                                    pattern='espana_region'),
                                               CallbackQueryHandler(show_espana_100_cumulative,
                                                                    pattern='espana_100_cumulative'),
                                               CallbackQueryHandler(show_espana_100_cumulative_media,
                                                                    pattern='espana_100_cumulative_media'),
                                               CallbackQueryHandler(show_espana_100_death,
                                                                    pattern='espana_100_death'),
                                               CallbackQueryHandler(show_espana_100_death_media,
                                                                    pattern='espana_100_death_media'),
                                           ],
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
                                                                pattern='cataluna_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cataluna_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cataluna_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cataluna_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cataluna_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='cataluna_all'),
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
                                                                pattern='navarra_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='navarra_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='navarra_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='navarra_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='navarra_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='navarra_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='paisvasco_info'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='paisvasco_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='paisvasco_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='paisvasco_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='paisvasco_hospital'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='paisvasco_all'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='espana_increment'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='espana_age'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='espana_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='espana_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='espana_region'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='espana_100_cumulative'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='espana_100_cumulative_media'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='espana_100_death'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='espana_100_death_media'),
                                           CallbackQueryHandler(usuario_pulsa_boton_anterior,
                                                                pattern='espana_all'),
                                       ])

    updater.dispatcher.add_handler(conv_handler)

    run(updater)


if __name__ == '__main__':
    main()