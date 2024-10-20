import mysql.connector
    

mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'database': 'test',
    'auth_plugin': 'mysql_native_password'
}

conexion = mysql.connector.connect(**mysql_config)

def get_conexion():
    return conexion
