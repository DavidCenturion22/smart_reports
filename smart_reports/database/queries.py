"""
Todas las consultas SQL del sistema
"""
from .connection import DatabaseConnection


class DatabaseQueries:
    """Centraliza todas las consultas SQL"""

    def __init__(self):
        self.db = DatabaseConnection()

    # ==================== UNIDADES DE NEGOCIO ====================

    def get_all_business_units(self):
        """Obtiene todas las unidades de negocio"""
        query = "SELECT IdUnidadDeNegocio, NombreUnidad FROM Instituto_UnidadDeNegocio ORDER BY NombreUnidad"
        return self.db.execute(query)

    def get_users_by_business_unit(self, unit_id):
        """Obtiene usuarios de una unidad de negocio"""
        query = """
            SELECT u.UserId, u.Nombre, u.Email, un.NombreUnidad,
                   u.Division, u.Nivel, u.Activo
            FROM dbo.Instituto_Usuario u
            INNER JOIN Instituto_UnidadDeNegocio un ON u.IdUnidadDeNegocio = un.IdUnidadDeNegocio
            WHERE un.IdUnidadDeNegocio = ?
            ORDER BY u.Nombre
        """
        return self.db.execute(query, (unit_id,))

    # ==================== MÓDULOS ====================

    def get_all_modules(self):
        """Obtiene todos los módulos"""
        query = "SELECT IdModulo, NombreModulo FROM Instituto_Modulo WHERE Activo = 1 ORDER BY NombreModulo"
        return self.db.execute(query)

    def get_modules_by_status(self, module_id=None, statuses=None):
        """Obtiene módulos filtrados por estado"""
        query = """
            SELECT m.NombreModulo, u.Nombre as Usuario,
                   pm.EstatusModuloUsuario as Estado,
                   pm.CalificacionModuloUsuario as Calificacion,
                   pm.FechaInicio, pm.FechaFinalizacion
            FROM Instituto_ProgresoModulo pm
            INNER JOIN Instituto_Modulo m ON pm.IdModulo = m.IdModulo
            INNER JOIN dbo.Instituto_Usuario u ON pm.UserId = u.UserId
            WHERE pm.EstatusModuloUsuario IN ({})
        """

        params = list(statuses) if statuses else []

        if module_id:
            query += " AND m.IdModulo = ?"
            params.append(module_id)

        query += " ORDER BY m.NombreModulo, u.Nombre"

        placeholders = ','.join(['?' for _ in statuses])
        query = query.format(placeholders)

        return self.db.execute(query, params)

    # ==================== USUARIOS ====================

    def get_user_by_id(self, user_id):
        """Busca usuario por ID - ERROR 7: Consulta completa con todos los campos"""
        query = """
            SELECT u.UserId, u.Nombre, u.Email, un.NombreUnidad,
                   u.Nivel, u.Division, u.Activo
            FROM dbo.Instituto_Usuario u
            LEFT JOIN Instituto_UnidadDeNegocio un ON u.IdUnidadDeNegocio = un.IdUnidadDeNegocio
            WHERE u.UserId = ?
        """
        return self.db.execute_one(query, (user_id,))

    def get_new_users(self, days=30):
        """Obtiene usuarios nuevos - ERROR 4: Removida FechaRegistro"""
        query = """
            SELECT u.UserId, u.Nombre, u.Email, un.NombreUnidad,
                   u.Division, u.Activo
            FROM dbo.Instituto_Usuario u
            LEFT JOIN Instituto_UnidadDeNegocio un ON u.IdUnidadDeNegocio = un.IdUnidadDeNegocio
            ORDER BY u.Nombre
        """
        return self.db.execute(query)

    def insert_user(self, user_id, nombre, email, unit_id=None):
        """Inserta nuevo usuario"""
        query = """
            INSERT INTO dbo.Instituto_Usuario (UserId, Nombre, Email, IdUnidadDeNegocio)
            VALUES (?, ?, ?, ?)
        """
        cursor = self.db.get_cursor()
        cursor.execute(query, (user_id, nombre, email, unit_id))
        self.db.commit()

    # ==================== DASHBOARDS ====================

    def get_module_status_counts(self):
        """Obtiene conteo de módulos por estado"""
        query = """
            SELECT EstatusModuloUsuario, COUNT(*) as Total
            FROM Instituto_ProgresoModulo
            GROUP BY EstatusModuloUsuario
        """
        return self.db.execute(query)

    def get_users_by_unit_counts(self):
        """Obtiene conteo de usuarios por unidad"""
        query = """
            SELECT un.NombreUnidad, COUNT(u.UserId) as Total
            FROM Instituto_UnidadDeNegocio un
            LEFT JOIN dbo.Instituto_Usuario u ON un.IdUnidadDeNegocio = u.IdUnidadDeNegocio
            GROUP BY un.NombreUnidad
            ORDER BY Total DESC
        """
        return self.db.execute(query)

    def get_monthly_completion_trend(self, months=6):
        """Obtiene tendencia mensual de completación"""
        query = """
            SELECT FORMAT(FechaFinalizacion, 'yyyy-MM') as Mes,
                   COUNT(*) as Completados
            FROM Instituto_ProgresoModulo
            WHERE EstatusModuloUsuario = 'Completado'
            AND FechaFinalizacion >= DATEADD(month, -?, GETDATE())
            GROUP BY FORMAT(FechaFinalizacion, 'yyyy-MM')
            ORDER BY Mes
        """
        return self.db.execute(query, (months,))

    # ==================== ACTUALIZACIÓN DE DATOS ====================

    def update_user(self, user_id, column, new_value):
        """Actualiza un campo de usuario"""
        query = f"UPDATE dbo.Instituto_Usuario SET {column} = ? WHERE UserId = ?"
        cursor = self.db.get_cursor()
        cursor.execute(query, (new_value, user_id))
        self.db.commit()

    def update_module_progress(self, inscription_id, column, new_value):
        """Actualiza progreso de módulo"""
        query = f"UPDATE Instituto_ProgresoModulo SET {column} = ? WHERE IdInscripcion = ?"
        cursor = self.db.get_cursor()
        cursor.execute(query, (new_value, inscription_id))
        self.db.commit()

    # ==================== HISTORIAL ====================

    def log_change(self, table_name, entity_id, column_name, old_value, new_value):
        """
        Registra cambio en historial
        ERROR 2: DESHABILITADO - No guardar en historialCambios
        """
        # DESHABILITADO: No registrar cambios en HistorialCambios
        # query = """
        #     INSERT INTO HistorialCambios
        #     (TipoEntidad, IdEntidad, TipoCambio, DescripcionCambio,
        #      ValorAnterior, ValorNuevo, UsuarioSistema)
        #     VALUES (?, ?, 'UPDATE', ?, ?, ?, 'Sistema')
        # """
        # cursor = self.db.get_cursor()
        # cursor.execute(query, (
        #     table_name, entity_id,
        #     f"Actualización de {column_name}",
        #     str(old_value), str(new_value)
        # ))
        # self.db.commit()
        pass  # No hacer nada

    # ==================== ESTADÍSTICAS ====================

    def get_system_stats(self):
        """Obtiene estadísticas generales del sistema"""
        stats = {}

        # Total usuarios
        result = self.db.execute_one("SELECT COUNT(*) FROM dbo.Instituto_Usuario")
        stats['total_users'] = result[0] if result else 0

        # Total módulos
        result = self.db.execute_one("SELECT COUNT(*) FROM Instituto_Modulo WHERE Activo = 1")
        stats['total_modules'] = result[0] if result else 0

        # Total inscripciones
        result = self.db.execute_one("SELECT COUNT(*) FROM Instituto_ProgresoModulo")
        stats['total_enrollments'] = result[0] if result else 0

        return stats
