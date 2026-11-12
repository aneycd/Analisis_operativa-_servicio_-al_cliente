"""Regla de negocio R2: desglose de correos por buzón.

Calcula la cantidad atendida por cada buzón de correos mencionado en el contexto:
- Bienes adquiridos
- Centro Asistencia N1
- Centro Asistencia N2
- Operativa CAC PCI
- Servicio oficina virtual
- Soporte CAC

Los datos de entrada vienen de los archivos Excel de `insumos/`.
Esta función solo lee; nunca escribe dentro de `insumos/`.

IMPORTANTE: los nombres exactos de los buzones del contexto no se han confirmado
como columnas en los insumos. Esta regla busca columnas que coincidan con esos
nombres (tolerante a mayúsculas/minúsculas y espacios) y reporta explícitamente
cuáles buzones faltan, sin inventar valores.
"""

from __future__ import annotations

import os
from typing import Any

import openpyxl

from app.services.lectura_insumos import _fila_tiene_contenido, _primer_encabezado_valido


BUZONES_CONTEXTO = [
    "Bienes adquiridos",
    "Centro Asistencia N1",
    "Centro Asistencia N2",
    "Operativa CAC PCI",
    "Servicio oficina virtual",
    "Soporte CAC",
]


def _normalizar(texto: str) -> str:
    """Normaliza texto para comparación: minúsculas, sin espacios extra."""
    return texto.strip().lower()


def _buscar_columna_buzon(columnas: list[str], nombre_buzon: str) -> str | None:
    """Busca una columna cuyo nombre coincida con el buzón (tolerante).

    Devuelve el nombre exacto de la columna encontrada o None.
    """
    nombre_normalizado = _normalizar(nombre_buzon)
    for col in columnas:
        if col is not None and _normalizar(str(col)) == nombre_normalizado:
            return str(col)
    return None


def _leer_hoja_como_dicts(ruta_archivo: str, nombre_hoja: str) -> list[dict[str, Any]]:
    """Lee una hoja de Excel y devuelve una lista de diccionarios (una por fila de datos)."""
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


def _numero(valor: Any) -> float | None:
    """Convierte un valor a float, devolviendo None si no es numérico."""
    if valor is None:
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _buscar_hoja_con_columnas_correos(
    ruta_archivo: str,
) -> tuple[str, list[dict[str, Any]], list[str]] | None:
    """Busca una hoja que tenga la columna 'Correos' o similar para conteo de correos.

    Devuelve (nombre_hoja, filas, columnas_detectadas) o None.
    """
    wb = openpyxl.load_workbook(ruta_archivo, data_only=True, read_only=True)
    for nombre_hoja in wb.sheetnames:
        ws = wb[nombre_hoja]
        columnas, fila_encabezado = _primer_encabezado_valido(ws)
        if fila_encabezado == 0:
            continue
        columnas_norm = {_normalizar(str(c)) for c in columnas if c}
        # Buscar columnas relacionadas con correos
        col_correos = None
        for c in columnas:
            if c is not None:
                cn = _normalizar(str(c))
                if "correo" in cn or "correos" in cn:
                    col_correos = str(c)
                    break
        if col_correos is None:
            continue
        filas = _leer_hoja_como_dicts(ruta_archivo, nombre_hoja)
        wb.close()
        return nombre_hoja, filas, [col_correos]
    wb.close()
    return None


