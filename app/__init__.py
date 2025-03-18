from flask import Flask
from flask_cors import CORS
from app.routes.login import loginIniciado
from app.routes.admin import adminStart
from app.routes.registro import registroUsuarios

def create_app():
    app = Flask(__name__)

    # 🔥 Configuración CORS mejorada para aceptar solicitudes de http://127.0.0.1:5501
    CORS(app, resources={r"/*": {
        "origins": "http://127.0.0.1:5501",  # Puedes cambiar "*" por "http://127.0.0.1:5501" si quieres más seguridad
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin"]
    }})

    # Registrar los blueprints
    app.register_blueprint(loginIniciado, url_prefix='/auth')
    app.register_blueprint(adminStart, url_prefix='/admin')
    app.register_blueprint(registroUsuarios, url_prefix='/usuarios')

    return app




