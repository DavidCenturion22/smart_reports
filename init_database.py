"""
Script para inicializar la base de datos SQL Server
Ejecutar una sola vez al inicio del proyecto
"""

import os
import sys
sys.path.append('src')

from database_setup import DatabaseManager

if __name__ == "__main__":
    # Crear carpetas necesarias
    folders = ['backups', 'reports', 'logs', 'data/uploads']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"[OK] Carpeta creada: {folder}")

    # Crear base de datos en SQL Server
    print("\n=== Conectando a SQL Server ===")
    db_manager = DatabaseManager(
        server='10.133.18.111',
        database='TNGCORE',
        username='tngdatauser',
        password='Password1'
    )

    print("\nCreando estructura de base de datos...")
    db_manager.connect()
    db_manager.create_database()
    db_manager.insert_initial_data()
    db_manager.verify_database()
    db_manager.close()

    print("\n[OK] Sistema inicializado correctamente con SQL Server")
