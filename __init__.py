# __init__.py
import os
from flask import Flask
from .models import db

def create_app():
    app = Flask(__name__)
    
    # Configuración de la base de datos profesional
    # Se asegura de que la DB se cree en la carpeta 'instance' como en tu repo de GitHub
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'instance', 'davitschool.db')
    
    # Crear carpeta instance si no existe
    if not os.path.exists(os.path.join(basedir, 'instance')):
        os.makedirs(os.path.join(basedir, 'instance'))

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    return app