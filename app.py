from flask import Flask, jsonify,  request
from flask_cors import CORS  # Importar Flask-CORS
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Ruta para obtener todos los usuarios
@app.route('/usuarios', methods=['GET'])#Aqui usamos el metodo get para obtener los datos que deseamos
#Esta Funcion nos permite conectarnos a la base de datos de MySQL y alli podemos solicitar los datos qque necesitamos mediante el cursor de todos los usuarios
#que se encuentren en nuestra base de datos
def obtener_usuarios():
    try:
        # Conectar a la base de datos
        conexion = mysql.connector.connect(**DB_CONFIG)
        
        if conexion.is_connected():
            cursor = conexion.cursor(dictionary=True)  # Devuelve resultados como diccionarios
            cursor.execute("SELECT u.nombres, u.apellidos, u.email, n.nombre as rol FROM `usuarios` u INNER JOIN roles n on u.rol_id = n.rol_id;")  # Cambia el nombre de la tabla si es necesario
            usuarios = cursor.fetchall()#aqui nos permite visualizar todos los usuarios que se encuentren en la base de datos y los muestra en formato json
            return jsonify(usuarios), 200
        
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

# Endpoint para autenticar usuario
@app.route('/login', methods=['POST'])#aqui usamos el metodo POST para enviar los datos requeridos para el logeo que son el email y la contraseña
#Esta funcion nos permite autenticar si el usuario que desea logearse esta registrado en la base de datos 
#si lo esta este le va a pwermitir continuar dentro de la aplicacion para su uso de no ser asi 
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

# Punto de entrada principal
if __name__ == '__main__':
    app.run(debug=True)
