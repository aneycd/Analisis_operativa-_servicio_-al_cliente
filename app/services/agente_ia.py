"""Integración del agente de IA con contrato JSON.

Recibe un contrato JSON de entrada con los datos de los insumos y las reglas
de negocio (R1-R5), llama a una IA usando la llave de `.env`, y devuelve un
contrato JSON de salida con el informe ejecutivo estructurado.

La lógica de negocio (cálculos) es código rígido (R1-R5); el agente de IA solo
formatea y estructura el informe según el contrato JSON.

La llave de IA se lee de la variable de entorno `IA_API_KEY` definida en `.env`.
Nunca se hardcodea.
"""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

IA_API_KEY = os.environ.get("IA_API_KEY", "")

# Contrato JSON de entrada (claves esperadas)
CONTRATO_ENTRADA_CLAVES = [
    "canales",           # resultado de R1
    "buzones",           # resultado de R2
    "matriz_asesor_buzon",  # resultado de R3
    "subcanales_whatsapp",  # resultado de R4
    "desempeno_asesores",   # resultado de R5
    "metadata",          # información adicional (archivo, fecha, etc.)
]

# Contrato JSON de salida (claves que el agente debe devolver)
CONTRATO_SALIDA_CLAVES = [
    "informe_ejecutivo",   # texto del informe en Markdown
    "metricas_globales",   # métricas por canal
    "detalle_correos",     # desglose por buzón
    "desempeño_asesores",  # desempeño por asesor
    "alertas",             # advertencias de datos faltantes
    "version",             # versión del contrato de salida
]


def validar_entrada(entrada: dict[str, Any]) -> tuple[bool, str | None]:
    """Valida que el JSON de entrada tenga las claves mínimas del contrato.

    Args:
        entrada: diccionario con los datos de entrada

    Returns:
        (es_valido, mensaje_error) donde mensaje_error es None si es válido.
    """
    if not isinstance(entrada, dict):
        return False, "La entrada debe ser un objeto JSON (dict)."

    claves_faltantes = [c for c in CONTRATO_ENTRADA_CLAVES if c not in entrada]
    if claves_faltantes:
        return False, (
            "Faltan claves requeridas en el contrato de entrada: "
            + ", ".join(claves_faltantes)
        )

    return True, None


def validar_salida(salida: dict[str, Any]) -> tuple[bool, str | None]:
    """Valida que el JSON de salida tenga las claves esperadas del contrato.

    Args:
        salida: diccionario con los datos de salida de la IA

    Returns:
        (es_valido, mensaje_error) donde mensaje_error es None si es válido.
    """
    if not isinstance(salida, dict):
        return False, "La salida debe ser un objeto JSON (dict)."

    claves_faltantes = [c for c in CONTRATO_SALIDA_CLAVES if c not in salida]
    if claves_faltantes:
        return False, (
            "Faltan claves requeridas en el contrato de salida: "
            + ", ".join(claves_faltantes)
        )

    return True, None


def construir_prompt(entrada: dict[str, Any]) -> str:
    """Construye el prompt para el agente de IA a partir del contrato de entrada.

    El prompt instruye a la IA para que formatee un informe ejecutivo en español
    usando únicamente los datos proporcionados, sin inventar valores.
    """
    partes: list[str] = []
    partes.append(
        "Eres un consultor senior de Contact Centers. Recibes datos de reglas de "
        "negocio (R1-R5) de una app de análisis operativo de servicio al cliente "
        "de un banco. Tu tarea es formatear un informe ejecutivo en Markdown, en "
        "español, usando ÚNICAMENTE los datos proporcionados. No inventes, no "
        "infieras y no asumas valores faltantes. Si un dato no está disponible, "
        "indícalo explícitamente."
    )
    partes.append("")
    partes.append("## Datos de entrada (reglas de negocio R1-R5):")
    partes.append(json.dumps(entrada, ensure_ascii=False, indent=2))
    partes.append("")
    partes.append("## Formato de salida esperado (JSON):")
    ejemplo_salida = {
        "informe_ejecutivo": "Texto en Markdown con tablas y viñetas",
        "metricas_globales": {"canal": "WhatsApp", "atendidas": 100, "aht": 150.5, "tr": 0.85},
        "detalle_correos": {"buzon": "Bienes adquiridos", "cantidad": 50},
        "desempeño_asesores": {"asesor": "Juan Pérez", "total_gestiones": 200},
        "alertas": ["lista de advertencias de datos faltantes"],
        "version": "1.0",
    }
    partes.append(json.dumps(ejemplo_salida, ensure_ascii=False, indent=2))
    partes.append("")
    partes.append("Responde ÚNICAMENTE con JSON válido. No agregues texto antes o después.")

    return "\n".join(partes)


