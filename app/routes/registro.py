import re
import hashlib
import mysql.connector
from flask import Blueprint, request, jsonify
from config import DB_CONFIG

registroUsuarios = Blueprint('registroUsuarios', __name__)

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

@registroUsuarios.route('/registro', methods=['POST', 'OPTIONS'])
def registrar_usuario():
    if request.method == "OPTIONS":
        print("🟢 Recibida solicitud OPTIONS, respondiendo con 200 OK.")
        return jsonify({"mensaje": "OK"}), 200  # Responder a preflight request

    try:
        datos = request.get_json()
        nombres = datos.get('nombres')
        apellidos = datos.get('apellidos')
        email = datos.get('email')
        password = datos.get('password')
        celular = datos.get('celular')
        direccion = datos.get('direccion')

        if not all([nombres, apellidos, email, password, celular, direccion]):
            return jsonify({"error": "Faltan datos obligatorios"}), 400

        if not re.match(EMAIL_REGEX, email):
            return jsonify({"error": "El correo electrónico no es válido"}), 400

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conexion = mysql.connector.connect(**DB_CONFIG)
        if conexion.is_connected():
            cursor = conexion.cursor()

            cursor.execute("SELECT email FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"error": "El correo ya está registrado"}), 409

            cursor.execute("""
                INSERT INTO usuarios (nombres, apellidos, email, password, celular, direccion, rol_id) 
                VALUES (%s, %s, %s, %s, %s, %s, 3)
            """, (nombres, apellidos, email, hashed_password, celular, direccion))
            conexion.commit()

            return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201

    except mysql.connector.Error as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
    
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()

