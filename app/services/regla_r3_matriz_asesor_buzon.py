"""Regla de negocio R3: matriz Asesor vs Buzón de correos.

Crea una tabla cruzada donde las filas son asesores y las columnas son los 6
buzones del contexto, con la cantidad de correos gestionados por cada asesor
en cada buzón.

Los datos de entrada vienen de los archivos Excel de `insumos/`.
Esta función solo lee; nunca escribe dentro de `insumos/`.

IMPORTANTE: en la regla R2 se confirmó que ninguno de los 6 buzones del contexto
existe como columna en los insumos. Por lo tanto, esta regla no puede calcular
una matriz real. Reporta explícitamente el vacío, sin inventar valores.
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


def _buscar_hoja_con_correos(
    ruta_archivo: str,
) -> tuple[str, list[dict[str, Any]], list[str]] | None:
    """Busca una hoja que tenga la columna 'Correos' o similar.

    Devuelve (nombre_hoja, filas, columnas_detectadas) o None.
    """
    wb = openpyxl.load_workbook(ruta_archivo, data_only=True, read_only=True)
    for nombre_hoja in wb.sheetnames:
        ws = wb[nombre_hoja]
        columnas, fila_encabezado = _primer_encabezado_valido(ws)
        if fila_encabezado == 0:
            continue
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


def _obtener_asesor(fila: dict[str, Any]) -> str | None:
    """Extrae el nombre del asesor de una fila, por columna Nombre o Agente."""
    for clave in ("Nombre", "Agente", "Nombre de Agente", "Nombre Agente"):
        valor = fila.get(clave)
        if valor is not None and str(valor).strip() != "":
            return str(valor).strip()
    return None


def calcular_matriz_asesor_buzon(ruta_carpeta_insumos: str) -> dict[str, Any]:
    """Calcula la matriz Asesor vs Buzón de correos.

    Returns:
        Diccionario con:
        - matriz: diccionario clave = asesor, valor = diccionario buzón -> cantidad
        - asesores: lista de nombres de asesores encontrados
        - buzones: lista de buzones del contexto
        - buzones_con_columna: lista de buzones que sí tienen columna en insumos
        - buzones_sin_columna: lista de buzones que NO tienen columna en insumos
        - archivo_usado: nombre del archivo donde se buscó
        - hoja_usada: nombre de la hoja donde se buscó
        - datos_disponibles: bool, True si al menos un buzón tiene columna
    """
    archivos_posibles = [
        "Control llamadas y correos.xlsx",
        "Control WhatsApp.xlsx",
    ]

    matriz: dict[str, dict[str, int | None]] = {}
    asesores_encontrados: set[str] = set()
    buzones_con_columna: list[str] = []
    buzones_sin_columna: list[str] = []
    archivo_usado: str | None = None
    hoja_usada: str | None = None

    for nombre_archivo in archivos_posibles:
        ruta_archivo = os.path.join(ruta_carpeta_insumos, nombre_archivo)

        if not os.path.isfile(ruta_archivo):
            continue

        encontrado = _buscar_hoja_con_correos(ruta_archivo)

        if encontrado is None:
            continue

        nombre_hoja, filas, columnas_detectadas = encontrado

        # Leer encabezados para buscar columnas de buzón y de asesor
        wb = openpyxl.load_workbook(ruta_archivo, data_only=True, read_only=True)
        ws = wb[nombre_hoja]
        columnas_hoja, _ = _primer_encabezado_valido(ws)
        wb.close()

        # Identificar qué buzones tienen columna en esta hoja
        columnas_buzon_encontradas: dict[str, str] = {}  # nombre_buzon -> nombre_columna
        for nombre_buzon in BUZONES_CONTEXTO:
            col = _buscar_columna_buzon(columnas_hoja, nombre_buzon)
            if col is not None:
                columnas_buzon_encontradas[nombre_buzon] = col
                buzones_con_columna.append(nombre_buzon)

        if not columnas_buzon_encontradas:
            # Ningún buzón tiene columna en este archivo, seguir buscando
            continue

        archivo_usado = nombre_archivo
        hoja_usada = nombre_hoja

        # Procesar filas: para cada asesor, sumar por buzón
        for fila in filas:
            asesor = _obtener_asesor(fila)
            if asesor is None:
                continue

            asesores_encontrados.add(asesor)

            if asesor not in matriz:
                matriz[asesor] = {b: 0 for b in BUZONES_CONTEXTO}

            for nombre_buzon, columna in columnas_buzon_encontradas.items():
                valor = _numero(fila.get(columna))
                if valor is not None:
                    matriz[asesor][nombre_buzon] = (
                        (matriz[asesor].get(nombre_buzon) or 0) + int(valor)
                    )

        # Si ya encontramos datos, no necesitamos seguir buscando en otros archivos
        break

    # Determinar buzones sin columna
    buzones_sin_columna = [
        b for b in BUZONES_CONTEXTO if b not in buzones_con_columna
    ]

    datos_disponibles = len(buzones_con_columna) > 0 and len(asesores_encontrados) > 0

    return {
        "matriz": matriz,
        "asesores": sorted(asesores_encontrados),
        "buzones": BUZONES_CONTEXTO,
        "buzones_con_columna": buzones_con_columna,
        "buzones_sin_columna": buzones_sin_columna,
        "archivo_usado": archivo_usado,
        "hoja_usada": hoja_usada,
        "datos_disponibles": datos_disponibles,
    }


def formatear_resultado_r3(resultado: dict[str, Any]) -> str:
    """Formatea el resultado de R3 como texto legible (Markdown)."""
    lineas: list[str] = []
    lineas.append("## R3 — Matriz Asesor vs Buzón de correos")
    lineas.append("")

    if not resultado["datos_disponibles"]:
        lineas.append("### No hay datos disponibles para calcular la matriz")
        lineas.append("")
        lineas.append("**Motivo:** ninguno de los 6 buzones del contexto tiene una "
                      "columna correspondiente en los archivos de insumos.")
        lineas.append("")
        lineas.append("### Buzones del contexto sin columna en insumos")
        for buzon in resultado["buzones_sin_columna"]:
            lineas.append(f"- {buzon}")
        lineas.append("")
        lineas.append("### Archivos revisados")
        if resultado["archivo_usado"]:
            lineas.append(
                f"- {resultado['archivo_usado']} (hoja: {resultado['hoja_usado']})"
            )
        else:
            lineas.append("- No se encontró hoja con columnas de correos en los insumos")
        lineas.append("")
        lineas.append("**Nota:** no se inventaron valores. La matriz requiere que los "
                      "buzones existan como columnas en los insumos.")
        return "\n".join(lineas)

    lineas.append("### Matriz Asesor × Buzón (cantidad de correos gestionados)")
    lineas.append("")

    # Encabezado de tabla
    encabezado = "| Asesor | " + " | ".join(resultado["buzones"]) + " | Total |"
    separador = "|--------|" + "|".join(["--------"] * len(resultado["buzones"])) + "|--------|"
    lineas.append(encabezado)
    lineas.append(separador)

    for asesor in resultado["asesores"]:
        fila_matriz = resultado["matriz"].get(asesor, {})
        total = sum(v for v in fila_matriz.values() if v is not None)
        celdas = " | ".join(
            str(fila_matriz.get(b) or 0) for b in resultado["buzones"]
        )
        lineas.append(f"| {asesor} | {celdas} | {total} |")

    lineas.append("")
    lineas.append("### Archivo y hoja utilizados")
    lineas.append(f"- Archivo: {resultado['archivo_usado']}")
    lineas.append(f"- Hoja: {resultado['hoja_usada']}")
    lineas.append("")
    lineas.append("### Buzones con columna encontrada")
    for buzon in resultado["buzones_con_columna"]:
        lineas.append(f"- {buzon}")
    lineas.append("")
    if resultado["buzones_sin_columna"]:
        lineas.append("### Buzones sin columna en insumos")
        for buzon in resultado["buzones_sin_columna"]:
            lineas.append(f"- {buzon}")

    return "\n".join(lineas)


if __name__ == "__main__":
    ruta_insumos = os.path.join(os.path.dirname(__file__), "..", "..", "insumos")
    ruta_insumos = os.path.abspath(ruta_insumos)

    resultado = calcular_matriz_asesor_buzon(ruta_insumos)
    print(formatear_resultado_r3(resultado))
