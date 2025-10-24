"""
Panel ModernDashboard - Dashboard rediseñado con múltiples visualizaciones
"""
import customtkinter as ctk
from smart_reports.ui.components.metric_card import MetricCard
from smart_reports.ui.components.chart_card import ChartCard


class ModernDashboard(ctk.CTkFrame):
    """Dashboard completamente rediseñado con visualizaciones modernas"""

    def __init__(self, parent, db_connection, **kwargs):
        """
        Args:
            parent: Widget padre
            db_connection: Conexión a la base de datos
        """
        super().__init__(parent, fg_color='#1a1d2e', **kwargs)
        self.db = db_connection
        self.cursor = db_connection.cursor() if db_connection else None

        # Configurar grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Crear scroll container
        self._create_scrollable_content()

    def _create_scrollable_content(self):
        """Crear contenedor scrollable para el dashboard"""
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color='transparent',
            scrollbar_button_color='#3a3d5c',
            scrollbar_button_hover_color='#4a4d6c'
        )
        scroll_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        scroll_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Header con título y botón
        self._create_header(scroll_frame)

        # Row 1: Métricas principales (3 cards)
        self._create_metrics_row(scroll_frame)

        # Row 2: Distribución por unidad (2 cards)
        self._create_distribution_row(scroll_frame)

        # Row 3: Progreso de módulos (1 card grande)
        self._create_modules_progress(scroll_frame)

        # Row 4: Top performers (2 cards)
        self._create_performers_row(scroll_frame)

    def _create_header(self, parent):
        """Crear header con título y acciones"""
        header = ctk.CTkFrame(parent, fg_color='transparent', height=80)
        header.grid(row=0, column=0, columnspan=3, sticky='ew', pady=(0, 20))
        header.grid_columnconfigure(0, weight=1)
        header.grid_propagate(False)

        # Título
        title = ctk.CTkLabel(
            header,
            text='Panel de Control',
            font=('Segoe UI', 32, 'bold'),
            text_color='#ffffff',
            anchor='w'
        )
        title.pack(side='left')

        # Botón actualizar
        refresh_btn = ctk.CTkButton(
            header,
            text='⟳ Actualizar',
            font=('Segoe UI', 14),
            fg_color='#6c63ff',
            hover_color='#5a52d5',
            corner_radius=10,
            height=40,
            width=140,
            command=self.refresh_all_data
        )
        refresh_btn.pack(side='right', padx=10)

    def _create_metrics_row(self, parent):
        """Crear las 3 cards de métricas principales"""
        # Obtener datos reales
        total_users = self._get_total_users()
        active_modules = self._get_active_modules()
        completion_rate = self._get_completion_rate()

        # Card 1: Total Usuarios
        card1 = MetricCard(
            parent,
            title='Total de Usuarios',
            value=f'{total_users:,}',
            change_percent=None,
            icon='👥',
            color='#6c63ff'
        )
        card1.grid(row=1, column=0, sticky='ew', padx=10, pady=10)

        # Card 2: Módulos Activos
        card2 = MetricCard(
            parent,
            title='Módulos Activos',
            value=f'{active_modules}/14',
            icon='📚',
            color='#4ecdc4'
        )
        card2.grid(row=1, column=1, sticky='ew', padx=10, pady=10)

        # Card 3: Tasa de Completado
        card3 = MetricCard(
            parent,
            title='Tasa de Completado',
            value=f'{completion_rate:.1f}%',
            change_percent=None,
            icon='✓',
            color='#51cf66'
        )
        card3.grid(row=1, column=2, sticky='ew', padx=10, pady=10)

    def _create_distribution_row(self, parent):
        """Crear distribución por unidades de negocio"""
        # Obtener datos
        unidades_data = self._get_users_by_unit()

        if unidades_data and len(unidades_data) > 0:
            unidades = [row[0] for row in unidades_data]
            counts = [row[1] for row in unidades_data]

            # Card 1: Barras horizontales
            chart1 = ChartCard(parent, 'Usuarios por Unidad de Negocio', 'horizontal_bar')
            chart1.grid(row=2, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)
            chart1.create_chart(counts, unidades)

            # Card 2: Donut chart
            chart2 = ChartCard(parent, 'Distribución Porcentual', 'donut')
            chart2.grid(row=2, column=2, sticky='nsew', padx=10, pady=10)
            chart2.create_chart(counts, unidades)
        else:
            # Mostrar mensaje si no hay datos
            placeholder = ctk.CTkLabel(
                parent,
                text='No hay datos de unidades de negocio',
                font=('Segoe UI', 14),
                text_color='#a0a0b0'
            )
            placeholder.grid(row=2, column=0, columnspan=3, padx=10, pady=40)

    def _create_modules_progress(self, parent):
        """Crear gráfico de progreso por módulos"""
        # Obtener datos
        modules_data = self._get_modules_progress()

        if modules_data and len(modules_data) > 0:
            # Preparar datos para gráfico apilado
            module_names = []
            completados = []
            en_progreso = []
            registrados = []

            for row in modules_data:
                module_names.append(row[0][:20] + '...' if len(row[0]) > 20 else row[0])  # Truncar nombres largos
                completados.append(row[1] or 0)
                en_progreso.append(row[2] or 0)
                registrados.append(row[3] or 0)

            # Card con gráfico de barras apiladas
            chart = ChartCard(parent, 'Progreso por Módulo', 'stacked_bar', height=400)
            chart.grid(row=3, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)
            chart.create_chart(completados, module_names, en_progreso, registrados)
        else:
            # Mostrar mensaje si no hay datos
            placeholder = ctk.CTkLabel(
                parent,
                text='No hay datos de progreso de módulos',
                font=('Segoe UI', 14),
                text_color='#a0a0b0'
            )
            placeholder.grid(row=3, column=0, columnspan=3, padx=10, pady=40)

    def _create_performers_row(self, parent):
        """Crear cards de top performers"""
        # Card 1: Top unidades por completados
        top_units = self._get_top_units_by_completion()

        if top_units and len(top_units) > 0:
            units = [row[0] for row in top_units[:5]]  # Top 5
            completions = [row[1] for row in top_units[:5]]

            chart1 = ChartCard(parent, 'Top 5 Unidades - Módulos Completados', 'bar')
            chart1.grid(row=4, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)
            chart1.create_chart(completions, units)
        else:
            placeholder1 = ctk.CTkLabel(
                parent,
                text='No hay datos disponibles',
                font=('Segoe UI', 14),
                text_color='#a0a0b0'
            )
            placeholder1.grid(row=4, column=0, columnspan=2, padx=10, pady=40)

        # Card 2: Distribución de estados
        status_data = self._get_status_distribution()

        if status_data and len(status_data) > 0:
            statuses = [row[0] for row in status_data]
            counts = [row[1] for row in status_data]

            chart2 = ChartCard(parent, 'Distribución por Estado', 'donut')
            chart2.grid(row=4, column=2, sticky='nsew', padx=10, pady=10)
            chart2.create_chart(counts, statuses)
        else:
            placeholder2 = ctk.CTkLabel(
                parent,
                text='No hay datos disponibles',
                font=('Segoe UI', 14),
                text_color='#a0a0b0'
            )
            placeholder2.grid(row=4, column=2, padx=10, pady=40)

    # ==================== MÉTODOS DE DATOS ====================

    def _get_total_users(self):
        """Obtener total de usuarios"""
        if not self.cursor:
            return 0
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Instituto_Usuario")
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error obteniendo total de usuarios: {e}")
            return 0

    def _get_active_modules(self):
        """Obtener número de módulos activos"""
        if not self.cursor:
            return 0
        try:
            self.cursor.execute("SELECT COUNT(DISTINCT IdModulo) FROM Instituto_ProgresoModulo")
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error obteniendo módulos activos: {e}")
            return 0

    def _get_completion_rate(self):
        """Obtener tasa de completado"""
        if not self.cursor:
            return 0.0
        try:
            self.cursor.execute("""
                SELECT
                    CAST(SUM(CASE WHEN EstatusModuloUsuario = 'Terminado' THEN 1 ELSE 0 END) AS FLOAT) * 100 /
                    NULLIF(COUNT(*), 0) as rate
                FROM Instituto_ProgresoModulo
            """)
            result = self.cursor.fetchone()
            return result[0] if result and result[0] else 0.0
        except Exception as e:
            print(f"Error obteniendo tasa de completado: {e}")
            return 0.0

    def _get_users_by_unit(self):
        """Obtener usuarios por unidad de negocio"""
        if not self.cursor:
            return []
        try:
            self.cursor.execute("""
                SELECT un.NombreUnidad, COUNT(u.UserId)
                FROM Instituto_Usuario u
                JOIN Instituto_UnidadDeNegocio un ON u.IdUnidadDeNegocio = un.IdUnidadDeNegocio
                GROUP BY un.IdUnidadDeNegocio, un.NombreUnidad
                ORDER BY COUNT(u.UserId) DESC
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo usuarios por unidad: {e}")
            return []

    def _get_modules_progress(self):
        """Obtener progreso por módulo"""
        if not self.cursor:
            return []
        try:
            self.cursor.execute("""
                SELECT
                    m.NombreModulo,
                    SUM(CASE WHEN pm.EstatusModuloUsuario = 'Terminado' THEN 1 ELSE 0 END) as Completados,
                    SUM(CASE WHEN pm.EstatusModuloUsuario = 'En Progreso' THEN 1 ELSE 0 END) as EnProgreso,
                    SUM(CASE WHEN pm.EstatusModuloUsuario NOT IN ('Terminado', 'En Progreso') THEN 1 ELSE 0 END) as Registrados
                FROM Instituto_Modulo m
                LEFT JOIN Instituto_ProgresoModulo pm ON m.IdModulo = pm.IdModulo
                GROUP BY m.IdModulo, m.NombreModulo
                ORDER BY m.IdModulo
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo progreso de módulos: {e}")
            return []

    def _get_top_units_by_completion(self):
        """Obtener top unidades por completados"""
        if not self.cursor:
            return []
        try:
            self.cursor.execute("""
                SELECT
                    un.NombreUnidad,
                    COUNT(CASE WHEN pm.EstatusModuloUsuario = 'Terminado' THEN 1 END) as Completados
                FROM Instituto_UnidadDeNegocio un
                LEFT JOIN Instituto_Usuario u ON un.IdUnidadDeNegocio = u.IdUnidadDeNegocio
                LEFT JOIN Instituto_ProgresoModulo pm ON u.UserId = pm.UserId
                GROUP BY un.IdUnidadDeNegocio, un.NombreUnidad
                ORDER BY Completados DESC
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo top unidades: {e}")
            return []

    def _get_status_distribution(self):
        """Obtener distribución por estado"""
        if not self.cursor:
            return []
        try:
            self.cursor.execute("""
                SELECT
                    EstatusModuloUsuario as Estado,
                    COUNT(*) as Total
                FROM Instituto_ProgresoModulo
                GROUP BY EstatusModuloUsuario
                ORDER BY Total DESC
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo distribución de estados: {e}")
            return []

    def refresh_all_data(self):
        """Refrescar todos los datos del dashboard"""
        # Limpiar widgets existentes
        for widget in self.winfo_children():
            widget.destroy()

        # Recrear contenido
        self._create_scrollable_content()
