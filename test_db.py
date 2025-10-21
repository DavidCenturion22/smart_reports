"""Script de prueba para verificar la base de datos"""
import sqlite3
import sys

db_path = 'data/instituto_hp.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=== Verificacion de Base de Datos ===\n")

    # Listar tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tablas en la base de datos:")
    for table in tables:
        print(f"  - {table[0]}")

    print("\n=== Conteo de Registros ===")

    # Contar registros en cada tabla
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  {table_name}: {count} registros")

    # Mostrar unidades de negocio
    print("\n=== Unidades de Negocio ===")
    cursor.execute("SELECT IdUnidadDeNegocio, NombreUnidad, Descripcion FROM UnidadDeNegocio")
    unidades = cursor.fetchall()
    for unidad in unidades:
        print(f"  [{unidad[0]}] {unidad[1]} - {unidad[2]}")

    conn.close()
    print("\n[OK] Base de datos verificada correctamente!")

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
