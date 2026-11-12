"""Lectura de archivos de insumos (solo lectura).

Lee cada archivo Excel de la carpeta `insumos/` y devuelve, por hoja:
- nombre de la hoja
- columnas (encabezados de la primera fila)
- número de filas de datos (excluyendo el encabezado)

Nunca escribe nada dentro de `insumos/`.
"""

from __future__ import annotations

import os
from typing import Any

import openpyxl


def _fila_tiene_contenido(fila: tuple[Any, ...]) -> bool:
    """Devuelve True si la fila tiene al menos una celda no vacía."""
    return any(c is not None and str(c).strip() != "" for c in fila)


def _primer_encabezado_valido(ws) -> tuple[list[str], int]:
    """Busca la primera fila no vacía de la hoja y la devuelve como encabezado.

    Devuelve (lista_de_columnas, indice_fila_encabezado_base_1).
    Si la hoja está completamente vacía, devuelve ([], 0).
    """
    for indice, fila in enumerate(ws.iter_rows(values_only=True), start=1):
        if _fila_tiene_contenido(fila):
            columnas = [str(c) if c is not None else "" for c in fila]
            return columnas, indice
    return [], 0


def leer_archivo_excel(ruta_archivo: str) -> list[dict[str, Any]]:
    """Lee un archivo Excel y devuelve información de cada hoja.

    Args:
        ruta_archivo: ruta absoluta o relativa al archivo .xlsx

    Returns:
        Lista de diccionarios, uno por hoja, con claves:
        - hoja: nombre de la hoja
        - columnas: lista de nombres de columna (encabezados detectados en la
          primera fila con contenido)
        - filas_datos: número de filas con contenido, excluyendo el encabezado
        - filas_total: número total de filas de la hoja
        - fila_encabezado: número de fila (base 1) donde se detectó el encabezado
    """
    resultado: list[dict[str, Any]] = []

    wb = openpyxl.load_workbook(ruta_archivo, data_only=True, read_only=True)

    for nombre_hoja in wb.sheetnames:
        ws = wb[nombre_hoja]

        columnas, fila_encabezado = _primer_encabezado_valido(ws)

        if fila_encabezado == 0:
            resultado.append(
                {
                    "hoja": nombre_hoja,
                    "columnas": [],
                    "filas_datos": 0,
                    "filas_total": ws.max_row,
                    "fila_encabezado": 0,
                }
            )
            continue

        n_datos = 0
        filas = ws.iter_rows(values_only=True, min_row=fila_encabezado + 1)
        for fila in filas:
            if _fila_tiene_contenido(fila):
                n_datos += 1

        resultado.append(
            {
                "hoja": nombre_hoja,
                "columnas": columnas,
                "filas_datos": n_datos,
                "filas_total": ws.max_row,
                "fila_encabezado": fila_encabezado,
            }
        )

    wb.close()
    return resultado


def leer_insumos(ruta_carpeta_insumos: str) -> dict[str, list[dict[str, Any]]]:
    """Lee todos los archivos Excel de la carpeta de insumos.

    Args:
        ruta_carpeta_insumos: ruta a la carpeta `insumos/`

    Returns:
        Diccionario clave = nombre de archivo, valor = lista de hojas
        (cada hoja con columnas y filas de datos).
    """
    insumos: dict[str, list[dict[str, Any]]] = {}

    if not os.path.isdir(ruta_carpeta_insumos):
        return insumos

    for nombre_archivo in sorted(os.listdir(ruta_carpeta_insumos)):
        if not nombre_archivo.lower().endswith((".xlsx", ".xls")):
            continue

        ruta_completa = os.path.join(ruta_carpeta_insumos, nombre_archivo)
        insumos[nombre_archivo] = leer_archivo_excel(ruta_completa)

    return insumos


def imprimir_reporte(insumos: dict[str, list[dict[str, Any]]]) -> None:
    """Imprime un reporte legible de columnas y filas por archivo y hoja."""
    for nombre_archivo, hojas in insumos.items():
        print(f"===== {nombre_archivo} =====")
        for hoja in hojas:
            columnas_str = ", ".join(c for c in hoja["columnas"] if c) if hoja["columnas"] else "(sin encabezados)"
            print(
                f"  Hoja '{hoja['hoja']}': "
                f"{len(hoja['columnas'])} columnas, "
                f"{hoja['filas_datos']} filas de datos, "
                f"encabezado en fila {hoja['fila_encabezado']}"
            )
            if hoja["columnas"]:
                print(f"    Columnas: {columnas_str[:200]}{'...' if len(columnas_str) > 200 else ''}")
        print()


if __name__ == "__main__":
    # Ruta relativa a la carpeta insumos desde la raíz del proyecto
    ruta_insumos = os.path.join(os.path.dirname(__file__), "..", "..", "insumos")
    ruta_insumos = os.path.abspath(ruta_insumos)

    datos = leer_insumos(ruta_insumos)
    imprimir_reporte(datos)
