# tests/test_regla_r2_correos_buzon.py
# Pruebas de unidad para la regla de negocio R2: desglose de correos por buzón.
#
# LIMITACIÓN: AGENTS.md no existe en la raíz del proyecto, por lo que no hay
# cifras de control definidas. Estas pruebas verifican estructura, consistencia
# y casos límite, no valores esperados específicos.

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.services.regla_r2_correos_buzon import calcular_correos_por_buzon, BUZONES_CONTEXTO


def test_r2_devuelve_estructura_correcta():
    """La regla R2 debe devolver un dict con claves 'buzones', 'resumen' y 'columnas_faltantes'."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_correos_por_buzon(ruta_insumos)

    assert isinstance(resultado, dict), "El resultado debe ser un diccionario"
    assert "buzones" in resultado, "Falta la clave 'buzones'"
    assert "resumen" in resultado, "Falta la clave 'resumen'"
    assert "columnas_faltantes" in resultado, "Falta la clave 'columnas_faltantes'"
    assert isinstance(resultado["buzones"], list), "'buzones' debe ser una lista"


def test_r2_tiene_6_buzones_del_contexto():
    """La regla R2 debe procesar exactamente los 6 buzones definidos en el contexto."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_correos_por_buzon(ruta_insumos)

    assert len(resultado["buzones"]) == len(BUZONES_CONTEXTO), (
        f"Se esperaban {len(BUZONES_CONTEXTO)} buzones, se obtuvieron {len(resultado['buzones'])}"
    )

    buzones_obtenidos = {b["buzon"] for b in resultado["buzones"]}
    assert buzones_obtenidos == set(BUZONES_CONTEXTO), (
        f"Buzones obtenidos no coinciden con los del contexto"
    )


def test_r2_cada_buzon_tiene_claves_requeridas():
    """Cada buzón del resultado R2 debe tener las claves definidas en el contrato."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_correos_por_buzon(ruta_insumos)

    claves_requeridas = {
        "buzon", "archivo", "hoja", "cantidad_atendida",
        "columna_encontrada", "datos_disponibles",
    }

    for buzon in resultado["buzones"]:
        claves_obtenidas = set(buzon.keys())
        faltantes = claves_requeridas - claves_obtenidas
        assert not faltantes, f"Faltan claves en buzón '{buzon.get('buzon')}': {faltantes}"


def test_r2_no_inventa_cantidad_cuando_no_hay_columna():
    """Si no hay columna para un buzón, cantidad_atendida debe ser None."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_correos_por_buzon(ruta_insumos)

    for buzon in resultado["buzones"]:
        if not buzon["datos_disponibles"]:
            assert buzon["cantidad_atendida"] is None, (
                f"Si no hay datos para '{buzon['buzon']}', cantidad_atendida debe ser None"
            )
            assert buzon["archivo"] is None, (
                f"Si no hay datos para '{buzon['buzon']}', archivo debe ser None"
            )
            assert buzon["hoja"] is None, (
                f"Si no hay datos para '{buzon['buzon']}', hoja debe ser None"
            )


def test_r2_ruta_insumos_inexistente():
    """Si la carpeta de insumos no existe, la regla debe devolver estructura vacía sin fallar."""
    resultado = calcular_correos_por_buzon("/ruta/que/no/existe/insumos")

    assert isinstance(resultado, dict)
    assert "buzones" in resultado
    assert "resumen" in resultado
    assert resultado["resumen"]["total_buzones"] == 6
    assert resultado["resumen"]["buzones_encontrados"] == 0


def test_r2_resumen_tiene_claves_esperadas():
    """El resumen de R2 debe tener claves: total_buzones, buzones_encontrados, buzones_no_encontrados."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_correos_por_buzon(ruta_insumos)

    resumen = resultado["resumen"]
    assert "total_buzones" in resumen
    assert "buzones_encontrados" in resumen
    assert "buzones_no_encontrados" in resumen
    assert resumen["total_buzones"] == resumen["buzones_encontrados"] + resumen["buzones_no_encontrados"], (
        "total_buzones debe ser la suma de buzones_encontrados y buzones_no_encontrados"
    )
