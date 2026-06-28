# En blueprintapp/main/__init__.py
from flask import Blueprint

# Cambiamos la ruta para que busque dentro de 'templates'
main_bp = Blueprint("main_bp", __name__, template_folder="templates")
