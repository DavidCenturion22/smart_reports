"""
Ventana principal de Smart Reports - VERSIÓN MODERNA con CustomTkinter
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from datetime import datetime
import os

from smart_reports.config.settings import APP_CONFIG
from smart_reports.database.connection import DatabaseConnection
from smart_reports.services.data_processor import TranscriptProcessor
from smart_reports.ui.components.modern_sidebar import ModernSidebar
from smart_reports.ui.panels.modern_dashboard import ModernDashboard


# Configurar appearance de customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class MainWindow:
    """Ventana principal moderna de la aplicación"""

    def __init__(self, root):
        self.root = root
        self.root.title("SMART REPORTS - Instituto Hutchison Ports")
        self.root.geometry("1400x900")

        # Base de datos
        self.db = DatabaseConnection()
        try:
            self.conn = self.db.connect()
            self.cursor = self.db.get_cursor()
            self.verify_database_tables()
        except Exception as e:
            messagebox.showerror("Error de Conexión",
                f"No se pudo conectar a la base de datos:\n{str(e)}")

        # Variables de tracking
        self.current_file = None
        self.changes_log = []

        # Crear interfaz moderna
        self.create_modern_interface()

    def verify_database_tables(self):
        """Verificar que las tablas necesarias existan"""
        tables_needed = ['Instituto_UnidadDeNegocio', 'Instituto_Usuario',
                        'Instituto_Modulo', 'Instituto_ProgresoModulo']
        placeholders = ','.join(['?' for _ in tables_needed])

        try:
            self.cursor.execute(f"""
                SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                AND TABLE_NAME IN ({placeholders})
            """, tables_needed)

            existing_tables = [t[0] for t in self.cursor.fetchall()]

            if len(existing_tables) < len(tables_needed):
                missing = set(tables_needed) - set(existing_tables)
                messagebox.showwarning("Advertencia",
                    f"Faltan tablas en la BD: {', '.join(missing)}\n" +
                    "Verifique que las tablas existan en la base de datos.")
        except Exception as e:
            print(f"Error verificando tablas: {e}")

    def create_modern_interface(self):
        """Crear interfaz moderna con customtkinter"""
        # Container principal con fondo oscuro
        self.main_container = ctk.CTkFrame(self.root, fg_color='#1a1d2e', corner_radius=0)
        self.main_container.pack(fill='both', expand=True)

        # Sidebar moderna
        navigation_callbacks = {
            'dashboard': self.show_dashboard_panel,
            'consultas': self.show_consultas_panel,
            'actualizar': self.show_actualizar_panel,
            'configuracion': self.show_configuracion_panel,
        }

        self.sidebar = ModernSidebar(self.main_container, navigation_callbacks)
        self.sidebar.pack(side='left', fill='y')

        # Área de contenido principal
        self.content_area = ctk.CTkFrame(self.main_container, fg_color='#1a1d2e', corner_radius=0)
        self.content_area.pack(side='left', fill='both', expand=True)

        # Mostrar dashboard por defecto
        self.show_dashboard_panel()
        self.sidebar.set_active('dashboard')

    def clear_content_area(self):
        """Limpiar área de contenido"""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # ==================== SECCIONES PRINCIPALES ====================

    def show_dashboard_panel(self):
        """Mostrar panel de dashboard moderno"""
        self.clear_content_area()

        # Crear Modern Dashboard
        dashboard = ModernDashboard(self.content_area, self.conn)
        dashboard.pack(fill='both', expand=True)

    def show_actualizar_panel(self):
        """Panel de actualización de datos - MODERNIZADO"""
        self.clear_content_area()

        # Scroll frame para contenido
        scroll_frame = ctk.CTkScrollableFrame(
            self.content_area,
            fg_color='transparent',
            scrollbar_button_color='#3a3d5c'
        )
        scroll_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkFrame(scroll_frame, fg_color='transparent')
        header.pack(fill='x', pady=(0, 30))

        title = ctk.CTkLabel(
            header,
            text='Actualizar Datos',
            font=('Segoe UI', 32, 'bold'),
            text_color='#ffffff'
        )
        title.pack(side='left')

        # Card 1: Seleccionar archivo
        card1 = ctk.CTkFrame(scroll_frame, fg_color='#2b2d42', corner_radius=20, border_width=1, border_color='#3a3d5c')
        card1.pack(fill='x', pady=10)

        # Card header
        card1_header = ctk.CTkLabel(
            card1,
            text='1️⃣  Seleccionar Archivo',
            font=('Segoe UI', 20, 'bold'),
            text_color='#ffffff'
        )
        card1_header.pack(padx=30, pady=(20, 10), anchor='w')

        # File info frame
        file_frame = ctk.CTkFrame(card1, fg_color='#3a3d5c', corner_radius=10)
        file_frame.pack(fill='x', padx=30, pady=10)

        file_label_title = ctk.CTkLabel(
            file_frame,
            text='Archivo:',
            font=('Segoe UI', 14),
            text_color='#a0a0b0'
        )
        file_label_title.pack(side='left', padx=15, pady=15)

        self.file_label = ctk.CTkLabel(
            file_frame,
            text='Ningún archivo seleccionado',
            font=('Segoe UI', 14),
            text_color='#6c6c80'
        )
        self.file_label.pack(side='left', padx=5, pady=15)

        # Botón seleccionar
        select_btn = ctk.CTkButton(
            card1,
            text='📁  Seleccionar Archivo Transcript Status',
            font=('Segoe UI', 16, 'bold'),
            fg_color='#6c63ff',
            hover_color='#5a52d5',
            corner_radius=10,
            height=50,
            command=self.select_transcript_file
        )
        select_btn.pack(padx=30, pady=(10, 20))

        # Card 2: Actualizar base de datos
        card2 = ctk.CTkFrame(scroll_frame, fg_color='#2b2d42', corner_radius=20, border_width=1, border_color='#3a3d5c')
        card2.pack(fill='x', pady=10)

        card2_header = ctk.CTkLabel(
            card2,
            text='2️⃣  Actualizar Base de Datos',
            font=('Segoe UI', 20, 'bold'),
            text_color='#ffffff'
        )
        card2_header.pack(padx=30, pady=(20, 10), anchor='w')

        card2_desc = ctk.CTkLabel(
            card2,
            text='Este proceso actualizará usuarios, módulos y progreso en la BD',
            font=('Segoe UI', 12),
            text_color='#a0a0b0'
        )
        card2_desc.pack(padx=30, pady=(0, 15), anchor='w')

        update_btn = ctk.CTkButton(
            card2,
            text='🔄  Actualizar Base de Datos (Cruce de Datos)',
            font=('Segoe UI', 16, 'bold'),
            fg_color='#51cf66',
            hover_color='#40c057',
            corner_radius=10,
            height=50,
            command=self.update_database_from_file
        )
        update_btn.pack(padx=30, pady=(0, 20))

        # Card 3: Panel de movimientos
        card3 = ctk.CTkFrame(scroll_frame, fg_color='#2b2d42', corner_radius=20, border_width=1, border_color='#3a3d5c')
        card3.pack(fill='both', expand=True, pady=10)

        card3_header = ctk.CTkLabel(
            card3,
            text='📋  Panel de Movimientos',
            font=('Segoe UI', 20, 'bold'),
            text_color='#ffffff'
        )
        card3_header.pack(padx=30, pady=(20, 10), anchor='w')

        # Text area para movimientos
        self.movements_text = ctk.CTkTextbox(
            card3,
            fg_color='#1a1d2e',
            border_color='#3a3d5c',
            border_width=1,
            corner_radius=10,
            font=('Consolas', 11),
            text_color='#ffffff',
            height=300
        )
        self.movements_text.pack(fill='both', expand=True, padx=30, pady=(10, 20))

        # Botón de estadísticas
        stats_btn = ctk.CTkButton(
            card3,
            text='📊  Ver Estadísticas Actuales',
            font=('Segoe UI', 14),
            fg_color='#4ecdc4',
            hover_color='#3dbdb3',
            corner_radius=10,
            height=40,
            command=self.show_progress_stats
        )
        stats_btn.pack(padx=30, pady=(0, 20))

    def show_consultas_panel(self):
        """Panel de consultas - MODERNIZADO"""
        self.clear_content_area()

        # Scroll frame
        scroll_frame = ctk.CTkScrollableFrame(
            self.content_area,
            fg_color='transparent',
            scrollbar_button_color='#3a3d5c'
        )
        scroll_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkFrame(scroll_frame, fg_color='transparent')
        header.pack(fill='x', pady=(0, 30))

        title = ctk.CTkLabel(
            header,
            text='Consultas de Usuarios',
            font=('Segoe UI', 32, 'bold'),
            text_color='#ffffff'
        )
        title.pack(side='left')

        # Card: Búsquedas
        search_card = ctk.CTkFrame(scroll_frame, fg_color='#2b2d42', corner_radius=20, border_width=1, border_color='#3a3d5c')
        search_card.pack(fill='x', pady=10)

        # Búsqueda por ID
        search_id_frame = ctk.CTkFrame(search_card, fg_color='transparent')
        search_id_frame.pack(fill='x', padx=30, pady=20)

        ctk.CTkLabel(
            search_id_frame,
            text='🔍  Buscar Usuario por ID:',
            font=('Segoe UI', 16),
            text_color='#ffffff'
        ).pack(side='left', padx=(0, 15))

        self.search_entry = ctk.CTkEntry(
            search_id_frame,
            placeholder_text='Ingrese ID de usuario...',
            font=('Segoe UI', 14),
            width=300,
            height=40,
            corner_radius=10
        )
        self.search_entry.pack(side='left', padx=5)

        search_btn = ctk.CTkButton(
            search_id_frame,
            text='Buscar',
            font=('Segoe UI', 14),
            fg_color='#6c63ff',
            hover_color='#5a52d5',
            corner_radius=10,
            height=40,
            width=120,
            command=self.search_user_by_id
        )
        search_btn.pack(side='left', padx=10)

        # Separador
        sep = ctk.CTkFrame(search_card, height=1, fg_color='#3a3d5c')
        sep.pack(fill='x', padx=30, pady=10)

        # Búsqueda por Unidad de Negocio
        search_unit_frame = ctk.CTkFrame(search_card, fg_color='transparent')
        search_unit_frame.pack(fill='x', padx=30, pady=20)

        ctk.CTkLabel(
            search_unit_frame,
            text='🏢  Consultar por Unidad de Negocio:',
            font=('Segoe UI', 16),
            text_color='#ffffff'
        ).pack(side='left', padx=(0, 15))

        self.business_unit_var = tk.StringVar()
        self.business_unit_combo = ctk.CTkComboBox(
            search_unit_frame,
            variable=self.business_unit_var,
            font=('Segoe UI', 14),
            width=350,
            height=40,
            corner_radius=10,
            values=['Cargando...']
        )
        self.business_unit_combo.pack(side='left', padx=5)

        # Cargar unidades
        self.load_business_units()

        search_unit_btn = ctk.CTkButton(
            search_unit_frame,
            text='Consultar',
            font=('Segoe UI', 14),
            fg_color='#4ecdc4',
            hover_color='#3dbdb3',
            corner_radius=10,
            height=40,
            width=120,
            command=self.query_business_unit_from_combo
        )
        search_unit_btn.pack(side='left', padx=10)

        # Separador
        sep2 = ctk.CTkFrame(search_card, height=1, fg_color='#3a3d5c')
        sep2.pack(fill='x', padx=30, pady=10)

        # Botones rápidos
        quick_frame = ctk.CTkFrame(search_card, fg_color='transparent')
        quick_frame.pack(fill='x', padx=30, pady=20)

        ctk.CTkLabel(
            quick_frame,
            text='⚡  Consultas Rápidas:',
            font=('Segoe UI', 16),
            text_color='#ffffff'
        ).pack(side='left', padx=(0, 15))

        quick_btn1 = ctk.CTkButton(
            quick_frame,
            text='📋  Todos los Usuarios',
            font=('Segoe UI', 14),
            fg_color='#ff8c42',
            hover_color='#e67a32',
            corner_radius=10,
            height=40,
            command=self.query_new_users
        )
        quick_btn1.pack(side='left', padx=5)

        # Card: Resultados
        results_card = ctk.CTkFrame(scroll_frame, fg_color='#2b2d42', corner_radius=20, border_width=1, border_color='#3a3d5c')
        results_card.pack(fill='both', expand=True, pady=10)

        results_header = ctk.CTkLabel(
            results_card,
            text='📊  Resultados',
            font=('Segoe UI', 20, 'bold'),
            text_color='#ffffff'
        )
        results_header.pack(padx=30, pady=(20, 10), anchor='w')

        # Container para resultados (usaremos tkinter Treeview aquí por compatibilidad)
        results_container = ctk.CTkFrame(results_card, fg_color='#1a1d2e', corner_radius=10)
        results_container.pack(fill='both', expand=True, padx=30, pady=(10, 20))

        # Crear Treeview con estilo oscuro
        import tkinter.ttk as ttk
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.Treeview',
            background='#1a1d2e',
            foreground='#ffffff',
            fieldbackground='#1a1d2e',
            borderwidth=0,
            font=('Segoe UI', 10)
        )
        style.configure('Dark.Treeview.Heading',
            background='#2b2d42',
            foreground='#ffffff',
            borderwidth=1,
            font=('Segoe UI', 11, 'bold')
        )
        style.map('Dark.Treeview',
            background=[('selected', '#6c63ff')],
            foreground=[('selected', '#ffffff')]
        )

        # Scrollbars
        vsb = ttk.Scrollbar(results_container, orient="vertical")
        hsb = ttk.Scrollbar(results_container, orient="horizontal")

        self.results_tree = ttk.Treeview(
            results_container,
            columns=(),
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            style='Dark.Treeview'
        )

        vsb.config(command=self.results_tree.yview)
        hsb.config(command=self.results_tree.xview)

        self.results_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        results_container.grid_rowconfigure(0, weight=1)
        results_container.grid_columnconfigure(0, weight=1)

        # Configurar tags para filas alternadas
        self.results_tree.tag_configure('oddrow', background='#2b2d42')
        self.results_tree.tag_configure('evenrow', background='#1a1d2e')

    def show_configuracion_panel(self):
        """Panel de configuración - MODERNIZADO"""
        self.clear_content_area()

        # Scroll frame
        scroll_frame = ctk.CTkScrollableFrame(
            self.content_area,
            fg_color='transparent',
            scrollbar_button_color='#3a3d5c'
        )
        scroll_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkFrame(scroll_frame, fg_color='transparent')
        header.pack(fill='x', pady=(0, 30))

        title = ctk.CTkLabel(
            header,
            text='Configuración',
            font=('Segoe UI', 32, 'bold'),
            text_color='#ffffff'
        )
        title.pack(side='left')

        # Grid de opciones
        scroll_frame.grid_columnconfigure((0, 1), weight=1)

        # Card 1: Actualizar Correos
        card1 = self._create_config_card(
            scroll_frame,
            icon='📧',
            title='Actualizar Correos',
            description='Actualiza los correos electrónicos de todos los usuarios desde el archivo',
            color='#6c63ff',
            command=self.update_emails
        )
        card1.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        # Card 2: Actualizar Usuarios
        card2 = self._create_config_card(
            scroll_frame,
            icon='👥',
            title='Actualizar Usuarios',
            description='Sincroniza la información de usuarios desde la fuente de datos',
            color='#4ecdc4',
            command=self.update_users
        )
        card2.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        # Card 3: Ver Estadísticas
        card3 = self._create_config_card(
            scroll_frame,
            icon='📊',
            title='Ver Estadísticas',
            description='Muestra estadísticas generales del sistema y progreso',
            color='#51cf66',
            command=self.show_progress_stats
        )
        card3.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        # Card 4: Acerca de
        card4 = self._create_config_card(
            scroll_frame,
            icon='ℹ️',
            title='Acerca de',
            description='Información sobre Smart Reports v2.0',
            color='#ff8c42',
            command=self.show_about
        )
        card4.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

    def _create_config_card(self, parent, icon, title, description, color, command):
        """Crear card de configuración"""
        card = ctk.CTkFrame(
            parent,
            fg_color='#2b2d42',
            corner_radius=20,
            border_width=1,
            border_color='#3a3d5c'
        )

        # Icono
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=('Segoe UI', 48),
            text_color=color
        )
        icon_label.pack(pady=(30, 10))

        # Título
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=('Segoe UI', 20, 'bold'),
            text_color='#ffffff'
        )
        title_label.pack(pady=(0, 10))

        # Descripción
        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=('Segoe UI', 12),
            text_color='#a0a0b0',
            wraplength=250
        )
        desc_label.pack(pady=(0, 20), padx=20)

        # Botón
        action_btn = ctk.CTkButton(
            card,
            text='Ejecutar',
            font=('Segoe UI', 14, 'bold'),
            fg_color=color,
            hover_color=self._darken_color(color),
            corner_radius=10,
            height=40,
            width=150,
            command=command
        )
        action_btn.pack(pady=(0, 30))

        # Hover effect
        card.bind('<Enter>', lambda e: card.configure(border_color=color))
        card.bind('<Leave>', lambda e: card.configure(border_color='#3a3d5c'))

        return card

    def _darken_color(self, hex_color):
        """Oscurecer un color hex"""
        # Simplificado: retornar versión más oscura
        color_map = {
            '#6c63ff': '#5a52d5',
            '#4ecdc4': '#3dbdb3',
            '#51cf66': '#40c057',
            '#ff8c42': '#e67a32'
        }
        return color_map.get(hex_color, hex_color)

    # ==================== FUNCIONES DE DATOS (MANTENER LÓGICA ORIGINAL) ====================

    def select_transcript_file(self):
        """Seleccionar archivo Transcript Status"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Transcript Status",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")]
        )

        if file_path:
            self.current_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.configure(text=filename, text_color='#51cf66')
            self.log_movement(f"Archivo seleccionado: {filename}")
            messagebox.showinfo("Archivo Seleccionado",
                f"Archivo cargado: {filename}\n\nAhora haz clic en 'Actualizar Base de Datos'")

    def update_database_from_file(self):
        """Actualizar base de datos desde archivo cargado"""
        if not self.current_file:
            messagebox.showwarning("Sin Archivo",
                "Primero debes seleccionar un archivo Transcript Status")
            return

        try:
            self.log_movement("="*50)
            self.log_movement("🔄 INICIANDO ACTUALIZACIÓN DE BASE DE DATOS")
            self.log_movement("="*50)

            # Crear procesador
            processor = TranscriptProcessor(self.conn)

            # Procesar archivo
            stats = processor.process_file(self.current_file)

            # Mostrar estadísticas detalladas
            self.show_processing_stats(stats)

            # Mensaje de éxito
            messagebox.showinfo("Actualización Exitosa",
                f"✓ Base de datos actualizada correctamente\n\n" +
                f"Registros procesados: {stats['total_registros']:,}\n" +
                f"Usuarios nuevos: {stats['usuarios_nuevos']}\n" +
                f"Módulos nuevos: {stats['modulos_nuevos']}\n" +
                f"Inscripciones actualizadas: {stats['inscripciones_actualizadas']}")

            self.log_movement("✓ Actualización completada exitosamente")
            self.log_movement("="*50 + "\n")

        except Exception as e:
            error_msg = f"Error al actualizar base de datos: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.log_movement(f"✗ ERROR: {str(e)}")
            import traceback
            self.log_movement(traceback.format_exc())

    def log_movement(self, message):
        """Registrar movimiento en el panel"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        if hasattr(self, 'movements_text'):
            self.movements_text.insert('end', log_entry)
            self.movements_text.see('end')

    def show_processing_stats(self, stats):
        """Mostrar estadísticas de procesamiento"""
        self.log_movement("\n📊 ESTADÍSTICAS DE PROCESAMIENTO:")
        self.log_movement(f"  • Archivo: {stats['archivo']}")
        self.log_movement(f"  • Fecha: {stats['fecha_procesamiento']}")
        self.log_movement(f"  • Total registros: {stats['total_registros']:,}")
        self.log_movement(f"  • Usuarios únicos: {stats['usuarios_unicos']}")
        self.log_movement(f"  • Usuarios nuevos: {stats['usuarios_nuevos']}")
        self.log_movement(f"  • Módulos únicos: {stats['modulos_unicos']}")
        self.log_movement(f"  • Módulos nuevos: {stats['modulos_nuevos']}")
        self.log_movement(f"  • Inscripciones actualizadas: {stats['inscripciones_actualizadas']}")

        if stats['errores']:
            self.log_movement(f"\n⚠️  ERRORES ({len(stats['errores'])}):")
            for error in stats['errores'][:10]:  # Mostrar primeros 10
                self.log_movement(f"  • {error}")

    def search_user_by_id(self):
        """Buscar usuario por ID"""
        user_id = self.search_entry.get().strip()
        if not user_id:
            messagebox.showwarning("Advertencia", "Ingrese un ID de usuario")
            return

        try:
            self.cursor.execute("""
                SELECT
                    u.UserId,
                    u.Nombre,
                    u.Email,
                    un.NombreUnidad,
                    u.Nivel,
                    u.Division,
                    m.NombreModulo,
                    pm.EstatusModuloUsuario,
                    CONVERT(VARCHAR(10), pm.FechaInicio, 103) as FechaAsignacion,
                    CONVERT(VARCHAR(10), pm.FechaFinalizacion, 103) as FechaFinalizacion
                FROM Instituto_Usuario u
                LEFT JOIN Instituto_UnidadDeNegocio un ON u.IdUnidadDeNegocio = un.IdUnidadDeNegocio
                LEFT JOIN Instituto_ProgresoModulo pm ON u.UserId = pm.UserId
                LEFT JOIN Instituto_Modulo m ON pm.IdModulo = m.IdModulo
                WHERE u.UserId = ?
                ORDER BY m.NombreModulo
            """, (user_id,))

            results = self.cursor.fetchall()
            if results:
                self.display_search_results(results,
                    ['User ID', 'Nombre', 'Email', 'Unidad', 'Nivel', 'División',
                     'Módulo', 'Estatus Módulo', 'Fecha Inicio', 'Fecha Fin'])
            else:
                messagebox.showinfo("Sin resultados", "Usuario no encontrado")
        except Exception as e:
            messagebox.showerror("Error", f"Error en búsqueda: {str(e)}")

    def load_business_units(self):
        """Cargar unidades de negocio en combobox"""
        try:
            self.cursor.execute("SELECT DISTINCT NombreUnidad FROM Instituto_UnidadDeNegocio ORDER BY NombreUnidad")
            units = self.cursor.fetchall()
            unit_names = [unit[0] for unit in units]

            if hasattr(self, 'business_unit_combo'):
                self.business_unit_combo.configure(values=unit_names)
                if unit_names:
                    self.business_unit_combo.set(unit_names[0])
        except Exception as e:
            print(f"Error cargando unidades: {e}")

    def query_business_unit_from_combo(self):
        """Consultar por unidad de negocio seleccionada"""
        unit_name = self.business_unit_var.get()
        if not unit_name:
            messagebox.showwarning("Advertencia", "Seleccione una unidad de negocio")
            return

        try:
            self.cursor.execute("""
                SELECT
                    u.UserId,
                    u.Nombre,
                    u.Email,
                    un.NombreUnidad,
                    COUNT(DISTINCT pm.IdModulo) as TotalModulos,
                    SUM(CASE WHEN pm.EstatusModuloUsuario = 'Terminado' THEN 1 ELSE 0 END) as Completados
                FROM Instituto_Usuario u
                JOIN Instituto_UnidadDeNegocio un ON u.IdUnidadDeNegocio = un.IdUnidadDeNegocio
                LEFT JOIN Instituto_ProgresoModulo pm ON u.UserId = pm.UserId
                WHERE un.NombreUnidad = ?
                GROUP BY u.UserId, u.Nombre, u.Email, un.NombreUnidad
                ORDER BY u.Nombre
            """, (unit_name,))

            results = self.cursor.fetchall()
            if results:
                self.display_search_results(results,
                    ['User ID', 'Nombre', 'Email', 'Unidad', 'Total Módulos', 'Completados'])
            else:
                messagebox.showinfo("Sin resultados", f"No hay usuarios en {unit_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Error en consulta: {str(e)}")

    def query_new_users(self):
        """Consultar todos los usuarios"""
        try:
            self.cursor.execute("""
                SELECT
                    u.UserId,
                    u.Nombre,
                    u.Email,
                    un.NombreUnidad,
                    COUNT(DISTINCT pm.IdModulo) as TotalModulos,
                    SUM(CASE WHEN pm.EstatusModuloUsuario = 'Completado' THEN 1 ELSE 0 END) as Completados
                FROM Instituto_Usuario u
                LEFT JOIN Instituto_UnidadDeNegocio un ON u.IdUnidadDeNegocio = un.IdUnidadDeNegocio
                LEFT JOIN Instituto_ProgresoModulo pm ON u.UserId = pm.UserId
                GROUP BY u.UserId, u.Nombre, u.Email, un.NombreUnidad
                ORDER BY u.UserId
            """)

            results = self.cursor.fetchall()
            if results:
                self.display_search_results(results,
                    ['User ID', 'Nombre', 'Email', 'Unidad', 'Total Módulos', 'Completados'])
            else:
                messagebox.showinfo("Sin resultados", "No hay usuarios en el sistema")
        except Exception as e:
            messagebox.showerror("Error", f"Error en consulta: {str(e)}")

    def display_search_results(self, results, columns):
        """Mostrar resultados en treeview"""
        # Limpiar treeview
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Configurar columnas
        self.results_tree['columns'] = columns
        self.results_tree['show'] = 'headings'

        # Diccionario de anchos fijos
        column_widths = {
            'User ID': 100,
            'Nombre': 200,
            'Email': 220,
            'Unidad': 150,
            'Nivel': 100,
            'División': 120,
            'Módulo': 250,
            'Estatus Módulo': 130,
            'Fecha Inicio': 100,
            'Fecha Fin': 100,
            'Total Módulos': 120,
            'Completados': 120
        }

        for col in columns:
            width = column_widths.get(col, 120)
            self.results_tree.heading(col, text=col, anchor='center')
            self.results_tree.column(col, width=width, minwidth=width, anchor='w')

        # Insertar datos con filas alternadas
        for idx, row in enumerate(results):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            values = [str(v) if v is not None else '' for v in row]
            self.results_tree.insert('', 'end', values=values, tags=(tag,))

    def update_emails(self):
        """Actualizar correos"""
        messagebox.showinfo("En Desarrollo", "Funcionalidad de actualizar correos")

    def update_users(self):
        """Actualizar usuarios"""
        messagebox.showinfo("En Desarrollo", "Funcionalidad de actualizar usuarios")

    def show_progress_stats(self):
        """Mostrar estadísticas de progreso"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Instituto_Usuario")
            total_users = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM Instituto_Modulo")
            total_modules = self.cursor.fetchone()[0]

            self.cursor.execute("""
                SELECT
                    SUM(CASE WHEN EstatusModuloUsuario = 'Terminado' THEN 1 ELSE 0 END) as Completados,
                    SUM(CASE WHEN EstatusModuloUsuario = 'En Progreso' THEN 1 ELSE 0 END) as EnProgreso,
                    COUNT(*) as Total
                FROM Instituto_ProgresoModulo
            """)
            result = self.cursor.fetchone()

            msg = f"""
📊 ESTADÍSTICAS GENERALES

Usuarios: {total_users}
Módulos: {total_modules}

Inscripciones Completadas: {result[0]}
En Progreso: {result[1]}
Total Inscripciones: {result[2]}

Porcentaje Completado: {(result[0]/result[2]*100):.1f}%
"""
            messagebox.showinfo("Estadísticas", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Error obteniendo estadísticas: {str(e)}")

    def show_about(self):
        """Mostrar información sobre la aplicación"""
        messagebox.showinfo("Acerca de",
            "SMART REPORTS v2.0\n\n" +
            "Sistema de Gestión de Capacitaciones\n" +
            "Instituto Hutchison Ports\n\n" +
            "© 2025 - Todos los derechos reservados")


def main():
    """Función principal"""
    root = ctk.CTk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
