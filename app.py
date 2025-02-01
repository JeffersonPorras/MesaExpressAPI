from flask import Flask, jsonify,  request
from flask_cors import CORS  # Importar Flask-CORS
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Ruta para obtener todos los usuarios
@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        if conexion.is_connected():
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.usuario_id AS id, u.nombres, u.apellidos, u.email, u.rol_id, r.nombre AS rol 
                FROM usuarios u 
                INNER JOIN roles r ON u.rol_id = r.rol_id
            """)
            usuarios = cursor.fetchall()
            return jsonify(usuarios), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()

# Endpoint para autenticar usuario
@app.route('/login', methods=['POST'])#aqui usamos el metodo POST para enviar los datos requeridos para el logeo que son el email y la contraseña
#Esta funcion nos permite autenticar si el usuario que desea logearse esta registrado en la base de datos 
#si lo esta este le va a permitir continuar dentro de la aplicacion para su uso de no ser asi 
# entonces le dira que las credenciales son invalidas
def autenticar_usuario():
    try:
        # Obtiene los datos enviados en el cuerpo de la solicitud
        datos = request.get_json()
        email = datos.get('email')
        password = datos.get('password')

        # Verifica que se hayan enviado los parámetros requeridos
        if not email or not password:
            return jsonify({"error": "Faltan parámetros: email y/o password"}), 400

        # Conecta a la base de datos
        conexion = mysql.connector.connect(**DB_CONFIG)
        if conexion.is_connected():
            cursor = conexion.cursor(dictionary=True)

            # Consulta para verificar el email y password
            consulta = "SELECT u.usuario_id, u.nombres, u.apellidos, u.email, n.nombre as rol FROM `usuarios` u INNER JOIN roles n on u.rol_id = n.rol_id WHERE email = %s AND password = %s"
            cursor.execute(consulta, (email, password))
            usuario = cursor.fetchone()#aqui nos retona solo el usuario que esta siendo consultado y no lo muestra en un formato json

            if usuario:
                return jsonify({
                    "mensaje": "Autenticación exitosa",
                    "usuario": {
                        "id": usuario["usuario_id"],
                        "nombre": usuario["nombres"],
                        "apellido": usuario["apellidos"],
                        "email": usuario["email"],
                        "rol": usuario["rol"]
                    }
                }), 200
            else:
                return jsonify({"error": "Credenciales inválidas"}), 401

    except Error as e:
        return jsonify({"error": f"Error al conectar con la base de datos: {e}"}), 500

    except Exception as e:
        return jsonify({"error": f"Error inesperado: {e}"}), 500

    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()


# Ruta para obtener todos los roles
@app.route('/roles', methods=['GET'])
def obtener_roles():
    try:
        # Conectar a la base de datos
        conexion = mysql.connector.connect(**DB_CONFIG)
        
        if conexion.is_connected():
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT rol_id AS id, nombre FROM roles")  # Ajusta el nombre de la tabla si es diferente
            roles = cursor.fetchall()  # Obtiene todos los roles en formato JSON
            return jsonify(roles), 200
        
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()


@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        if conexion.is_connected():
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM usuarios WHERE usuario_id = %s", (id,))
            conexion.commit()  # Confirmar cambios en la base de datos
            
            if cursor.rowcount > 0:
                return jsonify({"mensaje": "Usuario eliminado correctamente"}), 200
            else:
                return jsonify({"error": "Usuario no encontrado"}), 404

    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()




@app.route('/usuarios/<int:id>/rol', methods=['PUT'])
def actualizar_rol(id):
    try:
        datos = request.get_json()
        nuevo_rol_id = datos.get('rol_id')

        if not nuevo_rol_id:
            return jsonify({"error": "Falta el rol_id"}), 400

        conexion = mysql.connector.connect(**DB_CONFIG)
        if conexion.is_connected():
            cursor = conexion.cursor()
            cursor.execute("UPDATE usuarios SET rol_id = %s WHERE usuario_id = %s", (nuevo_rol_id, id))
            conexion.commit()

            if cursor.rowcount > 0:
                return jsonify({"mensaje": "Rol actualizado correctamente"}), 200
            else:
                return jsonify({"error": "Usuario no encontrado"}), 404

    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()


# Punto de entrada principal
if __name__ == '__main__':
    app.run(debug=True)
