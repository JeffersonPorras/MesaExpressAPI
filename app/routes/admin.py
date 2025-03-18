from flask import Blueprint, jsonify, request
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

adminStart = Blueprint('admin', __name__)  # Blueprint con un nombre más claro

@adminStart.route('/usuarios', methods=['GET'])
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



""" con esta Funcion obtenmos los roles que tenemos definidos en la base de datos """
@adminStart.route('/roles', methods=['GET'])
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



""" Con esta Funcion podremos actualizar los roles dentro de la interfaz del administrador """
""" 🔹 Ruta para actualizar el rol de un usuario con respuesta a OPTIONS """
@adminStart.route('/usuarios/<int:id>/rol', methods=['PUT', 'OPTIONS'])
def actualizar_rol(id):
    if request.method == "OPTIONS":
        print("🟢 Recibida solicitud OPTIONS")
        return jsonify({"mensaje": "OK"}), 200  # Responder preflight request

    try:
        datos = request.get_json()
        print(f"🔵 Datos recibidos: {datos}")  # Depuración

        nuevo_rol_id = datos.get('rol_id')

        if not nuevo_rol_id:
            print("❌ Error: Falta el rol_id")
            return jsonify({"error": "Falta el rol_id"}), 400

        conexion = mysql.connector.connect(**DB_CONFIG)
        if conexion.is_connected():
            cursor = conexion.cursor()
            print(f"🟡 Actualizando usuario {id} con nuevo rol {nuevo_rol_id}")
            cursor.execute("UPDATE usuarios SET rol_id = %s WHERE usuario_id = %s", (nuevo_rol_id, id))
            conexion.commit()

            if cursor.rowcount > 0:
                print("✅ Rol actualizado correctamente")
                return jsonify({"mensaje": "Rol actualizado correctamente"}), 200
            else:
                print("❌ Error: Usuario no encontrado")
                return jsonify({"error": "Usuario no encontrado"}), 404

    except Error as e:
        print(f"❌ Error en la base de datos: {e}")
        return jsonify({"error": str(e)}), 500
    
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()


""" con esta Funcion podremos eliminar los usuarios que no queremos que
a nuestra base de datos o personas que ya llevan cieto tiempo sin logearsen """
@adminStart.route('/usuarios/<int:id>', methods=['DELETE'])
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