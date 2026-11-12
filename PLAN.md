# PLAN.md — Plan de entregas del proyecto

## 1. RESUMEN (5 líneas)

Vamos a construir una app web de análisis operativo de servicio al cliente (Contact Center) de un banco. Entran los archivos de insumos de la carpeta `insumos/` (3 Excels: CHATBOT, llamadas y correos, WhatsApp) y el contexto de `contexto/Contexto_Mi_App.md`. El agente de IA recibe un contrato JSON con los datos de los insumos y devuelve el informe ejecutivo estructurado (métricas por canal, por buzón, por asesor). La app produce un informe ejecutivo en formato tablas/viñetas, listo para presentar a la alta dirección. Toda lógica de negocio es código rígido (sin IA); la IA solo formatea el informe según el contrato JSON.

---

## 2. LO QUE ENCONTRÉ

### Carpeta `contexto/`
- `Contexto_Mi_App.md` → ya existe (41 líneas). Contiene: rol de consultor senior, informe ejecutivo mensual, canales (Chatbot, llamadas, Correos, WhatsApp / CORI, Redes Sociales, PCI, Correos N), métricas (Cantidad Atendida, AHT, TR, Gestiones por Asesor), desglose de correos por buzón (Bienes adquiridos, Centro Asistencia N1, Centro Asistencia N2, Operativa CAC PCI, Servicio oficina virtual, Soporte CAC), matriz Asesor vs Buzón, desglose de WhatsApp por subcanal y por asesor, reglas estrictas (fidelidad absoluta, prohibición de invención, preguntar si falta dato), formato Markdown, tono profesional en español.
- `Proyecto análisis de operativo servicio al cliente.docx` → documento origen del contexto (no se modifica).

### Carpeta `insumos/` (solo lectura, nada modificado)
Tres archivos Excel inspeccionados:

| Archivo | Hojas detectadas | Filas de datos (aprox. por hoja principal) | Columnas principales observadas |
|---------|-----------------|-------------------------------------------|---------------------------------|
| `Control CHATBOT.xlsx` | Intervalos CORI, Chat, Vinculos | Chat: 50; Intervalos CORI: 54; Vinculos: 3 | Nivel, N1 |
| `Control llamadas y correos.xlsx` | Control Mensual, Control Diario, Control Intervalo, Control Auxiliares, Control Agentes, %Ocupación por intervalo, Vinculos | Vinculos: 533; Control Diario: 33; Control Intervalo: 67 | Entrantes, Contestadas, Abandonadas, AHT, % Service Level, Tasa de Respuesta, Llamadas Salientes, Correos, Correos Empresas, Contracargos, Nombre, Nivel, AgentLogin, Application |
| `Control WhatsApp.xlsx` | Control Agentes, Whatsapp, Diario agentes(REDES), Vinculos | Whatsapp: 37; Vinculos: 533; Diario agentes(REDES): 30 | Entrantes, Contestadas, Abandonadas, AHT, % Service Level, Tasa de Respuesta, Llamadas Salientes, Correos, Correos Empresas, Contracargos, Nivel, Grupo, Agente |

### Comparación con `AGENTS.md`
- **`AGENTS.md` no existe todavía** en la raíz del proyecto. No puede compararse.
- El contexto menciona canales "Chatbot, llamadas, Correos, WhatsApp" (original) y "CORI, Redes Sociales, PCI, Correos N" (mejorado). **No está mapeado qué archivo de insumo corresponde a cada canal.**
- El contexto menciona buzones de correos (Bienes adquiridos, Centro Asistencia N1, Centro Asistencia N2, Operativa CAC PCI, Servicio oficina virtual, Soporte CAC). **No se ha confirmado que existan como columnas en los insumos.**
- En los insumos aparece la columna "Nivel" con valores como N1, N2, PCI, Redes — **no está claro si mapea directamente a los canales del contexto.**

### Qué falta o no cuadra (pendiente de confirmar — PREGUNTAS PARA MÍ, sección 6)
1. `AGENTS.md` no existe (es el paso 4 del encargo original, aún pendiente).
2. Mapeo canal ↔ archivo de insumo.
3. Existencia de columnas de buzones de correos en los insumos.
4. Qué llave de IA y proveedor se usarán (variable de entorno en `.env`).
5. Formato de salida del informe (Markdown, PDF, HTML, solo pantalla web).

---

## 3. ENTREGAS POR SUBAGENTE

Orden de ejecución: @arquitecto → @backend → @frontend → @tester → @revisor.

| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 1 | @arquitecto | `PLAN.md` con los 6 bloques (datos, lógica, agente IA, pantallas, salida, puntos de control, riesgos, preguntas) | `PLAN.md` (raíz) | Contexto, insumos, AGENTS.md (si existe) | Abrir `PLAN.md` y confirmar que tiene las 6 secciones y la tabla de entregas |
| 2 | @backend | Estructura MVC base con `uv`: `app/__init__.py` con `create_app()`, `app/controllers/`, `app/services/`, `wsgi.py`, `iniciar_app.bat`, `.env` con llave de IA | `app/__init__.py`, `app/controllers/`, `app/services/`, `wsgi.py`, `iniciar_app.bat`, `.env`, `pyproject.toml` | Entrega 1 (`PLAN.md` aprobado) | Ejecutar `iniciar_app.bat`, abrir navegador, app responde sin error 500 |
| 3 | @backend | Lectura de insumos: función que lee cada Excel y devuelve columnas + número de filas (solo lectura, sin escribir en insumos) | `app/services/lectura_insumos.py` | Entrega 2 (app funcionando) | Ejecutar script de lectura, ver columnas y conteo de filas por archivo en consola |
| 4 | @backend | Regla de negocio R1: métricas globales por canal (Cantidad Atendida, AHT, TR, Gestiones por Asesor) para los 4 canales | `app/services/regla_r1_metricas_canal.py` | Entrega 3 (datos crudos cargados) | Ejecutar R1, ver tabla con 4 canales y sus 4 métricas en pantalla |
| 5 | @backend | Regla de negocio R2: desglose de correos por buzón (6 buzones del contexto) | `app/services/regla_r2_correos_buzon.py` | Entrega 4 | Ejecutar R2, ver tabla con los 6 buzones y sus cantidades |
| 6 | @backend | Regla de negocio R3: matriz Asesor vs Buzón de correos | `app/services/regla_r3_matriz_asesor_buzon.py` | Entrega 5 | Ejecutar R3, ver tabla cruzada asesor × buzón |
| 7 | @backend | Regla de negocio R4: desglose WhatsApp por subcanal (WhatsApp y Llamadas por separado: Atendidas, AHT, TR) | `app/services/regla_r4_whatsapp_subcanal.py` | Entrega 6 | Ejecutar R4, ver 2 subcanales con sus 3 métricas cada uno |
| 8 | @backend | Regla de negocio R5: desempeño por asesor de WhatsApp (Cantidad WhatsApp, Llamadas, Tiempo de ocupación, AHT, Total) | `app/services/regla_r5_whatsapp_asesor.py` | Entrega 7 | Ejecutar R5, ver tabla por asesor con las 5 columnas |
| 9 | @backend | Integración agente de IA: contrato JSON de entrada/salida, llave leída de `.env` | `app/services/agente_ia.py`, `.env` | Entregas 4-8 (reglas de negocio listas) | Enviar JSON de prueba, recibir respuesta JSON válida |
| 10 | @backend | Descarga de resultados: endpoint para exportar el informe (Markdown) | `app/controllers/export.py` | Entrega 9 | Hacer clic en descargar, recibir archivo con el informe |
| 11 | @frontend | Pantalla de inicio: carga/selección de insumos, botón ejecutar análisis | `app/templates/inicio.html`, `app/static/` (CSS) | Entrega 10 (endpoints listos) | Abrir `/`, ver formulario en español, fondo oscuro, botón ejecutar |
| 12 | @frontend | Pantalla de resultados: tablero con contadores grandes (Cantidad Atendida, AHT, TR, Gestiones por Asesor) y tablas con filtro | `app/templates/resultados.html`, `app/static/` | Entrega 11 | Ver contadores grandes y tabla con filtro funcional (escribir filtra filas) |
| 13 | @frontend | Detalle por registro: vista expandida de cada registro/asesor | `app/templates/detalle.html` (o sección en resultados) | Entrega 12 | Hacer clic en una fila, ver detalle del registro |
| 14 | @tester | Pruebas en `tests/` con pytest contra cifras de control y casos límite de `AGENTS.md` | `tests/test_*.py`, `pytest.ini`/`conftest.py` | Entregas 4-8 (reglas de negocio) | Ejecutar `pytest`, ver tests pasados/fallados |
| 15 | @tester | `VALIDACION.md` con esperado vs obtenido por cada prueba | `VALIDACION.md` (raíz) | Entrega 14 | Abrir `VALIDACION.md`, ver tabla esperado vs obtenido |
| 16 | @revisor | Revisión de seguridad: llaves en `.env`, no hardcodeadas, datos sensibles, `.gitignore` | Reporte de hallazgos (pantalla o archivo `.md`) | Entrega 16 | Leer reporte de hallazgos con prioridad y corrección propuesta |
| 17 | @revisor | Revisión de que todo esté en `AGENTS.md` (ninguna regla/columna/archivo inventado) | Reporte de hallazgos | Entrega 16 | Leer reporte, confirmar que todo cuadra con `AGENTS.md` |

