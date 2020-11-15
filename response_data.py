from dataframes import *
from datetime import date, timedelta, datetime

ccaa = ['Andalucía', 'Aragón', 'Asturias', 'Baleares', 'C. Valenciana', 'Canarias', 'Cantabria',
                  'Castilla La Mancha', 'Castilla y León', 'Cataluña', 'Ceuta', 'Extremadura', 'Galicia', 'La Rioja',
                  'Madrid', 'Melilla', 'Murcia', 'Navarra', 'País Vasco']


def format_date(fecha):
    return datetime.strptime(fecha, "%Y-%m-%d").strftime("%d-%m-%Y")


def casos_acumulados(current_autonomy):
    return str(df_ccaa_casos.groupby(['ccaa'])['num_casos'].sum()[current_autonomy])


def incremento_ultimo_dia(current_autonomy):
    df_loc = df_ccaa_casos.loc[(df_ccaa_casos['fecha'] == fecha_actualizacion(current_autonomy)) &
                               (df_ccaa_casos['ccaa'] == current_autonomy)]
    return str(df_loc['num_casos'].values[0])


def media_casos_semana(current_autonomy):
    ultima_fecha = fecha_actualizacion(current_autonomy)
    fecha = datetime.strptime(ultima_fecha, "%Y-%m-%d")

    total = 0
    for i in range(7):
        fecha2 = fecha - timedelta(days=i)
        fecha_semana_antes = fecha2.strftime("%Y-%m-%d")

        df_loc = df_ccaa_casos.loc[(df_ccaa_casos['fecha'] == fecha_semana_antes) &
                                   (df_ccaa_casos['ccaa'] == current_autonomy)]
        total += int(df_loc['num_casos'].values[0])

    return str(round(total/7, 1))


def fecha_actualizacion(current_autonomy):
    actual_day = date.today()
    dias_antes = 0
    day_before = timedelta(days=dias_antes)

    # La primera fecha de la que se tiene datos
    while df_ccaa_casos.loc[df_ccaa_casos['fecha'] == str(actual_day-day_before)].empty:
        dias_antes += 1
        day_before = timedelta(days=dias_antes)

    # Los ultimos datos de la ccaa
    df_loc = df_ccaa_casos.loc[(df_ccaa_casos['fecha'] == str(actual_day-day_before)) &
                               (df_ccaa_casos['ccaa'] == current_autonomy)]

    while df_loc['num_casos'].values[0] == 0:
        dias_antes += 1
        day_before = timedelta(days=dias_antes)
        df_loc = df_ccaa_casos.loc[(df_ccaa_casos['fecha'] == str(actual_day-day_before)) &
                                   (df_ccaa_casos['ccaa'] == current_autonomy)]

    return str(actual_day-day_before)


def muertes_totales(current_autonomy):
    return str(df_ccaa_muertes.groupby(['CCAA'])['Fallecidos'].sum()[current_autonomy])


def muertes_ultimo_dia(current_autonomy):
    df_loc = df_ccaa_muertes.loc[(df_ccaa_muertes['Fecha'] == fecha_actualizacion_muertes()) &
                                 (df_ccaa_muertes['CCAA'] == current_autonomy)]
    return str(df_loc['Fallecidos'].values[0])


def media_muertes_semana(current_autonomy):
    ultima_fecha = fecha_actualizacion_muertes()
    fecha = datetime.strptime(ultima_fecha, "%Y-%m-%d")

    total = 0
    for i in range(7):
        fecha2 = fecha - timedelta(days=i)
        fecha_semana_antes = fecha2.strftime("%Y-%m-%d")

        df_loc = df_ccaa_muertes.loc[(df_ccaa_muertes['Fecha'] == fecha_semana_antes) &
                                     (df_ccaa_muertes['CCAA'] == current_autonomy)]
        total += int(df_loc['Fallecidos'].values[0])

    return str(round(total/7, 1))


def tasa_letalidad(current_autonomy):
    return str(round(int(muertes_totales(current_autonomy))*100/int(casos_acumulados(current_autonomy)), 2))


def fecha_actualizacion_muertes():
    actual_day = date.today()
    dias_antes = 0
    day_before = timedelta(days=dias_antes)

    # La primera fecha de la que se tiene datos
    while df_ccaa_muertes.loc[df_ccaa_muertes['Fecha'] == str(actual_day - day_before)].empty:
        dias_antes += 1
        day_before = timedelta(days=dias_antes)

    return str(actual_day-day_before)


