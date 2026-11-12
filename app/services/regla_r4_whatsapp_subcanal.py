"""Regla de negocio R4: desglose WhatsApp por subcanal.

Calcula métricas operativas individuales separando WhatsApp y Llamadas
(Atendidas, AHT, TR) para la sección de Redes Sociales del informe.

Los datos de entrada vienen de los archivos Excel de `insumos/`.
Esta función solo lee; nunca escribe dentro de `insumos/`.

IMPORTANTE: los archivos de insumos no tienen una columna clara que distinga
el subcanal "WhatsApp" del subcanal "Llamadas" con valores exactos. Esta regla
busca las columnas de métricas disponibles y reporta explícitamente si no se
puede separar por subcanal, sin inventar valores.
"""

from __future__ import annotations

import os
from typing import Any

import openpyxl

from app.services.lectura_insumos import _fila_tiene_contenido, _primer_encabezado_valido


def _normalizar(texto: str) -> str:
    """Normaliza texto para comparación: minúsculas, sin espacios extra."""
    return texto.strip().lower()


def _numero(valor: Any) -> float | None:
    """Convierte un valor a float, devolviendo None si no es numérico."""
    if valor is None:
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _leer_hoja_como_listas(ruta_archivo: str, nombre_hoja: str) -> tuple[list[str], list[list[Any]]]:
    """Lee una hoja de Excel y devuelve encabezados y filas de datos.

    Maneja columnas duplicadas manteniendo todas las columnas con su índice.
    Devuelve (encabezados, filas) donde cada fila es una lista de valores.
    """
    wb = openpyxl.load_workbook(ruta_archivo, data_only=True, read_only=True)
    ws = wb[nombre_hoja]

    columnas, fila_encabezado = _primer_encabezado_valido(ws)
    if fila_encabezado == 0:
        wb.close()
        return [], []

    filas = ws.iter_rows(values_only=True, min_row=fila_encabezado + 1)
    resultado: list[list[Any]] = []
    for fila in filas:
        if not _fila_tiene_contenido(fila):
            continue
        resultado.append(list(fila))

    wb.close()
    return columnas, resultado


def _buscar_indices_columnas(
    encabezados: list[str], nombres_buscados: list[str]
) -> dict[str, list[int]]:
    """Busca los índices de columnas que coincidan con los nombres buscados.

    Devuelve un diccionario: nombre_buscado -> lista de índices (puede haber varios
    si hay columnas duplicadas).
    """
    resultado: dict[str, list[int]] = {}
    for nombre in nombres_buscados:
        nombre_norm = _normalizar(nombre)
        indices: list[int] = []
        for idx, col in enumerate(encabezados):
            if col is not None and _normalizar(str(col)) == nombre_norm:
                indices.append(idx)
        resultado[nombre] = indices
    return resultado


def _buscar_hoja_con_metricas(
    ruta_archivo: str,
) -> tuple[str, list[str], list[list[Any]]] | None:
    """Busca una hoja que tenga columnas de métricas (Contestadas, AHT, Tasa de Respuesta).

    Devuelve (nombre_hoja, encabezados, filas) o None.
    """
    wb = openpyxl.load_workbook(ruta_archivo, data_only=True, read_only=True)
    for nombre_hoja in wb.sheetnames:
        ws = wb[nombre_hoja]
        columnas, fila_encabezado = _primer_encabezado_valido(ws)
        if fila_encabezado == 0:
            continue
        columnas_norm = {_normalizar(str(c)) for c in columnas if c}
        necesarias = {"contestadas", "aht", "tasa de respuesta"}
        if necesarias.issubset(columnas_norm):
            filas = _leer_hoja_como_listas(ruta_archivo, nombre_hoja)[1]
            wb.close()
            return nombre_hoja, columnas, filas
    wb.close()
    return None


def _obtener_valor_primera_columna(
    fila: list[Any], indices: list[int]
) -> float | None:
    """Obtiene el primer valor numérico no None de una fila usando los índices dados."""
    for idx in indices:
        if idx < len(fila):
            num = _numero(fila[idx])
            if num is not None:
                return num
    return None


