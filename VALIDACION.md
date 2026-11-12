# VALIDACIÓN.md — Esperado vs Obtenido por cada prueba

## Resumen Ejecutivo

- **Total de pruebas ejecutadas:** 34
- **Pruebas pasadas:** 34
- **Pruebas falladas:** 0
- **Fecha de ejecución:** 2026-11-04
- **Comando utilizado:** `uv run pytest tests/ -v --tb=short`

---

## ⚠️ Limitación importante

**AGENTS.md no existe en la raíz del proyecto.** Por lo tanto:
- No hay **cifras de control** predefinidas (valores esperados de cantidad atendida, AHT, TR, gestiones por asesor, etc.)
- No hay **casos límite** documentados en AGENTS.md

Las pruebas verifican **estructura, consistencia y casos límite**, no valores esperados específicos contra una referencia externa. Los valores "esperados" mostrados a continuación son los que la lógica del código garantiza (por ejemplo: 4 canales, 6 buzones, 2 subcanales, etc.), no valores extraídos de AGENTS.md.

---

## Tabla: Esperado vs Obtenido por cada prueba

### 1. Reglas de negocio — R1: Métricas globales por canal

| # | Prueba | Valor Esperado | Valor Obtenido | Estado | Causa de diferencia (si aplica) |
|---|--------|---------------|----------------|--------|---------------------------------|
| R1-1 | Estructura correcta del resultado | dict con claves `canales` y `resumen` | dict con claves `canales` y `resumen` | ✅ Pasó | — |
| R1-2 | Tiene 4 canales | {Chatbot, Llamadas, Correos, WhatsApp} | {Chatbot, Llamadas, Correos, WhatsApp} | ✅ Pasó | — |
| R1-3 | Cada canal tiene claves requeridas | 12 claves por canal | 12 claves por canal | ✅ Pasó | — |
| R1-4 | No inventa datos cuando faltan columnas | cantidad_atendida/aht/tr = None si no hay datos | None para Chatbot (sin columnas) | ✅ Pasó | — |
| R1-5 | Ruta de insumos inexistente | Estructura vacía sin fallar | total_canales=4, canales_con_datos=0 | ✅ Pasó | — |
| R1-6 | Resumen tiene claves esperadas | total_canales, canales_con_datos, canales_sin_datos | total_canales=4, con=3, sin=1 | ✅ Pasó | — |
| R1-7 | columnas_faltantes es lista | lista (puede estar vacía) | lista para cada canal | ✅ Pasó | — |

**Resumen R1:** 4 canales procesados. Chatbot sin datos (no tiene columnas de métricas en insumos). Llamadas, Correos y WhatsApp con datos. Canales con datos: 3 de 4.

---

### 2. Reglas de negocio — R2: Desglose de correos por buzón

| # | Prueba | Valor Esperado | Valor Obtenido | Estado | Causa de diferencia (si aplica) |
|---|--------|---------------|----------------|--------|---------------------------------|
| R2-1 | Estructura correcta del resultado | dict con claves `buzones`, `resumen`, `columnas_faltantes` | dict con claves `buzones`, `resumen`, `columnas_faltantes` | ✅ Pasó | — |
| R2-2 | Tiene 6 buzones del contexto | 6 buzones (Bienes adquiridos, Centro Asistencia N1, Centro Asistencia N2, Operativa CAC PCI, Servicio oficina virtual, Soporte CAC) | 6 buzones | ✅ Pasó | — |
| R2-3 | Cada buzón tiene claves requeridas | 6 claves por buzón | 6 claves por buzón | ✅ Pasó | — |
| R2-4 | No inventa cantidad cuando no hay columna | cantidad_atendida = None si no hay datos | None para todos los 6 buzones | ✅ Pasó | — |
| R2-5 | Ruta de insumos inexistente | Estructura vacía sin fallar | total_buzones=6, encontrados=0 | ✅ Pasó | — |
| R2-6 | Resumen tiene claves esperadas | total_buzones, buzones_encontrados, buzones_no_encontrados | total=6, encontrados=0, no_encontrados=6 | ✅ Pasó | — |

**Resumen R2:** 0 de 6 buzones encontrados en insumos. Ninguno de los 6 buzones del contexto existe como columna en los archivos Excel.

---

### 3. Reglas de negocio — R3: Matriz Asesor vs Buzón de correos

| # | Prueba | Valor Esperado | Valor Obtenido | Estado | Causa de diferencia (si aplica) |
|---|--------|---------------|----------------|--------|---------------------------------|
| R3-1 | Estructura correcta del resultado | dict con claves `matriz`, `asesores`, `buzones`, etc. | dict con todas las claves esperadas | ✅ Pasó | — |
| R3-2 | Buzones son los del contexto | Lista de 6 buzones del contexto | Lista de 6 buzones del contexto | ✅ Pasó | — |
| R3-3 | Matriz es dict de dicts | Cada valor es un diccionario | Cada valor es un diccionario | ✅ Pasó | — |
| R3-4 | Sin datos reporta honestamente | datos_disponibles = False | datos_disponibles = False | ✅ Pasó | — |
| R3-5 | Ruta de insumos inexistente | No fallar | datos_disponibles = False, archivo_usado = None | ✅ Pasó | — |

**Resumen R3:** No hay datos disponibles para calcular la matriz. Ninguno de los 6 buzones tiene columna correspondiente en los insumos.