def calcular_correos_por_buzon(ruta_carpeta_insumos: str) -> dict[str, Any]:
    """Calcula la cantidad de correos atendidos por cada buzón del contexto.

    Returns:
        Diccionario con:
        - buzones: lista de diccionarios, uno por buzón, con claves:
            buzón, archivo, hoja, cantidad_atendida, columna_encontrada,
            datos_disponibles (bool)
        - resumen: conteo de buzones encontrados y no encontrados
        - columnas_faltantes: lista de buzones que no tienen columna correspondiente
    """
    archivos_posibles = [
        "Control llamadas y correos.xlsx",
        "Control WhatsApp.xlsx",
    ]

    resultado_buzones: list[dict[str, Any]] = []
    buzones_encontrados = 0

    for nombre_buzon in BUZONES_CONTEXTO:
        encontrado_en_cualquier_archivo = False

        for nombre_archivo in archivos_posibles:
            ruta_archivo = os.path.join(ruta_carpeta_insumos, nombre_archivo)

            if not os.path.isfile(ruta_archivo):
                continue

            encontrado = _buscar_hoja_con_columnas_correos(ruta_archivo)

            if encontrado is None:
                continue

            nombre_hoja, filas, columnas_detectadas = encontrado

            # Leer encabezados de la hoja para buscar la columna del buzón
            wb = openpyxl.load_workbook(ruta_archivo, data_only=True, read_only=True)
            ws = wb[nombre_hoja]
            columnas_hoja, _ = _primer_encabezado_valido(ws)
            wb.close()

            columna_buzon = _buscar_columna_buzon(columnas_hoja, nombre_buzon)

            if columna_buzon is None:
                continue

            # Sumar valores de la columna del buzón
            cantidad_total = 0
            for fila in filas:
                valor = _numero(fila.get(columna_buzon))
                if valor is not None:
                    cantidad_total += int(valor)

            resultado_buzones.append(
                {
                    "buzon": nombre_buzon,
                    "archivo": nombre_archivo,
                    "hoja": nombre_hoja,
                    "cantidad_atendida": cantidad_total if cantidad_total > 0 else None,
                    "columna_encontrada": columna_buzon,
                    "datos_disponibles": True,
                }
            )
            buzones_encontrados += 1
            encontrado_en_cualquier_archivo = True
            break  # pasar al siguiente buzón

        if not encontrado_en_cualquier_archivo:
            resultado_buzones.append(
                {
                    "buzon": nombre_buzon,
                    "archivo": None,
                    "hoja": None,
                    "cantidad_atendida": None,
                    "columna_encontrada": None,
                    "datos_disponibles": False,
                }
            )

    buzones_no_encontrados = [
        b["buzon"] for b in resultado_buzones if not b["datos_disponibles"]
    ]

    resumen = {
        "total_buzones": len(BUZONES_CONTEXTO),
        "buzones_encontrados": buzones_encontrados,
        "buzones_no_encontrados": len(buzones_no_encontrados),
    }

    return {
        "buzones": resultado_buzones,
        "resumen": resumen,
        "columnas_faltantes": buzones_no_encontrados,
    }


def formatear_resultado_r2(resultado: dict[str, Any]) -> str:
    """Formatea el resultado de R2 como texto legible (Markdown)."""
    lineas: list[str] = []
    lineas.append("## R2 — Desglose de correos por buzón")
    lineas.append("")
    lineas.append(
        "| Buzón | Archivo | Hoja | Cantidad Atendida | Columna encontrada |"
    )
    lineas.append("|-------|---------|------|-------------------|--------------------|")

    for buzon in resultado["buzones"]:
        if buzon["datos_disponibles"]:
            lineas.append(
                f"| {buzon['buzon']} | {buzon['archivo']} | {buzon['hoja']} | "
                f"{buzon['cantidad_atendida']} | {buzon['columna_encontrada']} |"
            )
        else:
            lineas.append(
                f"| {buzon['buzon']} | — | — | — | — |"
            )

    lineas.append("")
    lineas.append("### Resumen")
    lineas.append(f"- Total buzones del contexto: {resultado['resumen']['total_buzones']}")
    lineas.append(f"- Buzones encontrados en insumos: {resultado['resumen']['buzones_encontrados']}")
    lineas.append(f"- Buzones no encontrados: {resultado['resumen']['buzones_no_encontrados']}")
    lineas.append("")

    if resultado["columnas_faltantes"]:
        lineas.append("### Buzones sin columna correspondiente en insumos")
        for nombre in resultado["columnas_faltantes"]:
            lineas.append(f"- {nombre}")
    else:
        lineas.append("### Todos los buzones tienen columna correspondiente")

    return "\n".join(lineas)


if __name__ == "__main__":
    ruta_insumos = os.path.join(os.path.dirname(__file__), "..", "..", "insumos")
    ruta_insumos = os.path.abspath(ruta_insumos)

    resultado = calcular_correos_por_buzon(ruta_insumos)
    print(formatear_resultado_r2(resultado))
