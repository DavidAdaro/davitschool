import os
from app import create_app
from models import db, GlobalConfig

def initialize_database():
    app = create_app()
    with app.app_context():
        print("🛡️ Recreando base de datos DavIT Shield...")
        db.drop_all()
        db.create_all()
        
        # Configuración Maestro inicial
        master = GlobalConfig(key="NEXTDNS_MASTER_PROFILE", value="TU_ID_MAESTRO")
        db.session.add(master)
        db.session.commit()
        print("✅ Base de datos inicializada correctamente.")

if __name__ == "__main__":
    initialize_database()