import matplotlib.pyplot as plt
from util import *
from response_data import *

inicio_mes = ['2020-01-01', '2020-02-01', '2020-03-01', '2020-04-01', '2020-05-01', '2020-06-01', '2020-07-01',
              '2020-08-01', '2020-09-01', '2020-10-01', '2020-11-01', '2020-12-01']

ccaa = ['Andalucía', 'Aragón', 'Asturias', 'Baleares', 'C. Valenciana', 'Canarias', 'Cantabria', 'Castilla La Mancha',
        'Castilla y León', 'Cataluña', 'Ceuta', 'Extremadura', 'Galicia', 'La Rioja', 'Madrid', 'Melilla', 'Murcia',
        'Navarra', 'País Vasco']

def grafica_acumulado(current_autonomy):
    df_casos_ccaa = df_ccaa_casos.loc[df_ccaa_casos['ccaa'] == current_autonomy]
    df_casos_ccaa['casos_acumulados'] = df_casos_ccaa['num_casos'].cumsum()
    df_loc = df_casos_ccaa.loc[:, ['fecha', 'casos_acumulados']]
    df_loc.set_index("fecha", inplace=True)

    autonomy_lower = normalize(current_autonomy).lower()

    fig, ax = plt.subplots(figsize=(12, 6))
    x = df_loc.index.get_level_values('fecha')

    plt.bar(x, df_loc['casos_acumulados'], alpha=0.5, width=0.5, label=('Nº Casos'))

    ax.set_xticks(inicio_mes)
    ax.set_xlim('2020-03-01', x[-1])
    ax.figure.autofmt_xdate()

    plt.title('Casos acumulados en {}'.format(current_autonomy), fontsize=26)
    ax.set_ylabel('Nº Casos', fontsize=15)
    plt.savefig('./img_graficas/acumulado_{}.png'.format(autonomy_lower))
    plt.close()


def grafica_incremento(current_autonomy):
    df_casos_ccaa = df_ccaa_casos.loc[df_ccaa_casos['ccaa'] == current_autonomy]
    df_casos_ccaa.set_index("fecha", inplace=True)

    autonomy_lower = normalize(current_autonomy).lower()

    fig, ax = plt.subplots(figsize=(12, 6))
    x = df_casos_ccaa.index.get_level_values('fecha')

    plt.bar(x, df_casos_ccaa['num_casos'], alpha=0.5, width=0.5, label=('Incremento diario'))
    plt.plot(x, df_casos_ccaa['num_casos'], color='red')

    ax.set_xticks(inicio_mes)
    ax.set_xlim('2020-03-01', x[-1])
    ax.figure.autofmt_xdate()

    plt.title('Incremento de casos en {}'.format(current_autonomy), fontsize=26)
    ax.set_ylabel('Nº Casos', fontsize=15)
    plt.savefig('./img_graficas/incremento_{}.png'.format(autonomy_lower))
    plt.close()


def grafica_muertes(current_autonomy):
    df_muertes_ccaa = df_ccaa_muertes.loc[df_ccaa_muertes['CCAA'] == current_autonomy]
    df_muertes_ccaa.set_index("Fecha", inplace=True)

    autonomy_lower = normalize(current_autonomy).lower()

    fig, ax = plt.subplots(figsize=(12, 6))
    x = df_muertes_ccaa.index.get_level_values('Fecha')

    plt.bar(x, df_muertes_ccaa['Fallecidos'], alpha=0.5, width=0.7, label=('Fallecimientos diarios'), color='red')
    plt.plot(x, df_muertes_ccaa['Fallecidos'], color='red')

    ax.set_xticks(inicio_mes)
    ax.set_xlim('2020-03-01', x[-1])
    ax.figure.autofmt_xdate()

    plt.title('Evolución de fallecidos en {}'.format(current_autonomy), fontsize=26)
    ax.set_ylabel('Fallecidos', fontsize=15)
    plt.savefig('./img_graficas/fallecidos_{}.png'.format(autonomy_lower))
    plt.close()


def grafica_hospitales(current_autonomy):
    df_hospitales_ccaa = df_ccaa_hospital.loc[df_ccaa_hospital['CCAA'] == current_autonomy].fillna('0')
    df_hospitales_ccaa['% Camas Ocupadas UCI COVID'] = df_hospitales_ccaa['% Camas Ocupadas UCI COVID']
    df_hospitales_ccaa['% Camas Ocupadas COVID'] = df_hospitales_ccaa['% Camas Ocupadas COVID'].str.replace(r'%$', '')
    df_hospitales_ccaa['% Camas Ocupadas UCI COVID'] = df_hospitales_ccaa['% Camas Ocupadas UCI COVID'].str.replace(r'%$', '')

    autonomy_lower = normalize(current_autonomy).lower()

    df_hospitales_ccaa.set_index("Fecha", inplace=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8))
    x = df_hospitales_ccaa.index.get_level_values('Fecha')

    fig.suptitle('Evolución ocupación camas en {}'.format(current_autonomy), fontsize=26)

    ax1.plot(x, df_hospitales_ccaa['% Camas Ocupadas COVID'], color='blue')
    ax1.set_ylabel('% camas ocupadas', fontsize=15)
    ax1.set_xticks(inicio_mes)
    ax1.set_xlim('2020-08-19', x[-1])
    ax1.figure.autofmt_xdate()

    ax2.plot(x, df_hospitales_ccaa['% Camas Ocupadas UCI COVID'], color='red')
    ax2.set_ylabel('% camas UCI ocupadas', fontsize=15)
    ax2.set_xticks(inicio_mes)
    ax2.set_xlim('2020-08-19', x[-1])
    ax2.figure.autofmt_xdate()

    plt.savefig('./img_graficas/hospital_{}.png'.format(autonomy_lower))
    plt.close()