def _buscar_columna_canal(encabezados: list[str]) -> int | None:
    """Busca el índice de una columna que pueda distinguir el subcanal (Canal, Tipo, Application, etc.)."""
    nombres_canal = ("canal", "tipo", "application", "subcanal")
    for idx, col in enumerate(encabezados):
        if col is not None and _normalizar(str(col)) in nombres_canal:
            return idx
    return None


def _filtrar_por_subcanal(
    filas: list[list[Any]], idx_canal: int | None, nombre_subcanal: str
) -> list[list[Any]]:
    """Filtra filas por el valor de la columna de canal, si existe.

    Si no hay columna de canal, devuelve todas las filas.
    """
    if idx_canal is None:
        return filas

    nombre_norm = _normalizar(nombre_subcanal)
    resultado: list[list[Any]] = []
    for fila in filas:
        if idx_canal < len(fila):
            valor = fila[idx_canal]
            if valor is not None and nombre_norm in _normalizar(str(valor)):
                resultado.append(fila)
    return resultado


def calcular_whatsapp_por_subcanal(ruta_carpeta_insumos: str) -> dict[str, Any]:
    """Calcula métricas por subcanal (WhatsApp y Llamadas por separado).

    Returns:
        Diccionario con:
        - subcanales: lista de diccionarios, uno por subcanal, con claves:
            subcanal, archivo, hoja, filas_procesadas,
            atendidas, aht, tr, datos_disponibles (bool),
            columnas_faltantes (list), se_pudo_filtrar_por_subcanal (bool)
        - resumen: conteo de subcanales procesados y sin datos
    """
    archivos_posibles = [
        "Control WhatsApp.xlsx",
        "Control llamadas y correos.xlsx",
    ]

    subcanales: list[dict[str, Any]] = []
    subcanales_con_datos = 0

    for nombre_subcanal in ["WhatsApp", "Llamadas"]:
        encontrado_en_cualquier_archivo = False

        for nombre_archivo in archivos_posibles:
            ruta_archivo = os.path.join(ruta_carpeta_insumos, nombre_archivo)

            if not os.path.isfile(ruta_archivo):
                continue

            encontrado = _buscar_hoja_con_metricas(ruta_archivo)

            if encontrado is None:
                continue

            nombre_hoja, encabezados, filas = encontrado

            # Buscar columna que distinga el subcanal
            idx_canal = _buscar_columna_canal(encabezados)
            se_pudo_filtrar = idx_canal is not None

            # Filtrar filas por subcanal
            filas_filtradas = _filtrar_por_subcanal(filas, idx_canal, nombre_subcanal)
            filas_procesadas = len(filas_filtradas)

            # Buscar índices de columnas de métricas
            indices_metricas = _buscar_indices_columnas(
                encabezados, ["Contestadas", "AHT", "Tasa de Respuesta"]
            )

            # Calcular métricas
            contestadas_vals: list[float] = []
            aht_vals: list[float] = []
            tr_vals: list[float] = []

            for fila in filas_filtradas:
                c = _obtener_valor_primera_columna(fila, indices_metricas["Contestadas"])
                if c is not None:
                    contestadas_vals.append(c)
                a = _obtener_valor_primera_columna(fila, indices_metricas["AHT"])
                if a is not None:
                    aht_vals.append(a)
                t = _obtener_valor_primera_columna(fila, indices_metricas["Tasa de Respuesta"])
                if t is not None:
                    tr_vals.append(t)

            atendidas = sum(contestadas_vals) if contestadas_vals else None
            aht_promedio = (sum(aht_vals) / len(aht_vals)) if aht_vals else None
            tr_promedio = (sum(tr_vals) / len(tr_vals)) if tr_vals else None

            # Determinar columnas faltantes
            columnas_ideales = ["Contestadas", "AHT", "Tasa de Respuesta"]
            columnas_encontradas: list[str] = []
            columnas_faltantes: list[str] = []

            for col_ideal in columnas_ideales:
                if indices_metricas[col_ideal]:
                    columnas_encontradas.append(col_ideal)
                else:
                    columnas_faltantes.append(col_ideal)

            if not se_pudo_filtrar:
                columnas_faltantes.append(
                    "Columna para distinguir subcanal (Canal/Tipo/Application)"
                )

            datos_disponibles = filas_procesadas > 0 and atendidas is not None

            if datos_disponibles:
                subcanales_con_datos += 1

            subcanales.append(
                {
                    "subcanal": nombre_subcanal,
                    "archivo": nombre_archivo,
                    "hoja": nombre_hoja,
                    "filas_procesadas": filas_procesadas,
                    "atendidas": int(atendidas) if atendidas is not None else None,
                    "aht": round(aht_promedio, 2) if aht_promedio is not None else None,
                    "tr": round(tr_promedio, 2) if tr_promedio is not None else None,
                    "datos_disponibles": datos_disponibles,
                    "columnas_faltantes": columnas_faltantes,
                    "se_pudo_filtrar_por_subcanal": se_pudo_filtrar,
                    "columna_canal_usada": (
                        encabezados[idx_canal] if idx_canal is not None else None
                    ),
                }
            )
            encontrado_en_cualquier_archivo = True
            break

        if not encontrado_en_cualquier_archivo:
            subcanales.append(
                {
                    "subcanal": nombre_subcanal,
                    "archivo": None,
                    "hoja": None,
                    "filas_procesadas": 0,
                    "atendidas": None,
                    "aht": None,
                    "tr": None,
                    "datos_disponibles": False,
                    "columnas_faltantes": ["Archivo con métricas no encontrado"],
                    "se_pudo_filtrar_por_subcanal": False,
                    "columna_canal_usada": None,
                }
            )

    resumen = {
        "total_subcanales": 2,
        "subcanales_con_datos": subcanales_con_datos,
        "subcanales_sin_datos": 2 - subcanales_con_datos,
    }

    return {
        "subcanales": subcanales,
        "resumen": resumen,
    }


