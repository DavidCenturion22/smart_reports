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
            # Buscar patrones comunes de headers
            row_values = df.iloc[i].astype(str).values
            if any('Nombre completo' in v or 'User Name' in v or 'Usuario' in v for v in row_values):
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
        """
        # Crear un mapeo flexible - buscar columnas que contengan estas palabras clave
        normalized_df = df.copy()
        column_map = {}

        for col in df.columns:
            col_lower = str(col).lower().strip()

            # Identificación de usuario / User ID
            if 'identificación' in col_lower and 'usuario' in col_lower:
                column_map[col] = 'id_usuario'
            elif col_lower == 'user id':
                column_map[col] = 'id_usuario'

            # Nombre completo del usuario / User Name
            elif 'nombre completo' in col_lower:
                column_map[col] = 'nombre_usuario'
            elif col_lower == 'user name':
                column_map[col] = 'nombre_usuario'

            # Título de la capacitación / Training Title
            elif 'título' in col_lower and 'capacitación' in col_lower:
                column_map[col] = 'titulo_modulo'
            elif col_lower == 'training title':
                column_map[col] = 'titulo_modulo'

            # Estado del expediente / Transcript Status
            elif 'estado' in col_lower and 'expediente' in col_lower:
                column_map[col] = 'estado'
            elif col_lower == 'transcript status':
                column_map[col] = 'estado'

            # Fechas
            elif 'fecha' in col_lower and 'inicio' in col_lower:
                column_map[col] = 'fecha_inicio'
            elif col_lower == 'training start date':
                column_map[col] = 'fecha_inicio'

            elif 'fecha' in col_lower and 'finalización' in col_lower:
                column_map[col] = 'fecha_fin'
            elif col_lower == 'transcript completed date':
                column_map[col] = 'fecha_fin'

            elif 'fecha' in col_lower and 'registro' in col_lower:
                column_map[col] = 'fecha_registro'
            elif col_lower == 'transcript registration date':
                column_map[col] = 'fecha_registro'

            # Otros campos
            elif 'versión' in col_lower:
                column_map[col] = 'version'
            elif col_lower == 'training version':
                column_map[col] = 'version'

            elif 'tipo' in col_lower and 'capacitación' in col_lower:
                column_map[col] = 'tipo'
            elif col_lower == 'training type':
                column_map[col] = 'tipo'

            elif 'proveedor' in col_lower:
                column_map[col] = 'proveedor'
            elif col_lower == 'training provider':
                column_map[col] = 'proveedor'

        # Aplicar el mapeo
        normalized_df.rename(columns=column_map, inplace=True)

        # Verificar que tenemos las columnas mínimas requeridas
        required = ['id_usuario', 'titulo_modulo', 'estado']
        missing = [col for col in required if col not in normalized_df.columns]

        if missing:
            # Mostrar columnas disponibles para debugging
            print(f"Columnas originales del archivo: {list(df.columns)}")
            print(f"Columnas después del mapeo: {list(normalized_df.columns)}")
            print(f"Columnas faltantes: {missing}")
            raise ValueError(f"Columnas requeridas no encontradas después del mapeo: {missing}")

        return normalized_df

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

    def get_module_category(self, module_title: str) -> str:
        """
        Categoriza los módulos basándose en su título
        """
        title_lower = str(module_title).lower()

        # Categorías basadas en palabras clave
        categories = {
            'Cultura Organizacional': ['cultura', 'valores', 'ética', 'compliance', 'política'],
            'Operaciones': ['operación', 'operaciones', 'portuaria', 'grúa', 'equipo', 'maquinaria'],
            'Seguridad': ['seguridad', 'safety', 'nom-035', 'prevención', 'riesgo', 'emergencia'],
            'Tecnología': ['sistema', 'software', 'tecnología', 'digital', 'ti', 'informática'],
            'Gestión': ['gestión', 'liderazgo', 'administración', 'management', 'proyecto'],
            'Comercial': ['comercial', 'ventas', 'cliente', 'mercado', 'negocio'],
            'Salud y Bienestar': ['salud', 'bienestar', 'wellness', 'médico', 'primeros auxilios'],
            'Idiomas': ['inglés', 'english', 'idioma', 'language'],
            'General': []  # Categoría por defecto
        }

        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return category

        return 'General'

    def process_file(self, file_path: str) -> Dict:
        """
        Procesa el archivo completo y retorna estadísticas
        """
        # Leer y normalizar el archivo
        df = self.detect_file_structure(file_path)

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
            # tipo y proveedor son opcionales
            modulos_cols = ['titulo_modulo']
            if 'tipo' in df.columns:
                modulos_cols.append('tipo')
            if 'proveedor' in df.columns:
                modulos_cols.append('proveedor')

            modulos_df = df[modulos_cols].drop_duplicates()
            self.stats['modulos_unicos'] = len(modulos_df)

            for _, modulo in modulos_df.iterrows():
                if pd.notna(modulo['titulo_modulo']):
                    self.process_module(
                        titulo=modulo['titulo_modulo'],
                        tipo=modulo.get('tipo') if 'tipo' in modulo else None,
                        proveedor=modulo.get('proveedor') if 'proveedor' in modulo else None
                    )

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
        """
        try:
            # Verificar si el usuario existe
            self.cursor.execute("SELECT UserId FROM instituto_Usuario WHERE UserId = ?", (user_id,))

            if not self.cursor.fetchone():
                # Extraer información adicional del nombre si es posible
                email = f"{user_id}@hutchison.mx"  # Email por defecto

                # Insertar nuevo usuario
                self.cursor.execute("""
                    INSERT INTO instituto_Usuario (UserId, Nombre, Email, TipoDeCorreo)
                    VALUES (?, ?, ?, 'Corporativo')
                """, (user_id, nombre, email))

                self.stats['usuarios_nuevos'] += 1
                return True

        except Exception as e:
            self.stats['errores'].append(f"Error procesando usuario {user_id}: {str(e)}")

        return False

    def process_module(self, titulo: str, tipo: str = None, proveedor: str = None) -> int:
        """
        Procesa un módulo y retorna su ID
        """
        try:
            # Buscar si el módulo ya existe
            self.cursor.execute("SELECT IdModulo FROM instituto_Modulo WHERE NombreModulo = ?", (titulo,))
            result = self.cursor.fetchone()

            if result:
                return result[0]

            # Insertar nuevo módulo
            categoria = self.get_module_category(titulo)
            descripcion = f"Tipo: {tipo or 'N/A'}\nProveedor: {proveedor or 'Instituto HP'}\nCategoría: {categoria}"

            self.cursor.execute("""
                INSERT INTO instituto_Modulo (NombreModulo, DescripcionModulo, FechaDeAsignacion)
                VALUES (?, ?, GETDATE())
            """, (titulo, descripcion))

            self.conn.commit()

            # Obtener el ID del módulo recién insertado
            self.cursor.execute("SELECT @@IDENTITY")
            module_id = int(self.cursor.fetchone()[0])

            self.stats['modulos_nuevos'] += 1
            return module_id

        except Exception as e:
            self.stats['errores'].append(f"Error procesando módulo {titulo}: {str(e)}")
            return -1

    def process_inscription(self, row: pd.Series) -> bool:
        """
        Procesa una inscripción (progreso de módulo)
        """
        try:
            user_id = str(row['id_usuario'])
            titulo_modulo = row['titulo_modulo']
            estado = self.normalize_status(row.get('estado'))
            fecha_inicio = self.convert_excel_date(row.get('fecha_inicio'))
            fecha_fin = self.convert_excel_date(row.get('fecha_fin'))

            # Obtener ID del módulo
            self.cursor.execute("SELECT IdModulo FROM instituto_Modulo WHERE NombreModulo = ?", (titulo_modulo,))
            result = self.cursor.fetchone()

            if not result:
                # Si el módulo no existe, crearlo primero
                module_id = self.process_module(titulo_modulo, row.get('tipo'), row.get('proveedor'))
            else:
                module_id = result[0]

            if module_id > 0:
                # Verificar si ya existe la inscripción
                self.cursor.execute("""
                    SELECT IdInscripcion FROM instituto_ProgresoModulo
                    WHERE UserId = ? AND IdModulo = ?
                """, (user_id, module_id))

                existing = self.cursor.fetchone()

                if existing:
                    # Actualizar inscripción existente
                    self.cursor.execute("""
                        UPDATE instituto_ProgresoModulo
                        SET EstatusModuloUsuario = ?, FechaFinalizacion = ?, FechaUltimaActualizacion = GETDATE()
                        WHERE UserId = ? AND IdModulo = ?
                    """, (estado, fecha_fin, user_id, module_id))
                else:
                    # Insertar nueva inscripción
                    self.cursor.execute("""
                        INSERT INTO instituto_ProgresoModulo
                        (UserId, IdModulo, EstatusModuloUsuario, FechaInicio, FechaFinalizacion)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_id, module_id, estado, fecha_inicio, fecha_fin))

                self.stats['inscripciones_actualizadas'] += 1
                return True

        except Exception as e:
            self.stats['errores'].append(f"Error procesando inscripción: {str(e)}")

        return False

    def get_summary_stats(self) -> Dict:
        """
        Obtiene estadísticas generales de la base de datos
        """
        stats = {}

        # Total de usuarios
        self.cursor.execute("SELECT COUNT(*) FROM instituto_Usuario")
        stats['total_usuarios'] = self.cursor.fetchone()[0]

        # Total de módulos
        self.cursor.execute("SELECT COUNT(*) FROM instituto_Modulo")
        stats['total_modulos'] = self.cursor.fetchone()[0]

        # Estados de progreso
        self.cursor.execute("""
            SELECT EstatusModuloUsuario, COUNT(*)
            FROM instituto_ProgresoModulo
            GROUP BY EstatusModuloUsuario
        """)
        stats['estados'] = dict(self.cursor.fetchall())

        # Usuarios por unidad de negocio
        self.cursor.execute("""
            SELECT un.NombreUnidad, COUNT(u.UserId)
            FROM instituto_UnidadDeNegocio un
            LEFT JOIN instituto_Usuario u ON un.IdUnidadDeNegocio = u.IdUnidadDeNegocio
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
        """
        query = """
            SELECT
                m.NombreModulo,
                pm.EstatusModuloUsuario,
                pm.CalificacionModuloUsuario,
                pm.FechaInicio,
                pm.FechaFinalizacion
            FROM instituto_ProgresoModulo pm
            JOIN instituto_Modulo m ON pm.IdModulo = m.IdModulo
            WHERE pm.UserId = ?
            ORDER BY pm.FechaInicio DESC
        """

        return pd.read_sql_query(query, self.conn, params=[user_id])

    def get_module_stats(self) -> pd.DataFrame:
        """
        Obtiene estadísticas por módulo
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
            FROM instituto_Modulo m
            LEFT JOIN instituto_ProgresoModulo pm ON m.IdModulo = pm.IdModulo
            GROUP BY m.IdModulo, m.NombreModulo
            ORDER BY TotalUsuarios DESC
        """

        return pd.read_sql_query(query, self.conn)

    def get_business_unit_report(self, unit_id: int = None) -> pd.DataFrame:
        """
        Reporte por unidad de negocio
        """
        query = """
            SELECT
                un.NombreUnidad,
                COUNT(DISTINCT u.UserId) as TotalUsuarios,
                COUNT(DISTINCT pm.IdModulo) as ModulosActivos,
                SUM(CASE WHEN pm.EstatusModuloUsuario = 'Completado' THEN 1 ELSE 0 END) as ModulosCompletados,
                AVG(CASE WHEN pm.CalificacionModuloUsuario IS NOT NULL
                    THEN pm.CalificacionModuloUsuario END) as PromedioGeneral
            FROM instituto_UnidadDeNegocio un
            LEFT JOIN instituto_Usuario u ON un.IdUnidadDeNegocio = u.IdUnidadDeNegocio
            LEFT JOIN instituto_ProgresoModulo pm ON u.UserId = pm.UserId
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
        """
        query = f"""
            SELECT
                CAST(FechaFinalizacion AS DATE) as Fecha,
                COUNT(*) as ModulosCompletados,
                COUNT(DISTINCT UserId) as UsuariosActivos
            FROM instituto_ProgresoModulo
            WHERE EstatusModuloUsuario = 'Completado'
                AND FechaFinalizacion >= DATEADD(day, -{days}, GETDATE())
            GROUP BY CAST(FechaFinalizacion AS DATE)
            ORDER BY Fecha
        """

        return pd.read_sql_query(query, self.conn)
