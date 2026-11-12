"""Rutas principales de la aplicación.

Endpoints:
  - GET /   : pantalla de inicio
  - GET /health : estado de la aplicación (JSON)
"""

from flask import jsonify, render_template

from app.controllers import main_bp


@main_bp.route("/")
def inicio():
    """Pantalla de inicio de la app."""
    return render_template("inicio.html")


@main_bp.route("/health")
def health():
    """Endpoint de salud de la aplicación."""
    return jsonify(
        {
            "status": "ok",
            "app": "analisis-operativo-servicio-al-cliente",
        }
    )
