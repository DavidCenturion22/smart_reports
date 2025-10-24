"""
Módulo de procesamiento de datos para Smart Reports - Instituto HP
Este módulo maneja la carga, procesamiento y análisis de los archivos Transcript Status
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pyodbc
from typing import Dict, List, Tuple, Optional
import os
import re

class TranscriptProcessor:
    """Procesador especializado para archivos Transcript Status de Cornerstone"""

    def __init__(self, db_connection: pyodbc.Connection):
        self.conn = db_connection
        self.cursor = db_connection.cursor()
        self.stats = {}

    def detect_file_structure(self, file_path: str) -> pd.DataFrame:
        """
        Detecta la estructura del archivo y devuelve un DataFrame limpio
        """
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, nrows=20)
        else:
            df = pd.read_excel(file_path, nrows=20)

        # Buscar la fila donde empiezan los headers reales
        header_row = 0
        for i in range(len(df)):
            # Buscar patrones comunes de headers (español e inglés)
            row_values = df.iloc[i].astype(str).values
            # Buscar palabras clave en español e inglés
            header_keywords = [
                'Nombre completo', 'User Name', 'Usuario',
                'Identificación', 'User ID',
                'Título', 'Training Title',
                'Estado', 'Transcript Status',
                'Capacitación', 'Training'
            ]
            if any(keyword in v for v in row_values for keyword in header_keywords):
                header_row = i
                break

        # Re-leer el archivo con los headers correctos
        if header_row > 0:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, skiprows=header_row)
            else:
                df = pd.read_excel(file_path, skiprows=header_row)
        else:
            # Leer normalmente
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

        return self.normalize_columns(df)

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza los nombres de columnas a un formato estándar
        Busca flexiblemente las columnas en el Excel
        Solo mapea las columnas que realmente se usan
        """
        # Crear un mapeo flexible - buscar columnas que contengan estas palabras clave
        normalized_df = df.copy()
        column_map = {}

        for col in df.columns:
            col_lower = str(col).lower().strip()

            # Identificación de usuario / User ID
            if ('identificación' in col_lower and 'usuario' in col_lower) or \
               'user id' in col_lower or \
               col_lower == 'userid' or \
               col_lower == 'id usuario':
                column_map[col] = 'id_usuario'

            # Nombre completo del usuario / User Name
            elif 'nombre completo' in col_lower or \
                 'user name' in col_lower or \
                 col_lower == 'username' or \
                 col_lower == 'nombre usuario':
                column_map[col] = 'nombre_usuario'

            # Título de la capacitación / Training Title
            elif ('título' in col_lower and 'capacitación' in col_lower) or \
                 'training title' in col_lower or \
                 'titulo capacitacion' in col_lower or \
                 'course title' in col_lower:
                column_map[col] = 'titulo_modulo'

            # Estado del expediente / Transcript Status
            elif ('estado' in col_lower and 'expediente' in col_lower) or \
                 'transcript status' in col_lower or \
                 col_lower == 'status' or \
                 col_lower == 'estado':
                column_map[col] = 'estado'

            # Fecha asignada del expediente -> FechaInicio en BD
            elif ('fecha asignada' in col_lower and 'expediente' in col_lower) or \
                 'transcript assigned date' in col_lower or \
                 'assigned date' in col_lower or \
                 'fecha asignada' in col_lower:
                column_map[col] = 'fecha_inicio'

            # Fecha de finalización de expediente -> FechaFinalizacion en BD
            elif ('fecha' in col_lower and 'finalización' in col_lower and 'expediente' in col_lower) or \
                 'transcript completed date' in col_lower or \
                 'completed date' in col_lower or \
                 'fecha finalizacion' in col_lower or \
                 ('fecha' in col_lower and 'completado' in col_lower):
                column_map[col] = 'fecha_fin'

        # Aplicar el mapeo
        normalized_df.rename(columns=column_map, inplace=True)

        # Verificar que tenemos las columnas mínimas requeridas
        required = ['id_usuario', 'titulo_modulo', 'estado']
        missing = [col for col in required if col not in normalized_df.columns]

        if missing:
            # Mostrar columnas disponibles para debugging
            print(f"\n=== ERROR EN MAPEO DE COLUMNAS ===")
            print(f"Columnas originales del archivo: {list(df.columns)}")
            print(f"Columnas después del mapeo: {list(normalized_df.columns)}")
            print(f"Columnas faltantes: {missing}")
            raise ValueError(f"Columnas requeridas no encontradas: {missing}")

        return normalized_df

    def extract_module_info(self, titulo: str) -> tuple:
        """
        Extrae el número del módulo del título exacto de los 14 módulos
        Retorna: (IdModulo, NombreCorto)
        """
        if pd.isna(titulo):
            return (None, None)

        titulo_upper = str(titulo).strip().upper()

        # Diccionario de mapeo EXACTO de los 14 módulos
        modulos_mapping = {
            'MÓDULO 1. INTRODUCCIÓN A LA FILOSOFÍA HUTCHISON PORTS': (1, 'Filosofía HP'),
            'MÓDULO 2. SOSTENIBILIDAD, NUESTRO COMPROMISO CON EL FUTURO': (2, 'Sostenibilidad'),
            'MÓDULO 3. INTRODUCCIÓN A LAS OPERACIONES': (3, 'Operaciones'),
            'MÓDULO 4. RELACIONES LABORALES': (4, 'Relaciones Laborales'),
            'MÓDULO 5. SEGURIDAD EN LAS OPERACIONES': (5, 'Seguridad'),
            'MÓDULO 6. CIBERSEGURIDAD': (6, 'Ciberseguridad'),
            'MÓDULO 7. ENTORNO LABORAL SALUDABLE': (7, 'Entorno Laboral'),
            'MÓDULO 8. PROCESOS DE RECURSOS HUMANOS': (8, 'RRHH'),
            'MÓDULO 9. PROGRAMAS DE BIENESTAR INTEGRAL': (9, 'Bienestar'),
            'MÓDULO 10. DESARROLLO DE NUEVOS PRODUCTOS': (10, 'Nuevos Productos'),
            'MÓDULO 11. PRODUCTOS DIGITALES DE HP': (11, 'Productos Digitales'),
            'MÓDULO 12. TECNOLOGÍA: IMPULSO PARA LA EFICIENCIA Y PRODUCTIVIDAD': (12, 'Tecnología'),
            'MÓDULO 13. ACTIVACIÓN DE PROTOCOLOS Y BRIGADAS DE CONTINGENCIA': (13, 'Contingencia'),
            'MÓDULO 14. SISTEMA INTEGRADO DE GESTIÓN DE CALIDAD Y MEJORA CONTINUA': (14, 'Calidad'),
        }

        # Buscar coincidencia exacta primero
        if titulo_upper in modulos_mapping:
            return modulos_mapping[titulo_upper]

        # Si no hay coincidencia exacta, buscar por patrón MÓDULO X.
        match = re.search(r'MÓDULO\s+(\d+)\.', titulo_upper)
        if match:
            num = int(match.group(1))
            if 1 <= num <= 14:
                return (num, f'Módulo {num}')

        return (None, None)

    def convert_excel_date(self, excel_date) -> Optional[str]:
        """
        Convierte fechas de Excel a formato ISO
        """
        if pd.isna(excel_date):
            return None

        try:
            if isinstance(excel_date, (int, float)):
                # Fecha numérica de Excel
                dt = datetime(1899, 12, 30) + timedelta(days=excel_date)
                return dt.strftime('%Y-%m-%d')
            elif isinstance(excel_date, str):
                # Intentar parsear diferentes formatos
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']:
                    try:
                        dt = datetime.strptime(excel_date.split(' ')[0], fmt)
                        return dt.strftime('%Y-%m-%d')
                    except:
                        continue
                return excel_date  # Devolver como está si no se puede convertir
            else:
                return str(excel_date)
        except:
            return None

    def extract_business_unit(self, user_name: str) -> Optional[str]:
        """
        Intenta extraer la unidad de negocio del nombre del usuario si está codificada
        """
        # Por ahora retorna None, pero se puede expandir si hay patrones
        return None

    def normalize_status(self, status: str) -> str:
        """
        Normaliza los estados a valores estándar
        MAPEO EXACTO según los estados del Excel:
        - "Terminado" -> "Completado"
        - "En Progreso" -> "En proceso"
        - "Registrado" -> "Registrado"
        """
        if pd.isna(status):
            return 'No iniciado'

        status = str(status).strip()

        # Mapeo exacto primero
        exact_map = {
            'Terminado': 'Completado',
            'En Progreso': 'En proceso',
            'Registrado': 'Registrado',
        }

        # Buscar coincidencia exacta primero
        if status in exact_map:
            return exact_map[status]

        # Si no, buscar case-insensitive
        status_lower = status.lower()

        status_map = {
            'terminado': 'Completado',
            'completed': 'Completado',
            'completado': 'Completado',
            'complete': 'Completado',
            'finalizado': 'Completado',
            'aprobado': 'Completado',
            'passed': 'Completado',

            'en progreso': 'En proceso',
            'en proceso': 'En proceso',
            'in progress': 'En proceso',
            'iniciado': 'En proceso',
            'started': 'En proceso',

            'registrado': 'Registrado',
            'registered': 'Registrado',
            'inscrito': 'Registrado',
            'enrolled': 'Registrado',

            'no iniciado': 'No iniciado',
            'not started': 'No iniciado',
            'pendiente': 'No iniciado',
            'pending': 'No iniciado'
        }

        for key, value in status_map.items():
            if key in status_lower:
                return value

        # Si no encuentra ningún match, retornar el estado original para debugging
        print(f"ADVERTENCIA: Estado no reconocido: '{status}'")
        return 'No iniciado'  # Default


    def process_file(self, file_path: str) -> Dict:
        """
        Procesa el archivo completo y retorna estadísticas
        IMPORTANTE: Ahora procesa TODOS los 14 módulos (MÓDULO 1. hasta MÓDULO 14.)
        """
        # Leer y normalizar el archivo
        df = self.detect_file_structure(file_path)

        # CRITICAL: Filtrar solo filas con MÓDULO X. (1-14) en el título
        print(f"\nTotal de registros antes del filtro: {len(df)}")
        df = df[df['titulo_modulo'].str.contains(r'MÓDULO\s+\d+\.', case=False, na=False, regex=True)]
        print(f"Registros después de filtrar MÓDULO 1-14: {len(df)}")

        # CRITICAL: Filtrar solo estados válidos
        valid_states = ['Terminado', 'En Progreso', 'Registrado', 'En progreso']
        df = df[df['estado'].isin(valid_states)]
        print(f"Registros después de filtrar estados válidos: {len(df)}")

        # Estadísticas iniciales
        self.stats = {
            'archivo': os.path.basename(file_path),
            'fecha_procesamiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_registros': len(df),
            'usuarios_unicos': 0,
            'modulos_unicos': 0,
            'usuarios_nuevos': 0,
            'modulos_nuevos': 0,
            'inscripciones_actualizadas': 0,
            'errores': []
        }

        try:
            # Verificar que tenemos las columnas necesarias
            required_cols = ['id_usuario', 'titulo_modulo', 'estado']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Faltan columnas requeridas: {missing_cols}")

            # Procesar usuarios únicos
            # Usar nombre_usuario si existe, si no usar id_usuario como nombre
            if 'nombre_usuario' not in df.columns:
                df['nombre_usuario'] = df['id_usuario']

            usuarios_df = df[['id_usuario', 'nombre_usuario']].drop_duplicates()
            self.stats['usuarios_unicos'] = len(usuarios_df)

            for _, user in usuarios_df.iterrows():
                if pd.notna(user['id_usuario']):
                    nombre = user.get('nombre_usuario', user['id_usuario'])
                    if pd.isna(nombre):
                        nombre = str(user['id_usuario'])
                    self.process_user(
                        user_id=str(user['id_usuario']),
                        nombre=str(nombre)
                    )

            # Procesar módulos únicos
            modulos_df = df[['titulo_modulo']].drop_duplicates()
            self.stats['modulos_unicos'] = len(modulos_df)

            for _, modulo in modulos_df.iterrows():
                if pd.notna(modulo['titulo_modulo']):
                    self.process_module(titulo=modulo['titulo_modulo'])

            # Procesar inscripciones (progreso de módulos)
            print(f"\nProcesando {len(df)} inscripciones...")
            for idx, row in df.iterrows():
                if pd.notna(row['id_usuario']) and pd.notna(row['titulo_modulo']):
                    self.process_inscription(row)
                    if (idx + 1) % 100 == 0:
                        print(f"  Procesadas {idx + 1}/{len(df)} inscripciones...")

            self.conn.commit()
            print(f"✓ Procesamiento completado exitosamente!")

        except Exception as e:
            self.conn.rollback()
            self.stats['errores'].append(str(e))
            print(f"✗ Error durante el procesamiento: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e

        return self.stats

    def process_user(self, user_id: str, nombre: str) -> bool:
        """
        Procesa un usuario y lo inserta si es nuevo
        Tabla: Instituto_Usuario
        """
        try:
            # Verificar si el usuario existe
            self.cursor.execute("SELECT UserId FROM Instituto_Usuario WHERE UserId = ?", (user_id,))

            if not self.cursor.fetchone():
                # Extraer información adicional del nombre si es posible
                email = f"{user_id}@hutchison.mx"  # Email por defecto

                # Insertar nuevo usuario
                self.cursor.execute("""
                    INSERT INTO Instituto_Usuario (UserId, Nombre, Email, TipoDeCorreo)
                    VALUES (?, ?, ?, 'Corporativo')
                """, (user_id, nombre, email))

                self.stats['usuarios_nuevos'] += 1
                return True

        except Exception as e:
            self.stats['errores'].append(f"Error procesando usuario {user_id}: {str(e)}")

        return False

    def process_module(self, titulo: str) -> int:
        """
        Procesa un módulo y retorna su ID
        CRÍTICO: Extrae el ID del módulo usando mapeo de 14 módulos exactos
        Tabla: Instituto_Modulo
        """
        try:
            # Extraer información del módulo (ID y nombre corto)
            module_id, nombre_corto = self.extract_module_info(titulo)

            if module_id is None:
                self.stats['errores'].append(f"No se pudo extraer IdModulo de: {titulo}")
                return -1

            # Verificar si el módulo ya existe por su número
            self.cursor.execute("SELECT IdModulo FROM Instituto_Modulo WHERE IdModulo = ?", (module_id,))
            result = self.cursor.fetchone()

            if result:
                return result[0]

            # Insertar nuevo módulo con IdModulo específico y nombre corto
            self.cursor.execute("""
                SET IDENTITY_INSERT Instituto_Modulo ON;
                INSERT INTO Instituto_Modulo (IdModulo, NombreModulo, FechaDeAsignacion, Activo)
                VALUES (?, ?, GETDATE(), 1);
                SET IDENTITY_INSERT Instituto_Modulo OFF;
            """, (module_id, nombre_corto))

            self.conn.commit()
            self.stats['modulos_nuevos'] += 1
            print(f"  ✓ Módulo {module_id} creado: {nombre_corto}")
            return module_id

        except Exception as e:
            self.stats['errores'].append(f"Error procesando módulo {titulo}: {str(e)}")
            return -1

    def process_inscription(self, row: pd.Series) -> bool:
        """
        Procesa una inscripción (progreso de módulo)
        CRÍTICO: Mapea a Instituto_ProgresoModulo
        Mapeo de columnas:
        - "Identificación de usuario" -> UserId
        - "Título de la capacitación" -> Extrae IdModulo con regex MÓDULO 1.X
        - "Estado del expediente" -> EstatusModuloUsuario (normalizado)
        - "Fecha asignada del expediente" -> FechaInicio
        - "Fecha de finalización de expediente" -> FechaFinalizacion
        """
        try:
            user_id = str(row['id_usuario'])
            titulo_modulo = row['titulo_modulo']

            # Extraer el número del módulo del título usando mapeo de 14 módulos
            module_id, _ = self.extract_module_info(titulo_modulo)

            if module_id is None:
                self.stats['errores'].append(f"No se pudo extraer IdModulo de: {titulo_modulo}")
                return False

            # Normalizar estado
            estado = self.normalize_status(row.get('estado'))

            # Convertir fechas
            fecha_inicio = self.convert_excel_date(row.get('fecha_inicio'))
            fecha_fin = self.convert_excel_date(row.get('fecha_fin'))

            # Asegurar que el módulo existe
            self.cursor.execute("SELECT IdModulo FROM Instituto_Modulo WHERE IdModulo = ?", (module_id,))
            if not self.cursor.fetchone():
                # Crear el módulo si no existe
                module_id = self.process_module(titulo_modulo)
                if module_id <= 0:
                    return False

            # UPSERT: Verificar si ya existe la inscripción (UserId + IdModulo)
            self.cursor.execute("""
                SELECT IdInscripcion FROM Instituto_ProgresoModulo
                WHERE UserId = ? AND IdModulo = ?
            """, (user_id, module_id))

            existing = self.cursor.fetchone()

            if existing:
                # Actualizar inscripción existente
                self.cursor.execute("""
                    UPDATE Instituto_ProgresoModulo
                    SET EstatusModuloUsuario = ?,
                        FechaInicio = ?,
                        FechaFinalizacion = ?,
                        FechaUltimaActualizacion = GETDATE()
                    WHERE UserId = ? AND IdModulo = ?
                """, (estado, fecha_inicio, fecha_fin, user_id, module_id))
            else:
                # Insertar nueva inscripción
                self.cursor.execute("""
                    INSERT INTO Instituto_ProgresoModulo
                    (UserId, IdModulo, EstatusModuloUsuario, FechaInicio, FechaFinalizacion)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, module_id, estado, fecha_inicio, fecha_fin))

            self.stats['inscripciones_actualizadas'] += 1
            return True

        except Exception as e:
            self.stats['errores'].append(f"Error procesando inscripción: {str(e)}")
            import traceback
            traceback.print_exc()

        return False

    def get_summary_stats(self) -> Dict:
        """
        Obtiene estadísticas generales de la base de datos
        Tablas: Instituto_Usuario, Instituto_Modulo, Instituto_ProgresoModulo, Instituto_UnidadDeNegocio
        """
        stats = {}

        # Total de usuarios
        self.cursor.execute("SELECT COUNT(*) FROM Instituto_Usuario")
        stats['total_usuarios'] = self.cursor.fetchone()[0]

        # Total de módulos
        self.cursor.execute("SELECT COUNT(*) FROM Instituto_Modulo")
        stats['total_modulos'] = self.cursor.fetchone()[0]

        # Estados de progreso
        self.cursor.execute("""
            SELECT EstatusModuloUsuario, COUNT(*)
            FROM Instituto_ProgresoModulo
            GROUP BY EstatusModuloUsuario
        """)
        stats['estados'] = dict(self.cursor.fetchall())

        # Usuarios por unidad de negocio
        self.cursor.execute("""
            SELECT un.NombreUnidad, COUNT(u.UserId)
            FROM Instituto_UnidadDeNegocio un
            LEFT JOIN Instituto_Usuario u ON un.IdUnidadDeNegocio = u.IdUnidadDeNegocio
            GROUP BY un.IdUnidadDeNegocio, un.NombreUnidad
        """)
        stats['usuarios_por_unidad'] = dict(self.cursor.fetchall())

        return stats


class ReportGenerator:
    """Generador de reportes y análisis"""

    def __init__(self, db_connection: pyodbc.Connection):
        self.conn = db_connection
        self.cursor = db_connection.cursor()

    def get_user_progress(self, user_id: str) -> pd.DataFrame:
        """
        Obtiene el progreso completo de un usuario
        Tablas: Instituto_ProgresoModulo, Instituto_Modulo
        """
        query = """
            SELECT
                m.NombreModulo,
                pm.EstatusModuloUsuario,
                pm.CalificacionModuloUsuario,
                pm.FechaInicio,
                pm.FechaFinalizacion
            FROM Instituto_ProgresoModulo pm
            JOIN Instituto_Modulo m ON pm.IdModulo = m.IdModulo
            WHERE pm.UserId = ?
            ORDER BY pm.FechaInicio DESC
        """

        return pd.read_sql_query(query, self.conn, params=[user_id])

    def get_module_stats(self) -> pd.DataFrame:
        """
        Obtiene estadísticas por módulo
        Tablas: Instituto_Modulo, Instituto_ProgresoModulo
        """
        query = """
            SELECT
                m.NombreModulo,
                COUNT(DISTINCT pm.UserId) as TotalUsuarios,
                SUM(CASE WHEN pm.EstatusModuloUsuario = 'Completado' THEN 1 ELSE 0 END) as Completados,
                SUM(CASE WHEN pm.EstatusModuloUsuario = 'En proceso' THEN 1 ELSE 0 END) as EnProceso,
                SUM(CASE WHEN pm.EstatusModuloUsuario = 'Registrado' THEN 1 ELSE 0 END) as Registrados,
                AVG(CASE WHEN pm.CalificacionModuloUsuario IS NOT NULL
                    THEN pm.CalificacionModuloUsuario END) as PromedioCalificacion
            FROM Instituto_Modulo m
            LEFT JOIN Instituto_ProgresoModulo pm ON m.IdModulo = pm.IdModulo
            GROUP BY m.IdModulo, m.NombreModulo
            ORDER BY TotalUsuarios DESC
        """

        return pd.read_sql_query(query, self.conn)

    def get_business_unit_report(self, unit_id: int = None) -> pd.DataFrame:
        """
        Reporte por unidad de negocio
        Tablas: Instituto_UnidadDeNegocio, Instituto_Usuario, Instituto_ProgresoModulo
        """
        query = """
            SELECT
                un.NombreUnidad,
                COUNT(DISTINCT u.UserId) as TotalUsuarios,
                COUNT(DISTINCT pm.IdModulo) as ModulosActivos,
                SUM(CASE WHEN pm.EstatusModuloUsuario = 'Completado' THEN 1 ELSE 0 END) as ModulosCompletados,
                AVG(CASE WHEN pm.CalificacionModuloUsuario IS NOT NULL
                    THEN pm.CalificacionModuloUsuario END) as PromedioGeneral
            FROM Instituto_UnidadDeNegocio un
            LEFT JOIN Instituto_Usuario u ON un.IdUnidadDeNegocio = u.IdUnidadDeNegocio
            LEFT JOIN Instituto_ProgresoModulo pm ON u.UserId = pm.UserId
        """

        if unit_id:
            query += " WHERE un.IdUnidadDeNegocio = ? GROUP BY un.IdUnidadDeNegocio, un.NombreUnidad"
            return pd.read_sql_query(query, self.conn, params=[unit_id])
        else:
            query += " GROUP BY un.IdUnidadDeNegocio, un.NombreUnidad"
            return pd.read_sql_query(query, self.conn)

    def get_completion_trends(self, days: int = 30) -> pd.DataFrame:
        """
        Obtiene tendencias de completación
        Tabla: Instituto_ProgresoModulo
        """
        query = f"""
            SELECT
                CAST(FechaFinalizacion AS DATE) as Fecha,
                COUNT(*) as ModulosCompletados,
                COUNT(DISTINCT UserId) as UsuariosActivos
            FROM Instituto_ProgresoModulo
            WHERE EstatusModuloUsuario = 'Completado'
                AND FechaFinalizacion >= DATEADD(day, -{days}, GETDATE())
            GROUP BY CAST(FechaFinalizacion AS DATE)
            ORDER BY Fecha
        """

        return pd.read_sql_query(query, self.conn)
