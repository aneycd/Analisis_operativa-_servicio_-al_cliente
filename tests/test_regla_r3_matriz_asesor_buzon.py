# tests/test_regla_r3_matriz_asesor_buzon.py
# Pruebas de unidad para la regla de negocio R3: matriz Asesor vs Buzón de correos.
#
# LIMITACIÓN: AGENTS.md no existe en la raíz del proyecto, por lo que no hay
# cifras de control definidas. Estas pruebas verifican estructura, consistencia
# y casos límite, no valores esperados específicos.

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.services.regla_r3_matriz_asesor_buzon import calcular_matriz_asesor_buzon, BUZONES_CONTEXTO


def test_r3_devuelve_estructura_correcta():
    """La regla R3 debe devolver un dict con claves esperadas."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_matriz_asesor_buzon(ruta_insumos)

    assert isinstance(resultado, dict), "El resultado debe ser un diccionario"
    claves_esperadas = {
        "matriz", "asesores", "buzones", "buzones_con_columna",
        "buzones_sin_columna", "archivo_usado", "hoja_usada", "datos_disponibles",
    }
    for clave in claves_esperadas:
        assert clave in resultado, f"Falta la clave '{clave}'"


def test_r3_buzones_son_los_del_contexto():
    """La lista de buzones en R3 debe coincidir con los 6 buzones del contexto."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_matriz_asesor_buzon(ruta_insumos)

    assert resultado["buzones"] == list(BUZONES_CONTEXTO), (
        "Los buzones de R3 deben coincidir con BUZONES_CONTEXTO"
    )


def test_r3_matriz_es_dict_de_dicts():
    """La matriz de R3 debe ser un diccionario donde cada valor es un diccionario."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_matriz_asesor_buzon(ruta_insumos)

    assert isinstance(resultado["matriz"], dict), "'matriz' debe ser un diccionario"
    for asesor, fila in resultado["matriz"].items():
        assert isinstance(fila, dict), f"La fila del asesor '{asesor}' debe ser un diccionario"


def test_r3_sin_datos_reporta_honestamente():
    """Si no hay columnas de buzón, datos_disponible debe ser False y no inventar valores."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_matriz_asesor_buzon(ruta_insumos)

    # En los insumos actuales no hay columnas de buzón del contexto
    if not resultado["datos_disponibles"]:
        assert resultado["archivo_usado"] is None, (
            "Si no hay datos, archivo_usado debe ser None"
        )
        assert resultado["hoja_usada"] is None, (
            "Si no hay datos, hoja_usada debe ser None"
        )
        assert len(resultado["buzones_sin_columna"]) == len(BUZONES_CONTEXTO), (
            "Todos los buzones deben estar en buzones_sin_columna si no hay datos"
        )


def test_r3_ruta_insumos_inexistente():
    """Si la carpeta de insumos no existe, la regla no debe fallar."""
    resultado = calcular_matriz_asesor_buzon("/ruta/que/no/existe/insumos")

    assert isinstance(resultado, dict)
    assert resultado["datos_disponibles"] is False
    assert resultado["archivo_usado"] is None
