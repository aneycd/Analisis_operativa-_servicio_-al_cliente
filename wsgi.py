"""Punto de entrada para despliegue (WSGI).

Importa create_app y expone la aplicación como `app`.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
