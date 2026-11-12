"""Factory de la aplicación Flask.

define create_app() que registra blueprints/controllers,
carga configuración y inicializa extensiones.
"""

import os

from flask import Flask


def create_app():
    """Crea y configura la instancia de la aplicación Flask."""
    app = Flask(__name__, instance_relative_config=True)

    # Configuración base. Los secretos se leen del entorno (.env),
    # nunca se hardcodean aquí.
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        IA_API_KEY=os.environ.get("IA_API_KEY", ""),
    )

    # Registrar blueprints / controllers
    from app.controllers import main_bp  # noqa: WPS433
    app.register_blueprint(main_bp)

    from app.controllers.export import export_bp  # noqa: WPS433
    app.register_blueprint(export_bp)

    return app