def pacientes_ingresados(current_autonomy):
    df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == fecha_actualizacion_hospital(current_autonomy)) &
                                  (df_ccaa_hospital['CCAA'] == current_autonomy)]
    return str(int(df_loc['Total Pacientes COVID ingresados']))


def porcentaje_camas_ocupadas(current_autonomy):
    df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == fecha_actualizacion_hospital(current_autonomy)) &
                                  (df_ccaa_hospital['CCAA'] == current_autonomy)]
    return str(df_loc['% Camas Ocupadas COVID'].values[0])


def pacientes_ingresados_uci(current_autonomy):
    df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == fecha_actualizacion_hospital(current_autonomy)) &
                                  (df_ccaa_hospital['CCAA'] == current_autonomy)]
    return str(int(df_loc['Total pacientes COVID en UCI']))


def porcentaje_camas_uci_ocupadas(current_autonomy):
    df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == fecha_actualizacion_hospital(current_autonomy)) &
                                  (df_ccaa_hospital['CCAA'] == current_autonomy)]
    return str(df_loc['% Camas Ocupadas UCI COVID'].values[0])


def ingresados_ultimo_dia(current_autonomy):
    df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == fecha_actualizacion_hospital(current_autonomy)) &
                                  (df_ccaa_hospital['CCAA'] == current_autonomy)]
    return str(int(df_loc['Ingresos COVID últimas 24 h']))


def altas_ultimo_dia(current_autonomy):
    df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == fecha_actualizacion_hospital(current_autonomy)) &
                                  (df_ccaa_hospital['CCAA'] == current_autonomy)]
    return str(int(df_loc['Altas COVID últimas 24 h']))


def fecha_actualizacion_hospital(current_autonomy):
    actual_day = date.today()
    dias_antes = 0
    day_before = timedelta(days=dias_antes)

    # La primera fecha de la que se tiene datos
    while df_ccaa_hospital.loc[df_ccaa_hospital['Fecha'] == str(actual_day-day_before)].empty:
        dias_antes += 1
        day_before = timedelta(days=dias_antes)

    # Los ultimos datos de la ccaa
    df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == str(actual_day-day_before)) &
                                  (df_ccaa_hospital['CCAA'] == current_autonomy)]

    while df_loc['Total Pacientes COVID ingresados'].values[0] == 0:
        dias_antes += 1
        day_before = timedelta(days=dias_antes)
        df_loc = df_ccaa_hospital.loc[(df_ccaa_hospital['Fecha'] == str(actual_day-day_before)) &
                                      (df_ccaa_hospital['CCAA'] == current_autonomy)]

    return str(actual_day-day_before)


def casos_acumulados_espana():
    return str(df_ccaa_casos['num_casos'].sum())


def incremento_ultimo_dia_espana():
    df_loc = df_ccaa_casos.loc[df_ccaa_casos['fecha'] == fecha_actualizacion_espana()]
    return str(df_loc['num_casos'].sum())


def media_casos_semana_espana():
    ultima_fecha = fecha_actualizacion_espana()
    fecha = datetime.strptime(ultima_fecha, "%Y-%m-%d")

    total = 0
    for i in range(7):
        fecha2 = fecha - timedelta(days=i)
        fecha_semana_antes = fecha2.strftime("%Y-%m-%d")

        df_loc = df_ccaa_casos.loc[df_ccaa_casos['fecha'] == fecha_semana_antes]
        total += int(df_loc['num_casos'].sum())

    return str(round(total / 7, 1))


def fecha_actualizacion_espana():
    actual_day = date.today()
    dias_antes = 0
    day_before = timedelta(days=dias_antes)

    # La primera fecha de la que se tiene datos
    while df_ccaa_casos.loc[df_ccaa_casos['fecha'] == str(actual_day - day_before)].empty:
        dias_antes += 1
        day_before = timedelta(days=dias_antes)

    return str(actual_day-day_before)


def casos_edad(edad):
    df_loc = df_edad.loc[(df_edad['fecha'] == fecha_actualizacion_edad()) & (df_edad['sexo'] == 'ambos') & (df_edad['rango_edad'] == edad)]
    return str(df_loc['casos_confirmados'].values[0])


def muertos_edad(edad):
    df_loc = df_edad.loc[(df_edad['fecha'] == fecha_actualizacion_edad()) & (df_edad['sexo'] == 'ambos') & (df_edad['rango_edad'] == edad)]
    return str(df_loc['fallecidos'].values[0])


