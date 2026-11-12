"""Controlador de exportación de resultados.

Endpoint para exportar el informe ejecutivo en formato Markdown.
Ejecutar las reglas de negocio (R1-R5) y generar el archivo descargable.
"""

from flask import Blueprint, jsonify, make_response

from app.services.regla_r1_metricas_canal import (
    calcular_metricas_por_canal,
    formatear_resultado_r1,
)
from app.services.regla_r2_correos_buzon import (
    calcular_correos_por_buzon,
    formatear_resultado_r2,
)
from app.services.regla_r3_matriz_asesor_buzon import (
    calcular_matriz_asesor_buzon,
    formatear_resultado_r3,
)
from app.services.regla_r4_whatsapp_subcanal import (
    calcular_whatsapp_por_subcanal,
    formatear_resultado_r4,
)
from app.services.regla_r5_whatsapp_asesor import (
    calcular_desempeño_asesor_whatsapp,
    formatear_resultado_r5,
)

export_bp = Blueprint("export", __name__)


def _obtener_ruta_insumos() -> str:
    """Devuelve la ruta absoluta a la carpeta de insumos."""
    import os

    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "insumos")
    )


@export_bp.route("/exportar_informe", methods=["GET"])
def exportar_informe():
    """Genera y devuelve el informe ejecutivo en formato Markdown.

    Ejecuta las reglas de negocio R1-R5 sobre los archivos de insumos
    y devuelve el resultado como archivo Markdown descargable.

    Returns:
        Respuesta Flask con el contenido Markdown y headers de descarga.
    """
    ruta_insumos = _obtener_ruta_insumos()

    # Ejecutar reglas de negocio
    resultado_r1 = calcular_metricas_por_canal(ruta_insumos)
    resultado_r2 = calcular_correos_por_buzon(ruta_insumos)
    resultado_r3 = calcular_matriz_asesor_buzon(ruta_insumos)
    resultado_r4 = calcular_whatsapp_por_subcanal(ruta_insumos)
    resultado_r5 = calcular_desempeño_asesor_whatsapp(ruta_insumos)

    # Generar informe Markdown
    lineas: list[str] = []
    lineas.append("# Informe Ejecutivo Mensual de Operaciones")
    lineas.append("")
    lineas.append(
        "Contact Center - Servicio al Cliente\n"
        "Generado automáticamente por la app de análisis operativo.\n"
    )
    lineas.append("---")
    lineas.append("")

    # R1: Métricas globales por canal
    lineas.append(formatear_resultado_r1(resultado_r1))
    lineas.append("")
    lineas.append("---")
    lineas.append("")

    # R2: Desglose de correos por buzón
    lineas.append(formatear_resultado_r2(resultado_r2))
    lineas.append("")
    lineas.append("---")
    lineas.append("")

    # R3: Matriz Asesor vs Buzón
    lineas.append(formatear_resultado_r3(resultado_r3))
    lineas.append("")
    lineas.append("---")
    lineas.append("")

    # R4: Desglose WhatsApp por subcanal
    lineas.append(formatear_resultado_r4(resultado_r4))
    lineas.append("")
    lineas.append("---")
    lineas.append("")

    # R5: Desempeño por asesor
    lineas.append(formatear_resultado_r5(resultado_r5))
    lineas.append("")
    lineas.append("---")
    lineas.append("")

    # Nota final sobre datos faltantes
    lineas.append("## Nota sobre datos faltantes")
    lineas.append("")
    lineas.append(
        "Este informe se generó exclusivamente con los datos presentes en los "
        "archivos de insumos. No se inventaron, infirieron ni asumieron valores "
        "faltantes. Si algún dato o indicador requerido no aparece en los archivos "
        "entregados, se indicó explícitamente en las secciones correspondientes."
    )
    lineas.append("")

    contenido_md = "\n".join(lineas)

    # Crear respuesta con headers de descarga
    response = make_response(contenido_md)
    response.headers["Content-Type"] = "text/markdown; charset=utf-8"
    response.headers[
        "Content-Disposition"
    ] = 'attachment; filename="Informe_Ejecutivo_Mensual.md"'

    return response


@export_bp.route("/api/informe", methods=["GET"])
def api_informe():
    """Devuelve el informe ejecutivo en formato JSON.

    Útil para el agente de IA o para consumo por frontend.
    """
    ruta_insumos = _obtener_ruta_insumos()

    resultado_r1 = calcular_metricas_por_canal(ruta_insumos)
    resultado_r2 = calcular_correos_por_buzon(ruta_insumos)
    resultado_r3 = calcular_matriz_asesor_buzon(ruta_insumos)
    resultado_r4 = calcular_whatsapp_por_subcanal(ruta_insumos)
    resultado_r5 = calcular_desempeño_asesor_whatsapp(ruta_insumos)

    return jsonify(
        {
            "r1_metricas_canal": resultado_r1,
            "r2_correos_buzon": resultado_r2,
            "r3_matriz_asesor_buzon": resultado_r3,
            "r4_whatsapp_subcanal": resultado_r4,
            "r5_desempeno_asesor": resultado_r5,
        }
    )