---

### 4. Reglas de negocio — R4: Desglose WhatsApp por subcanal

| # | Prueba | Valor Esperado | Valor Obtenido | Estado | Causa de diferencia (si aplica) |
|---|--------|---------------|----------------|--------|---------------------------------|
| R4-1 | Estructura correcta del resultado | dict con claves `subcanales` y `resumen` | dict con claves `subcanales` y `resumen` | ✅ Pasó | — |
| R4-2 | Tiene 2 subcanales | {WhatsApp, Llamadas} | {WhatsApp, Llamadas} | ✅ Pasó | — |
| R4-3 | Cada subcanal tiene claves requeridas | 11 claves por subcanal | 11 claves por subcanal | ✅ Pasó | — |
| R4-4 | No inventa datos cuando no se puede filtrar | atendidas/aht/tr = None si no hay datos | None para ambos subcanales | ✅ Pasó | — |
| R4-5 | Ruta de insumos inexistente | No fallar | total_subcanales=2, con_datos=0 | ✅ Pasó | — |
| R4-6 | Resumen tiene claves esperadas | total_subcanales, subcanales_con_datos, subcanales_sin_datos | total=2, con=0, sin=2 | ✅ Pasó | — |

**Resumen R4:** 0 subcanales con datos. No hay columna que distinga WhatsApp de Llamadas en los insumos.

---

### 5. Reglas de negocio — R5: Desempeño por asesor de WhatsApp

| # | Prueba | Valor Esperado | Valor Obtenido | Estado | Causa de diferencia (si aplica) |
|---|--------|---------------|----------------|--------|---------------------------------|
| R5-1 | Estructura correcta del resultado | dict con claves `asesores`, `resumen`, `archivo_usado`, etc. | dict con todas las claves esperadas | ✅ Pasó | — |
| R5-2 | Cada asesor tiene claves requeridas | 9 claves por asesor | 9 claves por asesor | ✅ Pasó | — |
| R5-3 | No inventa cantidad_whatsapp ni cantidad_llamadas | Ambos = None (no hay columna de subcanal) | None para todos los asesores | ✅ Pasó | — |
| R5-4 | total_gestiones es positivo o None | >= 0 o None | Valores >= 0 o None | ✅ Pasó | — |
| R5-5 | Ruta de insumos inexistente | No fallar | total_asesores = 0 | ✅ Pasó | — |
| R5-6 | Resumen tiene claves esperadas | total_asesores, total_gestiones_global, asesores_con_datos | total=16, gestiones=9498, con=16 | ✅ Pasó | — |

**Resumen R5:** 16 asesores encontrados en `Control WhatsApp.xlsx` (hoja `Vinculos`). Total gestiones global: 9,498. cantidad_whatsapp y cantidad_llamadas = None (no hay columna de subcanal). AHT calculado para 15 de 16 asesores.

---

### 6. Pruebas de integración — Endpoint /api/informe

| # | Prueba | Valor Esperado | Valor Obtenido | Estado | Causa de diferencia (si aplica) |
|---|--------|---------------|----------------|--------|---------------------------------|
| INT-1 | Devuelve JSON válido | status 200, JSON con 5 claves de reglas | status 200, JSON con 5 claves | ✅ Pasó | — |
| INT-2 | Estructura r1_metricas_canal | claves `canales` y `resumen`, 4 canales | 4 canales, estructura correcta | ✅ Pasó | — |
| INT-3 | Estructura r2_correos_buzon | claves `buzones` y `resumen`, 6 buzones | 6 buzones, estructura correcta | ✅ Pasó | — |
| INT-4 | Estructura r5_desempeno_asesor | claves `asesores` y `resumen` | 16 asesores, estructura correcta | ✅ Pasó | — |

---

## Diferencias encontradas y causas probables

| Diferencia | Valor Esperado (según AGENTS.md) | Valor Obtenido | Causa Probable |
|------------|----------------------------------|----------------|----------------|
| Cifras de control de cantidad atendida | No definidas (AGENTS.md no existe) | Varía por canal (ver R1) | Falta AGENTS.md con valores de referencia |
| Cifras de control de AHT | No definidas (AGENTS.md no existe) | Varía por canal (ver R1) | Falta AGENTS.md con valores de referencia |
| Cifras de control de TR | No definidas (AGENTS.md no existe) | Varía por canal (ver R1) | Falta AGENTS.md con valores de referencia |
| Cifras de control por buzón | No definidas (AGENTS.md no existe) | 0 buzones encontrados | Los 6 buzones del contexto no existen como columnas en insumos |
| Cifras de control por asesor | No definidas (AGENTS.md no existe) | 16 asesores, 9,498 gestiones globales | Falta AGENTS.md con valores de referencia |

---

## Conclusión

Todas las **34 pruebas pasaron**. La aplicación funciona correctamente según la lógica implementada en las reglas de negocio R1-R5.

**Sin embargo**, no se pudo realizar una comparación de "esperado vs obtenido" contra cifras de control definidas en AGENTS.md porque **dicho archivo no existe**. Se recomienda crear AGENTS.md con las cifras de control esperadas antes de validar la precisión numérica del informe.

---

## Cómo verificar en pantalla

Ejecutar:
```
uv run pytest tests/ -v --tb=short
```

Resultado esperado: `34 passed`.