def tasa_edad(edad):
    return str(round(int(muertos_edad(edad))*100/int(casos_edad(edad)), 2))


def total_casos_edad():
    df_loc = df_edad.loc[(df_edad['fecha'] == fecha_actualizacion_edad()) & (df_edad['sexo'] == 'ambos')]
    return str(df_loc['casos_confirmados'].sum())


def total_muertos_edad():
    df_loc = df_edad.loc[(df_edad['fecha'] == fecha_actualizacion_edad()) & (df_edad['sexo'] == 'ambos')]
    return str(df_loc['fallecidos'].sum())


def total_tasa_edad():
    return str(round(int(total_muertos_edad())*100/int(total_casos_edad()), 2))


def fecha_actualizacion_edad():
    actual_day = date.today()
    dias_antes = 0
    day_before = timedelta(days=dias_antes)

    # La primera fecha de la que se tiene datos
    while df_edad.loc[df_edad['fecha'] == str(actual_day - day_before)].empty:
        dias_antes += 1
        day_before = timedelta(days=dias_antes)

    return str(actual_day - day_before)


def muertes_totales_espana():
    return str(df_ccaa_muertes.groupby(['CCAA'])['Fallecidos'].sum()['España'])


def muertes_ultimo_dia_espana():
    return str(muertes_ultimo_dia('España'))


def media_muertes_semana_espana():
    return media_muertes_semana('España')


def tasa_letalidad_espana():
    return str(int(muertes_totales('España'))*100/int(casos_acumulados_espana()))


def top_5_casos():
    dict = {}

    for i in range(len(ccaa)):
        dict[ccaa[i]] = int(casos_acumulados(ccaa[i]))

    text=''
    new_dict = sorted(dict.items(), key=lambda x: x[1], reverse=True)

    for i in range(5):
        text += '\t - ' + new_dict[i][0] + ': <b>' + str(new_dict[i][1]) + '</b>. \n'

    return text


def top_5_casos_100():
    dict = {}

    for i in range(len(ccaa)):
        df_loc = df_ccaa_habitantes.loc[df_ccaa_habitantes['ccaa'] == ccaa[i]]
        dict[ccaa[i]] = round((int(casos_acumulados(ccaa[i]))*100000)/df_loc['habitantes'].values[0], 1)

    text=''
    new_dict = sorted(dict.items(), key=lambda x: x[1], reverse=True)

    for i in range(5):
        text += '\t - ' + new_dict[i][0] + ': <b>' + str(new_dict[i][1]) + '</b>. \n'

    return text


def top_5_casos_100_semana():
    dict = {}

    for i in range(len(ccaa)):
        df_loc = df_ccaa_habitantes.loc[df_ccaa_habitantes['ccaa'] == ccaa[i]]
        dict[ccaa[i]] = round((float(media_casos_semana(ccaa[i]))*100000)/df_loc['habitantes'].values[0], 1)

    text=''
    new_dict = sorted(dict.items(), key=lambda x: x[1], reverse=True)

    for i in range(5):
        text += '\t - ' + new_dict[i][0] + ': <b>' + str(new_dict[i][1]) + '</b>. \n'

    return text


def top_5_muertes_100():
    dict = {}

    for i in range(len(ccaa)):
        df_loc = df_ccaa_habitantes.loc[df_ccaa_habitantes['ccaa'] == ccaa[i]]
        dict[ccaa[i]] = round((int(muertes_totales(ccaa[i]))*100000)/df_loc['habitantes'].values[0], 1)

    text=''
    new_dict = sorted(dict.items(), key=lambda x: x[1], reverse=True)

    for i in range(5):
        text += '\t - ' + new_dict[i][0] + ': <b>' + str(new_dict[i][1]) + '</b>. \n'

    return text


def top_5_muertes_100_semana():
    dict = {}

    for i in range(len(ccaa)):
        df_loc = df_ccaa_habitantes.loc[df_ccaa_habitantes['ccaa'] == ccaa[i]]
        dict[ccaa[i]] = round((float(media_muertes_semana(ccaa[i]))*100000)/df_loc['habitantes'].values[0], 1)

    text=''
    new_dict = sorted(dict.items(), key=lambda x: x[1], reverse=True)

    for i in range(5):
        text += '\t - ' + new_dict[i][0] + ': <b>' + str(new_dict[i][1]) + '</b>. \n'

    return text
