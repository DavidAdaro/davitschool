import os

class Config:
    # Configuración de Base de Datos
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'davitschool.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de Email Institucional
    MAIL_SERVER = "smtp.hostinger.com" # Cambiar según tu proveedor (Gmail, Hostinger, etc.)
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = "alert@davitshieldsystems.com"
    MAIL_PASSWORD =  # Usa contraseña de aplicación
    MAIL_DEFAULT_SENDER = ("DavIT Shield Systems", "alert@davitshieldsystems.com")

    # NextDNS
    NEXTDNS_API_KEY = "658b6594906e85c8ef0181242c4da09e79680313"