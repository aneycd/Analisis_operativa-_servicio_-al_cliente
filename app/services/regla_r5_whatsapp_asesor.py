"""Regla de negocio R5: desempeño por asesor de WhatsApp.

Calcula por asesor:
- Cantidad atendida en WhatsApp
- Cantidad de llamadas atendidas
- Tiempo de ocupación
- AHT del asesor
- Total de gestiones atendidas (suma global)

Los datos de entrada vienen de los archivos Excel de `insumos/`.
Esta función solo lee; nunca escribe dentro de `insumos/`.

IMPORTANTE: en las entregas R2 y R4 se confirmó que no hay columna que
distinga WhatsApp de Llamadas como subcanales separados, y que los datos
pueden venir mezclados. Esta regla calcula lo que pueda con las columnas
disponibles y reporta explícitamente qué no se puede separar, sin inventar
valores.
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

    Devuelve un diccionario: nombre_buscado -> lista de índices.
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


def _buscar_hoja_con_asesores_y_metricas(
    ruta_archivo: str,
) -> tuple[str, list[str], list[list[Any]]] | None:
    """Busca una hoja que tenga columnas de asesor y métricas.

    Busca columnas como: Nombre, Agente, AgentLogin, Contestadas, AHT,
    % Ocupación, Tiempo de ocupación, etc.

    Devuelve (nombre_hoja, encabezados, filas) o None.
    """
    wb = openpyxl.load_workbook(ruta_archivo, data_only=True, read_only=True)
    for nombre_hoja in wb.sheetnames:
        ws = wb[nombre_hoja]
        columnas, fila_encabezado = _primer_encabezado_valido(ws)
        if fila_encabezado == 0:
            continue

        columnas_norm = {_normalizar(str(c)) for c in columnas if c}

        # Debe tener al menos una columna de asesor y una de métricas
        tiene_asesor = any(
            n in columnas_norm
            for n in ("nombre", "agente", "agentlogin", "nombre de agente", "nombre agente")
        )
        tiene_metrica = any(
            n in columnas_norm
            for n in ("contestadas", "aht", "% ocupación", "% ocupacion", "tiempo de ocupación")
        )

        if tiene_asesor and tiene_metrica:
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


def _obtener_texto_primera_columna(
    fila: list[Any], indices: list[int]
) -> str | None:
    """Obtiene el primer valor de texto no vacío de una fila usando los índices dados."""
    for idx in indices:
        if idx < len(fila):
            valor = fila[idx]
            if valor is not None and str(valor).strip() != "":
                return str(valor).strip()
    return None


def calcular_desempeño_asesor_whatsapp(ruta_carpeta_insumos: str) -> dict[str, Any]:
    """Calcula desempeño por asesor para WhatsApp/Llamadas.

    Returns:
        Diccionario con:
        - asesores: lista de diccionarios, uno por asesor, con claves:
            asesor, cantidad_whatsapp, cantidad_llamadas,
            tiempo_ocupacion, aht, total_gestiones,
            columnas_faltantes (list), datos_disponibles (bool)
        - resumen: conteo de asesores y totales globales
        - nota_limitacion: explicación sobre qué no se pudo separar
    """
    archivos_posibles = [
        "Control WhatsApp.xlsx",
        "Control llamadas y correos.xlsx",
    ]

    asesores_data: dict[str, dict[str, Any]] = {}
    archivo_usado: str | None = None
    hoja_usada: str | None = None

    for nombre_archivo in archivos_posibles:
        ruta_archivo = os.path.join(ruta_carpeta_insumos, nombre_archivo)

        if not os.path.isfile(ruta_archivo):
            continue

        encontrado = _buscar_hoja_con_asesores_y_metricas(ruta_archivo)

        if encontrado is None:
            continue

        nombre_hoja, encabezados, filas = encontrado

        # Buscar índices de columnas relevantes
        indices_asesor = _buscar_indices_columnas(
            encabezados,
            ["Nombre", "Agente", "AgentLogin", "Nombre de Agente", "Nombre Agente"],
        )
        indices_contestadas = _buscar_indices_columnas(encabezados, ["Contestadas"])
        indices_aht = _buscar_indices_columnas(encabezados, ["AHT"])
        indices_ocupacion = _buscar_indices_columnas(
            encabezados, ["% Ocupación", "% Ocupacion", "Tiempo de Ocupación", "Tiempo de Ocupacion"]
        )

        # Aplanar índices de asesor (tomar el primero de cada tipo)
        idx_asesor = None
        for clave in ("Nombre", "Agente", "AgentLogin", "Nombre de Agente", "Nombre Agente"):
            if indices_asesor.get(clave):
                idx_asesor = indices_asesor[clave][0]
                break

        if idx_asesor is None:
            continue

        archivo_usado = nombre_archivo
        hoja_usada = nombre_hoja

        # Procesar filas
        for fila in filas:
            asesor = _obtener_texto_primera_columna(fila, [idx_asesor])
            if asesor is None:
                continue

            if asesor not in asesores_data:
                asesores_data[asesor] = {
                    "asesor": asesor,
                    "cantidad_whatsapp": None,
                    "cantidad_llamadas": None,
                    "tiempo_ocupacion": None,
                    "aht": None,
                    "total_gestiones": 0,
                    "filas_procesadas": 0,
                    "suma_contestadas": 0,
                    "suma_aht": 0.0,
                    "conteo_aht": 0,
                    "suma_ocupacion": 0.0,
                    "conteo_ocupacion": 0,
                }

            datos = asesores_data[asesor]
            datos["filas_procesadas"] += 1

            # Contestadas (usamos como cantidad total de gestiones)
            contestadas = _obtener_valor_primera_columna(fila, indices_contestadas["Contestadas"])
            if contestadas is not None:
                datos["suma_contestadas"] += int(contestadas)
                datos["total_gestiones"] += int(contestadas)

            # AHT
            aht = _obtener_valor_primera_columna(fila, indices_aht["AHT"])
            if aht is not None:
                datos["suma_aht"] += aht
                datos["conteo_aht"] += 1

            # Ocupación
            ocupacion = _obtener_valor_primera_columna(fila, indices_ocupacion.get("% Ocupación", []))
            if ocupacion is None:
                ocupacion = _obtener_valor_primera_columna(
                    fila, indices_ocupacion.get("% Ocupacion", [])
                )
            if ocupacion is None:
                ocupacion = _obtener_valor_primera_columna(
                    fila, indices_ocupacion.get("Tiempo de Ocupación", [])
                )
            if ocupacion is None:
                ocupacion = _obtener_valor_primera_columna(
                    fila, indices_ocupacion.get("Tiempo de Ocupacion", [])
                )
            if ocupacion is not None:
                datos["suma_ocupacion"] += ocupacion
                datos["conteo_ocupacion"] += 1

        # Si encontramos datos, no necesitamos seguir buscando en otros archivos
        break

    # Calcular promedios y construir lista final
    asesores_lista: list[dict[str, Any]] = []
    total_gestiones_global = 0

    for asesor, datos in sorted(asesores_data.items()):
        aht_promedio = (
            round(datos["suma_aht"] / datos["conteo_aht"], 2)
            if datos["conteo_aht"] > 0
            else None
        )
        ocupacion_promedio = (
            round(datos["suma_ocupacion"] / datos["conteo_ocupacion"], 2)
            if datos["conteo_ocupacion"] > 0
            else None
        )

        # No hay forma de separar WhatsApp de Llamadas, así que ambos son None
        # y se reporta la limitación
        total_gestiones_global += datos["total_gestiones"]

        asesores_lista.append(
            {
                "asesor": datos["asesor"],
                "cantidad_whatsapp": None,
                "cantidad_llamadas": None,
                "tiempo_ocupacion": ocupacion_promedio,
                "aht": aht_promedio,
                "total_gestiones": datos["total_gestiones"],
                "filas_procesadas": datos["filas_procesadas"],
                "datos_disponibles": datos["filas_procesadas"] > 0,
                "columnas_faltantes": [],
            }
        )

    # Determinar columnas faltantes (no se puede separar WhatsApp vs Llamadas)
    columnas_faltantes_comunes = [
        "Columna para distinguir WhatsApp de Llamadas (subcanal)",
    ]

    for asesor in asesores_lista:
        asesor["columnas_faltantes"] = columnas_faltantes_comunes.copy()
        asesor["cantidad_whatsapp"] = None
        asesor["cantidad_llamadas"] = None

    resumen = {
        "total_asesores": len(asesores_lista),
        "total_gestiones_global": total_gestiones_global,
        "asesores_con_datos": sum(1 for a in asesores_lista if a["datos_disponibles"]),
    }

    return {
        "asesores": asesores_lista,
        "resumen": resumen,
        "archivo_usado": archivo_usado,
        "hoja_usada": hoja_usada,
        "nota_limitacion": (
            "No se pudo separar Cantidad WhatsApp de Cantidad Llamadas porque no hay "
            "columna que distinga el subcanal en los insumos. Ambos campos se dejan "
            "vacíos (sin inventar valores). Se reporta Total de gestiones, AHT y "
            "Tiempo de ocupación cuando están disponibles."
        ),
    }


def formatear_resultado_r5(resultado: dict[str, Any]) -> str:
    """Formatea el resultado de R5 como texto legible (Markdown)."""
    lineas: list[str] = []
    lineas.append("## R5 — Desempeño por asesor de WhatsApp")
    lineas.append("")
    lineas.append(
        "| Asesor | Cantidad WhatsApp | Cantidad Llamadas | Tiempo de Ocupación | AHT | Total Gestiones |"
    )
    lineas.append("|--------|-------------------|-------------------|---------------------|-----|-----------------|")

    for asesor in resultado["asesores"]:
        lineas.append(
            f"| {asesor['asesor']} | "
            f"{asesor['cantidad_whatsapp'] or '—'} | "
            f"{asesor['cantidad_llamadas'] or '—'} | "
            f"{asesor['tiempo_ocupacion'] or '—'} | "
            f"{asesor['aht'] or '—'} | "
            f"{asesor['total_gestiones'] or '—'} |"
        )

    lineas.append("")
    lineas.append("### Resumen")
    lineas.append(f"- Total asesores: {resultado['resumen']['total_asesores']}")
    lineas.append(f"- Asesores con datos: {resultado['resumen']['asesores_con_datos']}")
    lineas.append(f"- Total gestiones global: {resultado['resumen']['total_gestiones_global']}")
    lineas.append("")
    lineas.append(f"### Archivo y hoja utilizados")
    lineas.append(f"- Archivo: {resultado['archivo_usado'] or '—'}")
    lineas.append(f"- Hoja: {resultado['hoja_usada'] or '—'}")
    lineas.append("")
    lineas.append("### Limitación")
    lineas.append(resultado["nota_limitacion"])

    return "\n".join(lineas)


if __name__ == "__main__":
    ruta_insumos = os.path.join(os.path.dirname(__file__), "..", "..", "insumos")
    ruta_insumos = os.path.abspath(ruta_insumos)

    resultado = calcular_desempeño_asesor_whatsapp(ruta_insumos)
    print(formatear_resultado_r5(resultado))
