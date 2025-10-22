"""Script para verificar tablas en SQL Server"""
import pyodbc
from smart_reports.config.settings import DATABASE_CONFIG

try:
    # Conectar
    conn_string = (
        f"DRIVER={{{DATABASE_CONFIG['driver']}}};"
        f"SERVER={DATABASE_CONFIG['server']};"
        f"DATABASE={DATABASE_CONFIG['database']};"
        f"UID={DATABASE_CONFIG['username']};"
        f"PWD={DATABASE_CONFIG['password']}"
    )

    print("Conectando a SQL Server...")
    conn = pyodbc.connect(conn_string)
    cursor = conn.cursor()

    print("✓ Conexión exitosa!\n")

    # Listar todas las tablas
    print("=== TABLAS EN LA BASE DE DATOS ===")
    cursor.execute("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)

    tables = cursor.fetchall()
    print(f"Total de tablas: {len(tables)}\n")

    for table in tables:
        table_name = table[0]
        print(f"  - {table_name}")

        # Contar registros
        try:
            cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
            count = cursor.fetchone()[0]
            print(f"    Registros: {count}")
        except:
            print(f"    (No se pudo contar)")

    # Buscar tablas específicas que necesitamos
    print("\n\n=== VERIFICANDO TABLAS NECESARIAS ===")
    needed_tables = [
        'Usuario', 'UnidadDeNegocio', 'Modulo', 'ProgresoModulo',
        'instituto_Usuario', 'instituto_UnidadDeNegocio', 'instituto_Modulo', 'instituto_ProgresoModulo'
    ]

    for needed in needed_tables:
        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = ?
        """, (needed,))
        exists = cursor.fetchone()[0] > 0
        status = "✓ EXISTE" if exists else "✗ NO EXISTE"
        print(f"{status}: {needed}")

    # Si existe tabla Usuario, mostrar sus columnas
    print("\n\n=== COLUMNAS DE TABLA Usuario (si existe) ===")
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'Usuario'
        ORDER BY ORDINAL_POSITION
    """)
    columns = cursor.fetchall()
    if columns:
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
    else:
        print("  Tabla 'Usuario' no encontrada, buscando 'instituto_Usuario'...")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'instituto_Usuario'
            ORDER BY ORDINAL_POSITION
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")

    conn.close()
    print("\n[OK] Verificación completada!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
