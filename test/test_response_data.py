import pytest
from response_data import *

ccaa = ['Andalucía', 'Aragón', 'Asturias', 'Baleares', 'C. Valenciana', 'Canarias', 'Cantabria', 'Castilla La Mancha',
        'Castilla y León', 'Cataluña', 'Ceuta', 'Extremadura', 'Galicia', 'La Rioja', 'Madrid', 'Melilla', 'Murcia',
        'Navarra', 'País Vasco']

lista_edades = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90 y +']


@pytest.mark.parametrize("fecha,expected", [("2020-12-12", '12-12-2020'), ("0001-07-16", '16-07-1'),
                                        ("2098-05-07", '07-05-2098')])
def test_format_date(fecha, expected):
    assert format_date(fecha) == expected


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_casos_acumulados(current_autonomy):
    assert isinstance(casos_acumulados(current_autonomy), str)


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_incremento_ultimo_dia(current_autonomy):
    assert isinstance(incremento_ultimo_dia(current_autonomy), str)


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_media_casos_semana(current_autonomy):
    assert isinstance(media_casos_semana(current_autonomy), str)


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_fecha_actualizacion(current_autonomy):
    date = fecha_actualizacion(current_autonomy)
    format = "%Y-%m-%d"

    try:
        datetime.strptime(date, format)
    except Exception as e:
        raise e


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_muertes_totales(current_autonomy):
    assert isinstance(muertes_totales(current_autonomy), str)


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_muertes_ultimo_dia(current_autonomy):
    assert isinstance(muertes_ultimo_dia(current_autonomy), str)


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_media_muertes_semana(current_autonomy):
    assert isinstance(media_muertes_semana(current_autonomy), str)


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_tasa_letalidad(current_autonomy):
    assert isinstance(tasa_letalidad(current_autonomy), str)


def test_fecha_actualizacion_muertes():
    assert isinstance(fecha_actualizacion_muertes(), str)


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_pacientes_ingresados(current_autonomy):
    if (current_autonomy == 'C. Valenciana'):
        current_autonomy = 'C Valenciana'
    assert isinstance(pacientes_ingresados(current_autonomy), str)


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_porcentaje_camas_ocupadas(current_autonomy):
    if (current_autonomy == 'C. Valenciana'):
        current_autonomy = 'C Valenciana'
    assert isinstance(porcentaje_camas_ocupadas(current_autonomy), str)


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_pacientes_ingresados_uci(current_autonomy):
    if (current_autonomy == 'C. Valenciana'):
        current_autonomy = 'C Valenciana'
    assert isinstance(pacientes_ingresados_uci(current_autonomy), str)


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_porcentaje_camas_uci_ocupadas(current_autonomy):
    if (current_autonomy == 'C. Valenciana'):
        current_autonomy = 'C Valenciana'
    assert isinstance(porcentaje_camas_uci_ocupadas(current_autonomy), str)


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_ingresados_ultimo_dia(current_autonomy):
    if (current_autonomy == 'C. Valenciana'):
        current_autonomy = 'C Valenciana'
    assert isinstance(ingresados_ultimo_dia(current_autonomy), str)


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_altas_ultimo_dia(current_autonomy):
    if (current_autonomy == 'C. Valenciana'):
        current_autonomy = 'C Valenciana'
    assert isinstance(altas_ultimo_dia(current_autonomy), str)


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_fecha_actualizacion_hospital(current_autonomy):
    if (current_autonomy == 'C. Valenciana'):
        current_autonomy = 'C Valenciana'
    date = fecha_actualizacion_hospital(current_autonomy)
    format = "%Y-%m-%d"

    try:
        assert isinstance(date, str)
        datetime.strptime(date, format)
    except Exception as e:
        raise e


def test_casos_acumulados_espana():
    assert isinstance(casos_acumulados_espana(), str)


def test_incremento_ultimo_dia_espana():
    assert isinstance(incremento_ultimo_dia_espana(), str)


def test_media_casos_semana_espana():
    assert isinstance(media_casos_semana_espana(), str)


def test_fecha_actualizacion_espana():
    date = fecha_actualizacion_espana()
    format = "%Y-%m-%d"

    try:
        assert isinstance(date, str)
        datetime.strptime(date, format)
    except Exception as e:
        raise e


@pytest.mark.parametrize("edad", lista_edades)
def test_casos_edad(edad):
    assert isinstance(casos_edad(edad), str)


@pytest.mark.parametrize("edad", lista_edades)
def test_muertos_edad(edad):
    assert isinstance(muertos_edad(edad), str)


@pytest.mark.parametrize("edad", lista_edades)
def test_tasa_edad(edad):
    assert isinstance(tasa_edad(edad), str)


def test_total_casos_edad():
    assert isinstance(total_casos_edad(), str)


def test_total_muertos_edad():
    assert isinstance(total_muertos_edad(), str)


def test_total_tasa_edad():
    assert isinstance(total_tasa_edad(), str)


def test_fecha_actualizacion_edad():
    date = fecha_actualizacion_edad()
    format = "%Y-%m-%d"

    try:
        assert isinstance(date, str)
        datetime.strptime(date, format)
    except Exception as e:
        raise e


def test_muertes_totales_espana():
    assert isinstance(muertes_totales_espana(), str)


def test_muertes_ultimo_dia_espana():
    assert isinstance(muertes_ultimo_dia_espana(), str)


def test_media_muertes_semana_espana():
    assert isinstance(media_muertes_semana_espana(), str)


def test_tasa_letalidad_espana():
    assert isinstance(tasa_letalidad_espana(), str)


def test_top_5_casos():
    assert isinstance(top_5_casos(), str)


def test_top_5_casos_100():
    assert isinstance(top_5_casos_100(), str)


def test_top_5_casos_100_semana():
    assert isinstance(top_5_casos_100_semana(), str)


def test_top_5_muertes_100():
    assert isinstance(top_5_muertes_100(), str)


def test_top_5_muertes_100_semana():
    assert isinstance(top_5_muertes_100_semana(), str)