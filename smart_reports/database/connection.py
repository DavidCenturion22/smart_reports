"""
Gestión de conexión a SQL Server
"""
import pyodbc
from smart_reports.config.settings import DATABASE_CONFIG


class DatabaseConnection:
    """Singleton para gestionar la conexión a la base de datos"""

    _instance = None
    _connection = None
    _cursor = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def connect(self):
        """Establece conexión con SQL Server"""
        if self._connection is not None:
            return self._connection

        try:
            connection_string = (
                f"DRIVER={{{DATABASE_CONFIG['driver']}}};"
                f"SERVER={DATABASE_CONFIG['server']};"
                f"DATABASE={DATABASE_CONFIG['database']};"
                f"UID={DATABASE_CONFIG['username']};"
                f"PWD={DATABASE_CONFIG['password']};"
                f"TrustServerCertificate=yes;"
            )

            self._connection = pyodbc.connect(connection_string)
            self._cursor = self._connection.cursor()

            return self._connection

        except pyodbc.Error as e:
            raise Exception(f"Error de conexión a BD: {str(e)}")

    def get_cursor(self):
        """Retorna el cursor de la conexión"""
        if self._cursor is None:
            self.connect()
        return self._cursor

    def commit(self):
        """Commit de transacción"""
        if self._connection:
            self._connection.commit()

    def rollback(self):
        """Rollback de transacción"""
        if self._connection:
            self._connection.rollback()

    def close(self):
        """Cierra la conexión"""
        if self._connection:
            self._connection.close()
            self._connection = None
            self._cursor = None

    def execute(self, query, params=None):
        """Ejecuta una query y retorna resultados"""
        cursor = self.get_cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()

    def execute_one(self, query, params=None):
        """Ejecuta query y retorna un solo resultado"""
        cursor = self.get_cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchone()
