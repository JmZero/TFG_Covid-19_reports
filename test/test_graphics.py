import pytest
from graphics import *

ccaa = ['Andalucía', 'Aragón', 'Asturias', 'Baleares', 'C. Valenciana', 'Canarias', 'Cantabria', 'Castilla La Mancha',
        'Castilla y León', 'Cataluña', 'Ceuta', 'Extremadura', 'Galicia', 'La Rioja', 'Madrid', 'Melilla', 'Murcia',
        'Navarra', 'País Vasco']

@pytest.mark.parametrize("current_autonomy", ccaa)
def test_grafica_acumulado(current_autonomy):
    try:
        grafica_acumulado(current_autonomy)
    except Exception as e:
        raise e


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_grafica_incremento(current_autonomy):
    try:
        grafica_incremento(current_autonomy)
    except Exception as e:
        raise e


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_grafica_muertes(current_autonomy):
    try:
        grafica_muertes(current_autonomy)
    except Exception as e:
        raise e


@pytest.mark.parametrize("current_autonomy", ccaa)
def test_grafica_hospitales(current_autonomy):
    try:
        grafica_hospitales(current_autonomy)
    except Exception as e:
        raise e


def test_grafica_incremento_espana():
    try:
        grafica_incremento_espana()
    except Exception as e:
        raise e


def test_grafica_acumulado_espana():
    try:
        grafica_acumulado_espana()
    except Exception as e:
        raise e


def test_grafica_muertes_espana():
    try:
        grafica_muertes_espana()
    except Exception as e:
        raise e


def test_grafica_casos_comunidad():
    try:
        grafica_casos_comunidad()
    except Exception as e:
        raise e


def test_grafica_casos_100():
    try:
        grafica_casos_100()
    except Exception as e:
        raise e


def test_grafica_casos_100_semana():
    try:
        grafica_casos_100_semana()
    except Exception as e:
        raise e


def test_grafica_muertes_100():
    try:
        grafica_muertes_100()
    except Exception as e:
        raise e


def test_grafica_muertes_100_semana():
    try:
        grafica_muertes_100_semana()
    except Exception as e:
        raise e


def test_grafica_edades():
    try:
        grafica_edades()
    except Exception as e:
        raise e