def grafica_incremento_espana():
    df_casos_fecha = df_ccaa_casos.groupby('fecha')['num_casos'].sum().reset_index()
    df_casos_fecha.set_index("fecha", inplace=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    x = df_casos_fecha.index.get_level_values('fecha')

    plt.bar(x, df_casos_fecha['num_casos'], alpha=0.5, width=0.5)
    plt.plot(x, df_casos_fecha['num_casos'], color='red')

    ax.set_xticks(inicio_mes)
    ax.set_xlim('2020-03-01', x[-1])
    ax.figure.autofmt_xdate()

    plt.title('Incremento de casos en España', fontsize=26)
    ax.set_ylabel('Nº Casos', fontsize=15)
    plt.savefig('./img_graficas/incremento_espana.png')
    plt.close()


def grafica_acumulado_espana():
    df_casos_fecha = df_ccaa_casos.groupby('fecha')['num_casos'].sum().reset_index()
    df_casos_fecha['casos_acumulados'] = df_casos_fecha['num_casos'].cumsum()
    df_loc = df_casos_fecha.loc[:, ['fecha', 'casos_acumulados']]
    df_loc.set_index("fecha", inplace=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    x = df_loc.index.get_level_values('fecha')

    plt.bar(x, df_loc['casos_acumulados'], alpha=0.5, width=0.5)
    plt.plot(x, df_loc['casos_acumulados'], color='red')

    ax.set_xticks(inicio_mes)
    ax.set_xlim('2020-03-01', x[-1])
    ax.figure.autofmt_xdate()

    plt.title('Casos acumulados en España', fontsize=26)
    ax.set_ylabel('Nº Casos', fontsize=15)
    plt.savefig('./img_graficas/acumulado_espana.png')
    plt.close()


def grafica_muertes_espana():
    df_muertes = df_ccaa_muertes.loc[df_ccaa_muertes['CCAA'] == 'España']
    df_muertes.set_index("Fecha", inplace=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    x = df_muertes.index.get_level_values('Fecha')

    plt.bar(x, df_muertes['Fallecidos'], alpha=0.5, width=0.7, label=('Fallecimientos diarios'), color='red')
    plt.plot(x, df_muertes['Fallecidos'], color='red')

    ax.set_xticks(inicio_mes)
    ax.set_xlim('2020-03-01', x[-1])
    ax.figure.autofmt_xdate()

    plt.title('Evolución de fallecidos en España', fontsize=26)
    ax.set_ylabel('Fallecidos', fontsize=15)
    plt.savefig('./img_graficas/fallecidos_espana.png')
    plt.close()


def grafica_casos_comunidad():
    dict = {}

    for i in range(len(ccaa)):
        dict[ccaa[i]] = int(casos_acumulados(ccaa[i]))

    new_dict = sorted(dict.items(), key=lambda x: x[1], reverse=True)
    df = pd.DataFrame(new_dict, columns=['ccaa', 'n_casos'])
    df.set_index("ccaa", inplace=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    x = df.index.get_level_values('ccaa')

    plt.barh(x, df['n_casos'], alpha=0.5, height=0.8)

    ax.figure.autofmt_xdate()

    plt.title('Casos por comunidad', fontsize=26)
    plt.gca().invert_yaxis()

    for index, value in enumerate(df['n_casos']):
        plt.text(value, index, str(value))

    plt.savefig('./img_graficas/casos_comunidad.png')
    plt.close()


def grafica_casos_100():
    dict = {}

    for i in range(len(ccaa)):
        df_loc = df_ccaa_habitantes.loc[df_ccaa_habitantes['ccaa'] == ccaa[i]]
        dict[ccaa[i]] = round((int(casos_acumulados(ccaa[i])) * 100000) / df_loc['habitantes'].values[0], 1)

    new_dict = sorted(dict.items(), key=lambda x: x[1], reverse=True)
    df = pd.DataFrame(new_dict, columns=['ccaa', 'n_casos'])
    df.set_index("ccaa", inplace=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    x = df.index.get_level_values('ccaa')

    plt.barh(x, df['n_casos'], alpha=0.5, height=0.8)

    ax.figure.autofmt_xdate()

    plt.title('Casos por cada 100mil habitantes', fontsize=26)
    plt.gca().invert_yaxis()

    for index, value in enumerate(df['n_casos']):
        plt.text(value, index, str(value))

    plt.savefig('./img_graficas/casos_100.png')
    plt.close()


def grafica_casos_100_semana():
    dict = {}

    for i in range(len(ccaa)):
        df_loc = df_ccaa_habitantes.loc[df_ccaa_habitantes['ccaa'] == ccaa[i]]
        dict[ccaa[i]] = round((float(media_casos_semana(ccaa[i])) * 100000) / df_loc['habitantes'].values[0], 1)

    new_dict = sorted(dict.items(), key=lambda x: x[1], reverse=True)
    df = pd.DataFrame(new_dict, columns=['ccaa', 'n_casos'])
    df.set_index("ccaa", inplace=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    x = df.index.get_level_values('ccaa')

    plt.barh(x, df['n_casos'], alpha=0.5, height=0.8)

    ax.figure.autofmt_xdate()

    plt.title('Casos última semana por cada 100mil habitantes', fontsize=26)
    plt.gca().invert_yaxis()

    for index, value in enumerate(df['n_casos']):
        plt.text(value, index, str(value))

    plt.savefig('./img_graficas/casos_100_semana.png')
    plt.close()


def grafica_muertes_100():
    dict = {}

    for i in range(len(ccaa)):
        df_loc = df_ccaa_habitantes.loc[df_ccaa_habitantes['ccaa'] == ccaa[i]]
        dict[ccaa[i]] = round((int(muertes_totales(ccaa[i])) * 100000) / df_loc['habitantes'].values[0], 1)

    new_dict = sorted(dict.items(), key=lambda x: x[1], reverse=True)
    df = pd.DataFrame(new_dict, columns=['ccaa', 'n_muertes'])
    df.set_index("ccaa", inplace=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    x = df.index.get_level_values('ccaa')

    plt.barh(x, df['n_muertes'], alpha=0.5, height=0.8)

    ax.figure.autofmt_xdate()

    plt.title('Muertes por cada 100mil habitantes', fontsize=26)
    plt.gca().invert_yaxis()

    for index, value in enumerate(df['n_muertes']):
        plt.text(value, index, str(value))

    plt.savefig('./img_graficas/muertes_100.png')
    plt.close()


def grafica_muertes_100_semana():
    dict = {}

    for i in range(len(ccaa)):
        df_loc = df_ccaa_habitantes.loc[df_ccaa_habitantes['ccaa'] == ccaa[i]]
        dict[ccaa[i]] = round((float(media_muertes_semana(ccaa[i])) * 100000) / df_loc['habitantes'].values[0], 1)

    new_dict = sorted(dict.items(), key=lambda x: x[1], reverse=True)
    df = pd.DataFrame(new_dict, columns=['ccaa', 'n_muertes'])
    df.set_index("ccaa", inplace=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    x = df.index.get_level_values('ccaa')

    plt.barh(x, df['n_muertes'], alpha=0.5, height=0.8)

    ax.figure.autofmt_xdate()

    plt.title('Muertes última semana por cada 100mil habitantes', fontsize=26)
    plt.gca().invert_yaxis()

    for index, value in enumerate(df['n_muertes']):
        plt.text(value, index, str(value))

    plt.savefig('./img_graficas/muertes_100_semana.png')
    plt.close()


def grafica_edades():
    df_mujeres = df_edad.loc[(df_edad['fecha'] == fecha_actualizacion_edad()) & (df_edad['sexo'] == 'mujeres') & (df_edad['rango_edad'] != 'Total')]
    df_hombres = df_edad.loc[(df_edad['fecha'] == fecha_actualizacion_edad()) & (df_edad['sexo'] == 'hombres') & (df_edad['rango_edad'] != 'Total')]
    df_mujeres.set_index("rango_edad", inplace=True)
    df_hombres.set_index("rango_edad", inplace=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
    x = df_mujeres.index.get_level_values('rango_edad')

    fig.suptitle('Casos por edad', fontsize=26)

    ax1.bar(x, df_mujeres['casos_confirmados'], alpha=0.5, width=0.5, label=('Casos mujeres'), color='blue')
    ax1.bar(x, df_mujeres['fallecidos'], alpha=0.5, width=0.5, label=('Mujeres fallecidas'), color='green')
    ax1.set_title('Mujeres')
    ax1.set_ylabel('Nº Casos', fontsize=15)
    ax1.legend()

    ax2.bar(x, df_hombres['casos_confirmados'], alpha=0.5, width=0.5, label=('Casos hombres'), color='red')
    ax2.bar(x, df_hombres['fallecidos'], alpha=0.5, width=0.5, label=('Hombres fallecidos'), color='yellow')
    ax2.set_title('Hombres')
    ax2.set_ylabel('Nº Casos', fontsize=15)
    ax2.legend()

    plt.savefig('./img_graficas/casos_edad_espana.png')
    plt.close()