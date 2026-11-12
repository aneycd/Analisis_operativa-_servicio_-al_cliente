# tests/test_regla_r5_whatsapp_asesor.py
# Pruebas de unidad para la regla de negocio R5: desempeño por asesor de WhatsApp.
#
# LIMITACIÓN: AGENTS.md no existe en la raíz del proyecto, por lo que no hay
# cifras de control definidas. Estas pruebas verifican estructura, consistencia
# y casos límite, no valores esperados específicos.

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.services.regla_r5_whatsapp_asesor import calcular_desempeño_asesor_whatsapp


def test_r5_devuelve_estructura_correcta():
    """La regla R5 debe devolver un dict con claves 'asesores', 'resumen', 'archivo_usado', 'hoja_usada', 'nota_limitacion'."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_desempeño_asesor_whatsapp(ruta_insumos)

    assert isinstance(resultado, dict), "El resultado debe ser un diccionario"
    assert "asesores" in resultado, "Falta la clave 'asesores'"
    assert "resumen" in resultado, "Falta la clave 'resumen'"
    assert "archivo_usado" in resultado, "Falta la clave 'archivo_usado'"
    assert "hoja_usada" in resultado, "Falta la clave 'hoja_usada'"
    assert "nota_limitacion" in resultado, "Falta la clave 'nota_limitacion'"
    assert isinstance(resultado["asesores"], list), "'asesores' debe ser una lista"


def test_r5_cada_asesor_tiene_claves_requeridas():
    """Cada asesor del resultado R5 debe tener las claves definidas en el contrato."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_desempeño_asesor_whatsapp(ruta_insumos)

    claves_requeridas = {
        "asesor", "cantidad_whatsapp", "cantidad_llamadas",
        "tiempo_ocupacion", "aht", "total_gestiones",
        "filas_procesadas", "datos_disponibles", "columnas_faltantes",
    }

    for asesor in resultado["asesores"]:
        claves_obtenidas = set(asesor.keys())
        faltantes = claves_requeridas - claves_obtenidas
        assert not faltantes, f"Faltan claves en asesor '{asesor.get('asesor')}': {faltantes}"


def test_r5_no_inventa_cantidad_whatsapp_ni_llamadas():
    """Como no hay columna que distinga subcanal, cantidad_whatsapp y cantidad_llamadas deben ser None."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_desempeño_asesor_whatsapp(ruta_insumos)

    for asesor in resultado["asesores"]:
        assert asesor["cantidad_whatsapp"] is None, (
            f"cantidad_whatsapp de '{asesor['asesor']}' debe ser None (no hay columna de subcanal)"
        )
        assert asesor["cantidad_llamadas"] is None, (
            f"cantidad_llamadas de '{asesor['asesor']}' debe ser None (no hay columna de subcanal)"
        )


def test_r5_total_gestiones_es_suma_positiva_o_none():
    """El total de gestiones debe ser un número positivo o None, nunca negativo."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_desempeño_asesor_whatsapp(ruta_insumos)

    for asesor in resultado["asesores"]:
        if asesor["total_gestiones"] is not None:
            assert asesor["total_gestiones"] >= 0, (
                f"total_gestiones de '{asesor['asesor']}' no debe ser negativo"
            )


def test_r5_ruta_insumos_inexistente():
    """Si la carpeta de insumos no existe, la regla no debe fallar."""
    resultado = calcular_desempeño_asesor_whatsapp("/ruta/que/no/existe/insumos")

    assert isinstance(resultado, dict)
    assert "asesores" in resultado
    assert "resumen" in resultado
    assert resultado["resumen"]["total_asesores"] == 0


def test_r5_resumen_tiene_claves_esperadas():
    """El resumen de R5 debe tener claves: total_asesores, total_gestiones_global, asesores_con_datos."""
    ruta_insumos = os.path.join(ROOT_DIR, "insumos")
    resultado = calcular_desempeño_asesor_whatsapp(ruta_insumos)

    resumen = resultado["resumen"]
    assert "total_asesores" in resumen
    assert "total_gestiones_global" in resumen
    assert "asesores_con_datos" in resumen
