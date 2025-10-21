"""Script de prueba de conexión a SQL Server"""
import pyodbc

server = '10.133.18.111'
database = 'TNGCORE'
username = 'tngdatauser'
password = 'Password1'

print("Intentando conectar a SQL Server...")
print(f"Servidor: {server}")
print(f"Base de datos: {database}")
print(f"Usuario: {username}")
print()

try:
    connection_string = (
        f'DRIVER={{SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
    )
    print(f"Connection string: {connection_string}")
    print()

    conn = pyodbc.connect(connection_string, timeout=10)
    cursor = conn.cursor()

    print("[EXITO] Conexion exitosa a SQL Server!")

    # Probar una consulta simple
    cursor.execute("SELECT @@VERSION")
    version = cursor.fetchone()[0]
    print(f"\nVersion de SQL Server:\n{version}")

    cursor.close()
    conn.close()

except pyodbc.Error as e:
    print(f"[ERROR] Error de conexion:")
    print(f"  Codigo de error: {e.args[0]}")
    print(f"  Mensaje: {e.args[1]}")

except Exception as e:
    print(f"[ERROR] Error inesperado: {e}")
