import pandas as pd

df_ccaa_casos = pd.read_csv('https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_datos_isciii_nueva_serie.csv',
                            sep=',',
                            usecols=['fecha', 'ccaa', 'num_casos'])
df_ccaa_muertes = pd.read_csv('https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_fallecidos_por_fecha_defuncion_nueva_serie_original.csv',
                              sep=',')
df_ccaa_hospital = pd.read_csv('https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_ingresos_camas_convencionales_uci.csv',
                               sep=',',
                               usecols=['Fecha', 'CCAA', 'Total Pacientes COVID ingresados', '% Camas Ocupadas COVID',
                                        'Total pacientes COVID en UCI', '% Camas Ocupadas UCI COVID',
                                        'Ingresos COVID últimas 24 h', 'Altas COVID últimas 24 h'])
df_edad = pd.read_csv('https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/nacional_covid19_rango_edad.csv',
                      sep=',',
                      usecols=['fecha', 'rango_edad', 'sexo', 'casos_confirmados', 'fallecidos'])
df_ccaa_habitantes = pd.read_csv('./data/habitantes_ccaa.csv', sep=',')