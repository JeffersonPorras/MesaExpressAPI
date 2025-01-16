import mysql.connector
from mysql.connector import Error

#Esta funcion permite con un try catch establecer la conexion como primera medida
#buscando el localhost el usuario de servidor y su debida contraseña y permitiendo conectar a la base de datos
#luego se asegura de que la conexion sea exitosa y se crea un cursos que vendria siendo nuestro puente entre python 
#la base de datos para realizar las diferentes consultas que se necesiten 
#pero tambien si no se logra una conexion exitosa entonces nos mostrara error 
#y en la rte final del try catch despues de haber realizado todo da por cerrada la conexion a la base de datos.
def conectar_a_mysql():
    try:
        # Establecer la conexión
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",        # Por defecto, el usuario es 'root' en XAMPP
            password="", # Por defecto, la contraseña está vacía en XAMPP
            database="mesaexpress"        # Cambia por el nombre de tu base de datos
        )

        if conexion.is_connected():
            print("Conexión exitosa a la base de datos")
            
            # Obtener información del servidor
            info_servidor = conexion.get_server_info()
            print(f"Versión del servidor MySQL: {info_servidor}")

            # Crear un cursor para ejecutar consultas
            cursor = conexion.cursor()
            cursor.execute("SELECT DATABASE();")
            nombre_base_datos = cursor.fetchone()
            print(f"Conectado a la base de datos: {nombre_base_datos[0]}")

            # Cierra el cursor
            cursor.close()

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
    finally:
        if conexion.is_connected():
            conexion.close()
            print("Conexión cerrada.")

# Llama a la función
if __name__ == "__main__":
    conectar_a_mysql()
