"""Blueprint principal de la aplicación.

Define las rutas y endpoints Flask. Reciben peticiones,
llaman a los servicios y devuelven respuestas (JSON o templates renderizados).
"""

from flask import Blueprint

main_bp = Blueprint("main", __name__)

from app.controllers import routes  # noqa: E402, F401, WPS433
from app.controllers import export  # noqa: E402, F401, WPS433
