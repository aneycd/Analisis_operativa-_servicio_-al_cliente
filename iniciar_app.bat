@echo off
cd /d "%~dp0"

:: Activa el entorno de uv y enciende la app Flask
uv run flask --app wsgi run --host 127.0.0.1 --port 5000

:: Abre el navegador en la URL local
start http://127.0.0.1:5000/