def formatear_resultado_r4(resultado: dict[str, Any]) -> str:
    """Formatea el resultado de R4 como texto legible (Markdown)."""
    lineas: list[str] = []
    lineas.append("## R4 — Desglose WhatsApp por subcanal")
    lineas.append("")
    lineas.append(
        "| Subcanal | Archivo | Hoja | Filas procesadas | Atendidas | AHT | TR |"
    )
    lineas.append("|----------|---------|------|------------------|-----------|-----|----|")

    for sub in resultado["subcanales"]:
        lineas.append(
            f"| {sub['subcanal']} | {sub['archivo'] or '—'} | {sub['hoja'] or '—'} | "
            f"{sub['filas_procesadas']} | {sub['atendidas'] or '—'} | "
            f"{sub['aht'] or '—'} | {sub['tr'] or '—'} |"
        )

    lineas.append("")
    lineas.append("### Resumen")
    lineas.append(f"- Total subcanales: {resultado['resumen']['total_subcanales']}")
    lineas.append(f"- Subcanales con datos: {resultado['resumen']['subcanales_con_datos']}")
    lineas.append(f"- Subcanales sin datos: {resultado['resumen']['subcanales_sin_datos']}")
    lineas.append("")

    lineas.append("### Columnas faltantes por subcanal")
    for sub in resultado["subcanales"]:
        if sub["columnas_faltantes"]:
            lineas.append(
                f"- **{sub['subcanal']}**: {', '.join(sub['columnas_faltantes'])}"
            )
        else:
            lineas.append(f"- **{sub['subcanal']}**: todas las columnas presentes")

    lineas.append("")
    lineas.append("### Nota sobre separación por subcanal")
    for sub in resultado["subcanales"]:
        if not sub["se_pudo_filtrar_por_subcanal"]:
            lineas.append(
                f"- **{sub['subcanal']}**: no se encontró columna que distinga "
                f"WhatsApp de Llamadas; se usaron todas las filas del archivo."
            )
        else:
            lineas.append(
                f"- **{sub['subcanal']}**: se filtró por la columna "
                f"'{sub['columna_canal_usada']}'."
            )

    return "\n".join(lineas)


if __name__ == "__main__":
    ruta_insumos = os.path.join(os.path.dirname(__file__), "..", "..", "insumos")
    ruta_insumos = os.path.abspath(ruta_insumos)

    resultado = calcular_whatsapp_por_subcanal(ruta_insumos)
    print(formatear_resultado_r4(resultado))
