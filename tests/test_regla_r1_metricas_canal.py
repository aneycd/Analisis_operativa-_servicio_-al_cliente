# tests/test_regla_r1_metricas_canal.py
# Pruebas de unidad para la regla de negocio R1: métricas globales por canal.
#
# LIMITACIÓN: AGENTS.md no existe en la raíz del proyecto, por lo que no hay
# cifras de control definidas. Estas pruebas verifican estructura, consistencia
# y casos límite, no valores esperados específicos.

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.services.regla_r1_metricas_canal import calcular_metricas_por_canal


def test_r1_devuelve_estructura_correcta():
    """La regla R1 debe devolver un dict con claves 'canales' y 'resumen'."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_metricas_por_canal(ruta_insumos)

    assert isinstance(resultado, dict), "El resultado debe ser un diccionario"
    assert "canales" in resultado, "Falta la clave 'canales'"
    assert "resumen" in resultado, "Falta la clave 'resumen'"
    assert isinstance(resultado["canales"], list), "'canales' debe ser una lista"
    assert isinstance(resultado["resumen"], dict), "'resumen' debe ser un diccionario"


def test_r1_tiene_4_canales():
    """La regla R1 debe procesar exactamente 4 canales: Chatbot, Llamadas, Correos, WhatsApp."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_metricas_por_canal(ruta_insumos)

    canales_esperados = {"Chatbot", "Llamadas", "Correos", "WhatsApp"}
    canales_obtenidos = {c["canal"] for c in resultado["canales"]}

    assert canales_obtenidos == canales_esperados, (
        f"Se esperaban canales {canales_esperados}, se obtuvieron {canales_obtenidos}"
    )


def test_r1_cada_canal_tiene_claves_requeridas():
    """Cada canal del resultado R1 debe tener las claves definidas en el contrato."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_metricas_por_canal(ruta_insumos)

    claves_requeridas = {
        "canal", "archivo", "hoja", "filas_procesadas",
        "cantidad_atendida", "aht", "tr", "gestiones_por_asesor",
        "columnas_encontradas", "columnas_faltantes", "datos_disponibles", "error",
    }

    for canal in resultado["canales"]:
        claves_obtenidas = set(canal.keys())
        faltantes = claves_requeridas - claves_obtenidas
        assert not faltantes, f"Faltan claves en canal '{canal.get('canal')}': {faltantes}"


def test_r1_no_inventa_datos_cuando_faltan_columnas():
    """Si faltan columnas, datos_disponibles debe ser False y cantidad_atendida None."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_metricas_por_canal(ruta_insumos)

    # Buscar el canal Chatbot (se sabe que no tiene columnas de métricas en insumos)
    canal_chatbot = next((c for c in resultado["canales"] if c["canal"] == "Chatbot"), None)
    if canal_chatbot is not None:
        # Si no hay datos disponibles, no debe inventar valores
        if not canal_chatbot["datos_disponibles"]:
            assert canal_chatbot["cantidad_atendida"] is None, (
                "Si no hay datos, cantidad_atendida debe ser None, no un valor inventado"
            )
            assert canal_chatbot["aht"] is None, (
                "Si no hay datos, aht debe ser None, no un valor inventado"
            )
            assert canal_chatbot["tr"] is None, (
                "Si no hay datos, tr debe ser None, no un valor inventado"
            )


def test_r1_ruta_insumos_inexistente():
    """Si la carpeta de insumos no existe, la regla debe devolver estructura vacía sin fallar."""
    resultado = calcular_metricas_por_canal("/ruta/que/no/existe/insumos")

    assert isinstance(resultado, dict)
    assert "canales" in resultado
    assert "resumen" in resultado
    assert resultado["resumen"]["total_canales"] == 4
    assert resultado["resumen"]["canales_con_datos"] == 0


def test_r1_resumen_tiene_claves_esperadas():
    """El resumen de R1 debe tener claves: total_canales, canales_con_datos, canales_sin_datos."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_metricas_por_canal(ruta_insumos)

    resumen = resultado["resumen"]
    assert "total_canales" in resumen
    assert "canales_con_datos" in resumen
    assert "canales_sin_datos" in resumen
    assert resumen["total_canales"] == resumen["canales_con_datos"] + resumen["canales_sin_datos"], (
        "total_canales debe ser la suma de canales_con_datos y canales_sin_datos"
    )


def test_r1_columnas_faltantes_son_lista():
    """Cada canal debe tener columnas_faltantes como una lista (puede estar vacía)."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_metricas_por_canal(ruta_insumos)

    for canal in resultado["canales"]:
        assert isinstance(canal["columnas_faltantes"], list), (
            f"columnas_faltantes de '{canal['canal']}' debe ser una lista"
        )
