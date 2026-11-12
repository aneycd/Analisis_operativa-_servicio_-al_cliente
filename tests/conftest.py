# tests/conftest.py
# Configuración de pytest: configura pythonpath para que pytest encuentre el paquete `app`.

import os
import sys

# Añadir la raíz del proyecto al path de Python para que se pueda importar `app`
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Ruta a la carpeta de insumos (usada por las pruebas de integración)
INSUMOS_DIR = os.path.join(ROOT_DIR, "insumos")