def llamar_ia(prompt: str) -> str | None:
    """Llama a la API de IA con el prompt dado.

    Esta es una implementación genérica. El proveedor concreto (OpenAI, Anthropic,
    otro) y el endpoint exacto dependen de la configuración del proyecto y deben
    confirmarse (ver pregunta 4 de PLAN.md sección 6).

    Lee la llave de `IA_API_KEY` del entorno (.env).

    Args:
        prompt: texto del prompt a enviar

    Returns:
        Texto de respuesta de la IA, o None si falló.
    """
    if not IA_API_KEY:
        return None

    # Placeholder: aquí se integraría el cliente del proveedor de IA.
    # Ejemplo estructurado (sin hardcodear proveedor específico):
    #   import openai  # o anthropic, etc.
    #   client = openai.OpenAI(api_key=IA_API_KEY)
    #   respuesta = client.chat.completions.create(...)
    #   return respuesta.choices[0].message.content

    return None


def procesar_con_agente_ia(entrada: dict[str, Any]) -> dict[str, Any]:
    """Procesa los datos de entrada a través del agente de IA.

    Args:
        entrada: diccionario con el contrato de entrada

    Returns:
        Diccionario con el contrato de salida (JSON válido) o un error estructurado.
    """
    # Validar entrada
    es_valida, error = validar_entrada(entrada)
    if not es_valida:
        return {
            "error": True,
            "codigo": "ENTRADA_INVALIDA",
            "mensaje": error,
            "version": "1.0",
        }

    # Verificar que hay llave de IA
    if not IA_API_KEY:
        return {
            "error": True,
            "codigo": "IA_API_KEY_NO_CONFIGURADA",
            "mensaje": (
                "La variable de entorno IA_API_KEY no está configurada en .env. "
                "Configúrala antes de usar el agente de IA."
            ),
            "version": "1.0",
        }

    # Construir prompt
    prompt = construir_prompt(entrada)

    # Llamar a la IA (con un reintento si la respuesta no es JSON válido)
    respuesta_texto = llamar_ia(prompt)
    if respuesta_texto is None:
        return {
            "error": True,
            "codigo": "IA_NO_DISPONIBLE",
            "mensaje": (
                "No se pudo obtener respuesta de la IA. Verifica que IA_API_KEY "
                "esté configurada y que el proveedor de IA esté disponible."
            ),
            "version": "1.0",
        }

    # Intentar parsear como JSON
    for intento in range(2):
        try:
            salida = json.loads(respuesta_texto)
        except (json.JSONDecodeError, TypeError):
            if intento == 0:
                # Reintentar una vez: pedir a la IA que devuelva JSON válido
                respuesta_texto = llamar_ia(
                    prompt + "\n\nERROR: La respuesta anterior no fue JSON válido. "
                    "Devuelve ÚNICAMENTE un objeto JSON válido, sin texto adicional."
                )
                if respuesta_texto is None:
                    break
                continue
            return {
                "error": True,
                "codigo": "RESPUESTA_NO_JSON",
                "mensaje": (
                    "La respuesta del agente de IA no es un JSON parseable tras "
                    "un reintento. No se usa texto no-JSON como dato."
                ),
                "version": "1.0",
            }

        # Validar contrato de salida
        es_valida, error = validar_salida(salida)
        if es_valida:
            salida["error"] = False
            salida["version"] = "1.0"
            return salida

        # Si falló la validación, reintentar una vez
        if intento == 0:
            respuesta_texto = llamar_ia(
                prompt + f"\n\nERROR: La respuesta no cumple el contrato de salida. "
                f"Faltan claves: {error}. Devuelve JSON válido con todas las claves "
                f"requeridas: {', '.join(CONTRATO_SALIDA_CLAVES)}."
            )
            if respuesta_texto is None:
                break
            continue

        return {
            "error": True,
            "codigo": "CONTRATO_SALIDA_INVALIDO",
            "mensaje": error,
            "version": "1.0",
        }

    return {
        "error": True,
        "codigo": "IA_RESPUESTA_VACIA",
        "mensaje": "La IA no devolvió respuesta válida.",
        "version": "1.0",
    }


if __name__ == "__main__":
    # Ejemplo de uso con contrato de entrada mínimo
    entrada_ejemplo = {
        "canales": [],
        "buzones": [],
        "matriz_asesor_buzon": {},
        "subcanales_whatsapp": [],
        "desempeno_asesores": [],
        "metadata": {"archivo": "ejemplo", "fecha": "2026-11-04"},
    }

    resultado = procesar_con_agente_ia(entrada_ejemplo)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
