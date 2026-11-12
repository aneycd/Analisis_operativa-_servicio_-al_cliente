# tests/test_regla_r4_whatsapp_subcanal.py
# Pruebas de unidad para la regla de negocio R4: desglose WhatsApp por subcanal.
#
# LIMITACIÓN: AGENTS.md no existe en la raíz del proyecto, por lo que no hay
# cifras de control definidas. Estas pruebas verifican estructura, consistencia
# y casos límite, no valores esperados específicos.

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.services.regla_r4_whatsapp_subcanal import calcular_whatsapp_por_subcanal


def test_r4_devuelve_estructura_correcta():
    """La regla R4 debe devolver un dict con claves 'subcanales' y 'resumen'."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_whatsapp_por_subcanal(ruta_insumos)

    assert isinstance(resultado, dict), "El resultado debe ser un diccionario"
    assert "subcanales" in resultado, "Falta la clave 'subcanales'"
    assert "resumen" in resultado, "Falta la clave 'resumen'"
    assert isinstance(resultado["subcanales"], list), "'subcanales' debe ser una lista"


def test_r4_tiene_2_subcanales():
    """La regla R4 debe procesar exactamente 2 subcanales: WhatsApp y Llamadas."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_whatsapp_por_subcanal(ruta_insumos)

    subcanales_esperados = {"WhatsApp", "Llamadas"}
    subcanales_obtenidos = {s["subcanal"] for s in resultado["subcanales"]}

    assert subcanales_obtenidos == subcanales_esperados, (
        f"Se esperaban subcanales {subcanales_esperados}, se obtuvieron {subcanales_obtenidos}"
    )


def test_r4_cada_subcanal_tiene_claves_requeridas():
    """Cada subcanal del resultado R4 debe tener las claves definidas en el contrato."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_whatsapp_por_subcanal(ruta_insumos)

    claves_requeridas = {
        "subcanal", "archivo", "hoja", "filas_procesadas",
        "atendidas", "aht", "tr", "datos_disponibles",
        "columnas_faltantes", "se_pudo_filtrar_por_subcanal", "columna_canal_usada",
    }

    for sub in resultado["subcanales"]:
        claves_obtenidas = set(sub.keys())
        faltantes = claves_requeridas - claves_obtenidas
        assert not faltantes, f"Faltan claves en subcanal '{sub.get('subcanal')}': {faltantes}"


def test_r4_no_inventa_datos_cuando_no_se_puede_filtrar():
    """Si no se puede filtrar por subcanal, los valores deben ser None o 0, no inventados."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_whatsapp_por_subcanal(ruta_insumos)

    for sub in resultado["subcanales"]:
        if not sub["datos_disponibles"]:
            assert sub["atendidas"] is None, (
                f"Si no hay datos para '{sub['subcanal']}', atendidas debe ser None"
            )
            assert sub["aht"] is None, (
                f"Si no hay datos para '{sub['subcanal']}', aht debe ser None"
            )
            assert sub["tr"] is None, (
                f"Si no hay datos para '{sub['subcanal']}', tr debe ser None"
            )


def test_r4_ruta_insumos_inexistente():
    """Si la carpeta de insumos no existe, la regla no debe fallar."""
    resultado = calcular_whatsapp_por_subcanal("/ruta/que/no/existe/insumos")

    assert isinstance(resultado, dict)
    assert "subcanales" in resultado
    assert "resumen" in resultado
    assert resultado["resumen"]["total_subcanales"] == 2


def test_r4_resumen_tiene_claves_esperadas():
    """El resumen de R4 debe tener claves: total_subcanales, subcanales_con_datos, subcanales_sin_datos."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_whatsapp_por_subcanal(ruta_insumos)

    resumen = resultado["resumen"]
    assert "total_subcanales" in resumen
    assert "subcanales_con_datos" in resumen
    assert "subcanales_sin_datos" in resumen
    assert resumen["total_subcanales"] == resumen["subcanales_con_datos"] + resumen["subcanales_sin_datos"], (
        "total_subcanales debe ser la suma de subcanales_con_datos y subcanales_sin_datos"
    )
