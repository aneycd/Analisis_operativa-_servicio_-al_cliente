"""Regla de negocio R1: métricas globales por canal.

Calcula, para cada canal del Contact Center, las métricas operativas:
- Cantidad Atendida
- AHT (Average Handling Time)
- TR (Tasa de Respuesta / Tasa de Servicio)
- Gestiones por Asesor

Los datos de entrada vienen de los archivos Excel de `insumos/`.
Esta función solo lee; nunca escribe dentro de `insumos/`.

IMPORTANTE: no existe AGENTS.md que defina el mapeo exacto
canal <-> archivo <-> columnas. Esta regla usa las columnas
observadas en los archivos reales y reporta explícitamente qué
datos faltan para cada canal, sin inventar valores.
"""

from __future__ import annotations

import os
from typing import Any

import openpyxl

from app.services.lectura_insumos import _fila_tiene_contenido, _primer_encabezado_valido


def _obtener_valor(fila: dict[str, Any], nombre_columna: str) -> Any:
    """Busca el valor de una columna en una fila, tolerando espacios y mayúsculas."""
    nombre_normalizado = nombre_columna.strip().lower()
    for clave, valor in fila.items():
        if clave is not None and str(clave).strip().lower() == nombre_normalizado:
            return valor
    return None


def _numero(valor: Any) -> float | None:
    """Convierte un valor a float, devolviendo None si no es numérico."""
    if valor is None:
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _leer_hoja_como_dicts(ruta_archivo: str, nombre_hoja: str) -> list[dict[str, Any]]:
    """Lee una hoja de Excel y devuelve una lista de diccionarios (una por fila de datos).

    Cada diccionario usa los encabezados como claves.
    """
    wb = openpyxl.load_workbook(ruta_archivo, data_only=True, read_only=True)
    ws = wb[nombre_hoja]

    columnas, fila_encabezado = _primer_encabezado_valido(ws)
    if fila_encabezado == 0:
        wb.close()
        return []

    filas = ws.iter_rows(values_only=True, min_row=fila_encabezado + 1)
    resultado: list[dict[str, Any]] = []
    for fila in filas:
        if not _fila_tiene_contenido(fila):
            continue
        registro: dict[str, Any] = {}
        for idx, nombre_col in enumerate(columnas):
            valor = fila[idx] if idx < len(fila) else None
            registro[nombre_col] = valor
        resultado.append(registro)

    wb.close()
    return resultado


def _buscar_hoja_con_columnas(
    ruta_archivo: str, columnas_necesarias: list[str]
) -> tuple[str, list[dict[str, Any]]] | None:
    """Busca en un archivo Excel una hoja que contenga todas las columnas necesarias.

    Devuelve (nombre_hoja, filas) o None si no se encuentra.
    """
    wb = openpyxl.load_workbook(ruta_archivo, data_only=True, read_only=True)
    for nombre_hoja in wb.sheetnames:
        ws = wb[nombre_hoja]
        columnas, fila_encabezado = _primer_encabezado_valido(ws)
        if fila_encabezado == 0:
            continue
        columnas_normalizadas = {str(c).strip().lower() for c in columnas if c}
        necesarias_norm = {c.strip().lower() for c in columnas_necesarias}
        if necesarias_norm.issubset(columnas_normalizadas):
            filas = _leer_hoja_como_dicts(ruta_archivo, nombre_hoja)
            wb.close()
            return nombre_hoja, filas
    wb.close()
    return None