---

## 4. PUNTOS DE CONTROL

Después de qué entrega interviene `@tester`, y qué cifra o resultado exacto debe ver el usuario en pantalla:

| Punto de control | Después de entrega | Qué debe ver el usuario en pantalla |
|------------------|--------------------|-------------------------------------|
| PC1 | Entrega 2 (estructura MVC) | Navegador abre en `http://127.0.0.1:5000/` o similar, app responde sin error 500 |
| PC2 | Entrega 3 (lectura insumos) | Consola imprime: nombre de cada Excel, columnas detectadas, número de filas de datos |
| PC3 | Entrega 4 (R1 métricas canal) | Tabla con 4 filas (canales) y columnas: Cantidad Atendida, AHT, TR, Gestiones por Asesor |
| PC4 | Entrega 5 (R2 correos buzón) | Tabla con 6 filas (buzones: Bienes adquiridos, Centro Asistencia N1, Centro Asistencia N2, Operativa CAC PCI, Servicio oficina virtual, Soporte CAC) |
| PC5 | Entrega 7 (R4 WhatsApp subcanal) | 2 filas: WhatsApp y Llamadas, cada una con Atendidas, AHT, TR |
| PC6 | Entrega 9 (agente IA) | Respuesta JSON válida (no texto suelto), con las claves del contrato definido en AGENTS.md |
| PC7 | Entrega 12 (resultados frontend) | Contadores grandes visibles y tabla con filtro funcional (escribir en el filtro filtra filas) |
| PC8 | Entrega 15 (VALIDACION.md) | Tabla esperado vs obtenido, con diferencias marcadas y causa probable |

---

## 5. RIESGOS

| Riesgo | Qué hará cada subagente si pasa |
|--------|---------------------------------|
| Datos incompletos (falta columna o fila en insumos) | @backend: detiene esa regla, devuelve error claro indicando qué dato falta. @tester: marca el test como fallado con causa "dato faltante en insumo". No se inventa nada. |
| Archivo escaneado (PDF sin texto) | No aplica aquí (todos son Excel). Si en el futuro hay PDFs escaneados, @backend reporta que no se puede extraer texto y pide el archivo en otro formato. |
| Respuesta del agente de IA que no es JSON | @backend: valida que la respuesta sea JSON parseable; si no, reintenta una vez y si falla devuelve error estructurado. Nunca se usa texto no-JSON como dato. |
| Límite de la llave gratis de IA | @backend: controla el consumo, avisa cuando se acerca al límite, y @revisor verifica que la llave esté solo en `.env` y no en código. |
| Contradicción entre contexto e insumos | @arquitecto: lo anota en `PLAN.md` como "PREGUNTA PARA EL USUARIO" y no avanza hasta que se resuelva. |
| Falta `AGENTS.md` para comparar | @arquitecto: marca como bloqueador. @revisor: no puede validar que todo esté en `AGENTS.md` si no existe. |
| Columnas de buzones no existen en insumos | @backend: reporta que faltan las columnas de buzones y no puede calcular R2/R3 sin ellas. @arquitecto: lo sube a preguntas para el usuario. |

---

## 6. PREGUNTAS PARA MÍ

Antes de empezar a construir, necesito que confirme:

1. **¿Existe o debo crear `AGENTS.md`?** El encargo original pedía crearlo, pero luego se dijo "no crees ningún otro archivo todavía". ¿Lo creo ahora como parte del plan, o espero a que me lo pida explícitamente?
2. **¿Cuál es el nombre canónico de cada canal y qué archivo de insumo corresponde a cada uno?** El contexto mezcla "Chatbot, llamadas, Correos, WhatsApp" con "CORI, Redes Sociales, PCI, Correos N". ¿`Control CHATBOT.xlsx` es Chatbot/CORI, `Control llamadas y correos.xlsx` es llamadas/Correos/PCI, `Control WhatsApp.xlsx` es WhatsApp/Redes Sociales?
3. **¿Los buzones de correos del contexto (Bienes adquiridos, Centro Asistencia N1, Centro Asistencia N2, Operativa CAC PCI, Servicio oficina virtual, Soporte CAC) existen como columnas en los insumos?** Si no, ¿qué columnas usan realmente para los buzones?
4. **¿Qué llave de IA se usa?** ¿Proveedor (OpenAI, Anthropic, otro) y nombre de la variable de entorno en `.env`?
5. **¿Formato de salida del informe?** ¿Markdown, PDF, HTML, o solo pantalla web?

Quedo a la espera de su aprobación de la tabla de entregas y de las respuestas a estas preguntas antes de que cualquier subagente comience a construir.
