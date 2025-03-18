import hashlib
import mysql.connector
from flask import Blueprint, jsonify, request
from config import DB_CONFIG

loginIniciado = Blueprint('auth', __name__)

@loginIniciado.route('/login', methods=['POST'])
def autenticar_usuario():
    try:
        datos = request.get_json()
        email = datos.get('email')
        password = datos.get('password')  # El usuario ingresa su contraseña en texto plano

        if not email or not password:
            return jsonify({"error": "Faltan parámetros"}), 400

        print(f"🟢 Recibido: email={email}, password={password}")  # Depuración

        conexion = mysql.connector.connect(**DB_CONFIG)
        if conexion.is_connected():
            cursor = conexion.cursor(dictionary=True)

            # Encriptar la contraseña ingresada por el usuario
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            print(f"🔒 Contraseña encriptada ingresada: {hashed_password}")

            consulta = """
                SELECT u.usuario_id, u.nombres, u.apellidos, u.email, u.password, n.nombre as rol 
                FROM usuarios u 
                INNER JOIN roles n ON u.rol_id = n.rol_id 
                WHERE email = %s
            """
            cursor.execute(consulta, (email,))
            usuario = cursor.fetchone()

            if usuario:
                print(f"🟡 Usuario encontrado en la BD: {usuario}")  # Depuración

                # 🔹 Comparar la contraseña encriptada ingresada con la almacenada
                if usuario['password'] == hashed_password:
                    print("✅ Contraseña correcta")  # Depuración
                    del usuario['password']  # Eliminar contraseña antes de enviarla al frontend
                    return jsonify({"mensaje": "Autenticación exitosa", "usuario": usuario}), 200
                else:
                    print("❌ Contraseña incorrecta")  # Depuración
                    return jsonify({"error": "Credenciales inválidas"}), 401
            else:
                print("❌ Usuario no encontrado")  # Depuración
                return jsonify({"error": "Credenciales inválidas"}), 401
    except mysql.connector.Error as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()