def calcular_metricas_por_canal(ruta_carpeta_insumos: str) -> dict[str, Any]:
    """Calcula métricas globales por canal.

    Returns:
        Diccionario con:
        - canales: lista de diccionarios, uno por canal, con claves:
            canal, archivo, hoja, filas_procesadas,
            cantidad_atendida, aht, tr, gestiones_por_asesor,
            columnas_encontradas, columnas_faltantes, datos_disponibles (bool)
        - resumen: conteo de canales procesados y canales con datos insuficientes
    """
    archivos = {
        "Chatbot": "Control CHATBOT.xlsx",
        "Llamadas": "Control llamadas y correos.xlsx",
        "Correos": "Control llamadas y correos.xlsx",
        "WhatsApp": "Control WhatsApp.xlsx",
    }

    # Columnas que idealmente necesitaríamos para calcular R1
    columnas_ideales = ["Entrantes", "Contestadas", "Abandonadas", "AHT", "Tasa de Respuesta"]

    canales: list[dict[str, Any]] = []

    for nombre_canal, nombre_archivo in archivos.items():
        ruta_archivo = os.path.join(ruta_carpeta_insumos, nombre_archivo)

        if not os.path.isfile(ruta_archivo):
            canales.append(
                {
                    "canal": nombre_canal,
                    "archivo": nombre_archivo,
                    "hoja": None,
                    "filas_procesadas": 0,
                    "cantidad_atendida": None,
                    "aht": None,
                    "tr": None,
                    "gestiones_por_asesor": None,
                    "columnas_encontradas": [],
                    "columnas_faltantes": columnas_ideales,
                    "datos_disponibles": False,
                    "error": f"Archivo no encontrado: {nombre_archivo}",
                }
            )
            continue

        encontrado = _buscar_hoja_con_columnas(ruta_archivo, columnas_ideales)

        if encontrado is None:
            # Intentar con columnas parciales (al menos Contestadas y AHT)
            encontrado_parcial = _buscar_hoja_con_columnas(
                ruta_archivo, ["Contestadas", "AHT"]
            )
            if encontrado_parcial is None:
                canales.append(
                    {
                        "canal": nombre_canal,
                        "archivo": nombre_archivo,
                        "hoja": None,
                        "filas_procesadas": 0,
                        "cantidad_atendida": None,
                        "aht": None,
                        "tr": None,
                        "gestiones_por_asesor": None,
                        "columnas_encontradas": [],
                        "columnas_faltantes": columnas_ideales,
                        "datos_disponibles": False,
                        "error": "No se encontró hoja con las columnas necesarias",
                    }
                )
                continue
            nombre_hoja, filas = encontrado_parcial
            columnas_encontradas = ["Contestadas", "AHT"]
            columnas_faltantes = ["Entrantes", "Abandonadas", "Tasa de Respuesta"]
        else:
            nombre_hoja, filas = encontrado
            columnas_encontradas = columnas_ideales
            columnas_faltantes = []

        filas_procesadas = len(filas)

        # Calcular métricas agregadas
        total_contestadas = 0
        total_entantes = 0
        suma_aht = 0.0
        conteo_aht = 0
        tr_disponible = False
        tr_valor = None

        asesores: dict[str, int] = {}

        for fila in filas:
            contestadas = _numero(_obtener_valor(fila, "Contestadas"))
            entrantes = _numero(_obtener_valor(fila, "Entrantes"))
            aht = _numero(_obtener_valor(fila, "AHT"))
            tr = _numero(_obtener_valor(fila, "Tasa de Respuesta"))

            if contestadas is not None:
                total_contestadas += contestadas
            if entrantes is not None:
                total_entantes += entrantes
            if aht is not None:
                suma_aht += aht
                conteo_aht += 1
            if tr is not None:
                tr_disponible = True
                tr_valor = tr

            # Intentar identificar asesor por columna Nombre o Agente
            asesor = _obtener_valor(fila, "Nombre") or _obtener_valor(fila, "Agente")
            if asesor is not None and str(asesor).strip() != "":
                clave_asesor = str(asesor).strip()
                if contestadas is not None:
                    asesores[clave_asesor] = asesores.get(clave_asesor, 0) + contestadas

        cantidad_atendida = total_contestadas if total_contestadas > 0 else None
        aht_promedio = (suma_aht / conteo_aht) if conteo_aht > 0 else None
        tr_promedio = tr_valor if tr_disponible else None

        canales.append(
            {
                "canal": nombre_canal,
                "archivo": nombre_archivo,
                "hoja": nombre_hoja,
                "filas_procesadas": filas_procesadas,
                "cantidad_atendida": cantidad_atendida,
                "aht": round(aht_promedio, 2) if aht_promedio is not None else None,
                "tr": round(tr_promedio, 2) if tr_promedio is not None else None,
                "gestiones_por_asesor": asesores if asesores else None,
                "columnas_encontradas": columnas_encontradas,
                "columnas_faltantes": columnas_faltantes,
                "datos_disponibles": filas_procesadas > 0,
                "error": None,
            }
        )

    resumen = {
        "total_canales": len(canales),
        "canales_con_datos": sum(1 for c in canales if c["datos_disponibles"]),
        "canales_sin_datos": sum(1 for c in canales if not c["datos_disponibles"]),
    }

    return {
        "canales": canales,
        "resumen": resumen,
    }


def formatear_resultado_r1(resultado: dict[str, Any]) -> str:
    """Formatea el resultado de R1 como texto legible (Markdown)."""
    lineas: list[str] = []
    lineas.append("## R1 — Métricas globales por canal")
    lineas.append("")
    lineas.append("| Canal | Archivo | Hoja | Filas procesadas | Cantidad Atendida | AHT | TR | Gestiones por Asesor |")
    lineas.append("|-------|---------|------|------------------|-------------------|-----|----|----------------------|")

    for canal in resultado["canales"]:
        gestiones = (
            ", ".join(f"{k}={v}" for k, v in (canal["gestiones_por_asesor"] or {}).items())
            if canal["gestiones_por_asesor"]
            else "—"
        )
        lineas.append(
            f"| {canal['canal']} | {canal['archivo']} | {canal['hoja'] or '—'} | "
            f"{canal['filas_procesadas']} | {canal['cantidad_atendida'] or '—'} | "
            f"{canal['aht'] or '—'} | {canal['tr'] or '—'} | {gestiones} |"
        )

    lineas.append("")
    lineas.append("### Resumen")
    lineas.append(f"- Canales totales: {resultado['resumen']['total_canales']}")
    lineas.append(f"- Canales con datos: {resultado['resumen']['canales_con_datos']}")
    lineas.append(f"- Canales sin datos: {resultado['resumen']['canales_sin_datos']}")
    lineas.append("")

    lineas.append("### Columnas faltantes por canal")
    for canal in resultado["canales"]:
        if canal["columnas_faltantes"]:
            lineas.append(
                f"- **{canal['canal']}**: faltan {', '.join(canal['columnas_faltantes'])}"
            )
        else:
            lineas.append(f"- **{canal['canal']}**: todas las columnas ideales presentes")

    return "\n".join(lineas)


if __name__ == "__main__":
    ruta_insumos = os.path.join(os.path.dirname(__file__), "..", "..", "insumos")
    ruta_insumos = os.path.abspath(ruta_insumos)

    resultado = calcular_metricas_por_canal(ruta_insumos)
    print(formatear_resultado_r1(resultado))
