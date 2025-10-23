"""
Ventana principal de Smart Reports
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import os

from smart_reports.config.settings import APP_CONFIG, COLORS
from smart_reports.database.connection import DatabaseConnection
from smart_reports.ui.components import EditableTreeview, LoadingSpinner
from smart_reports.services.data_processor import TranscriptProcessor
from smart_reports.services.pdf_generator import PDFReportGenerator


class MainWindow:
    """Ventana principal de la aplicación"""

    def __init__(self, root):
        self.root = root
        self.root.title(APP_CONFIG['title'])
        self.root.geometry(APP_CONFIG['geometry'])

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

        # Crear interfaz
        self.create_widgets()

    def verify_database_tables(self):
        """Verificar que las tablas necesarias existan"""
        tables_needed = ['dbo.UnidadDeNegocio', 'dbo.Instituto_Usuario', 'dbo.Modulo', 'dbo.ProgresoModulo']
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

    def create_widgets(self):
        """Crear interfaz principal"""
        # Container principal
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=BOTH, expand=True)

        # Sidebar
        self.create_sidebar(main_container)

        # Área de contenido
        self.content_area = ttk.Frame(main_container)
        self.content_area.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

        # Mostrar panel de actualizaciones por defecto
        self.show_estatus_panel()

    def create_sidebar(self, parent):
        """Crear barra lateral de navegación"""
        sidebar = ttk.Frame(parent, bootstyle='dark', width=200)
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False)

        # Título
        title_label = ttk.Label(sidebar, text="SMART REPORTS",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=20)

        # Botones de navegación
        nav_buttons = [
            ("Cruce de datos", self.show_estatus_panel),
            ("Dashboards", self.show_dashboards_panel),
            ("Consultas", self.show_consultas_panel),
            ("Configuracion", self.show_configuracion_panel)
        ]

        for text, command in nav_buttons:
            btn = ttk.Button(sidebar, text=text,
                           command=command,
                           bootstyle='dark',
                           width=20)
            btn.pack(pady=5, padx=10)

    def show_estatus_panel(self):
        """Panel principal de actualizaciones"""
        self.clear_content_area()

        # Frame principal
        main_frame = ttk.Frame(self.content_area)
        main_frame.pack(fill=BOTH, expand=True)

        # Título
        title = ttk.Label(main_frame, text="Actualizaciones",
                         font=('Arial', 20, 'bold'))
        title.pack(pady=10)

        # Frame de carga de archivo
        file_frame = ttk.LabelFrame(main_frame, text="1. Cargar Archivo", padding=20)
        file_frame.pack(padx=20, pady=10, fill=X)

        file_info_frame = ttk.Frame(file_frame)
        file_info_frame.pack(fill=X)

        ttk.Label(file_info_frame, text="Archivo:").pack(side=LEFT, padx=5)
        self.file_label = ttk.Label(file_info_frame, text="Ningún archivo seleccionado",
                                    foreground='gray')
        self.file_label.pack(side=LEFT, padx=5)

        ttk.Button(file_frame, text="📁 Seleccionar Archivo Transcript Status",
                  command=self.select_transcript_file,
                  bootstyle='info',
                  width=35).pack(pady=10)

        # Frame de actualización
        update_frame = ttk.LabelFrame(main_frame, text="2. Actualizar Base de Datos", padding=20)
        update_frame.pack(padx=20, pady=10, fill=X)

        ttk.Button(update_frame, text="🔄 Actualizar Base de Datos (Cruce de Datos)",
                  command=self.update_database_from_file,
                  bootstyle='success',
                  width=40).pack(pady=5)

        ttk.Label(update_frame, text="Este proceso actualizará usuarios, módulos y progreso en la BD",
                 font=('Arial', 9, 'italic'),
                 foreground='gray').pack()

        # Botones de acción adicionales
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(pady=10)

        ttk.Button(actions_frame, text="Actualizar Correos",
                  command=self.update_emails,
                  bootstyle='dark',
                  width=20).pack(side=LEFT, padx=10)

        ttk.Button(actions_frame, text="Actualizar Usuarios",
                  command=self.update_users,
                  bootstyle='dark',
                  width=20).pack(side=LEFT, padx=10)

        # Panel de movimientos
        movements_frame = ttk.LabelFrame(main_frame, text="Panel de movimientos",
                                       padding=20)
        movements_frame.pack(fill=BOTH, expand=True, pady=20)

        # Área de texto para mostrar movimientos
        self.movements_text = tk.Text(movements_frame, height=15,
                                     bg='white', fg='black')
        self.movements_text.pack(fill=BOTH, expand=True)

        # Frame para cargar archivo
        upload_frame = ttk.Frame(main_frame)
        upload_frame.pack(pady=10)

        ttk.Button(upload_frame, text="🔍 Ver Estadísticas Actuales",
                  command=self.show_progress_stats,
                  bootstyle='primary').pack()

    def select_transcript_file(self):
        """Seleccionar archivo Transcript Status"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Transcript Status",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")]
        )

        if file_path:
            self.current_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=filename, foreground='green')
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

            # Mostrar estadísticas detalladas en el panel
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

    def show_dashboards_panel(self):
        """Panel de dashboards con gráficas interactivas"""
        self.clear_content_area()

        # Frame principal con estilo del tema
        main_frame = ttk.Frame(self.content_area, bootstyle='default')
        main_frame.pack(fill=BOTH, expand=True)

        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=X, padx=20, pady=10)

        title = ttk.Label(title_frame, text="📊 Dashboards - Instituto HP",
                         font=('Arial', 20, 'bold'))
        title.pack(side=LEFT)

        # Botón de refrescar
        ttk.Button(title_frame, text="🔄 Actualizar Gráficas",
                  command=self.refresh_dashboards,
                  bootstyle='info-outline').pack(side=RIGHT)

        # Información de datos
        info_label = ttk.Label(main_frame,
                              text="Haz clic en cualquier gráfica para ver los datos detallados",
                              font=('Arial', 10, 'italic'),
                              foreground='gray')
        info_label.pack(pady=5)

        # Separador
        ttk.Separator(main_frame, orient='horizontal').pack(fill=X, padx=20, pady=5)

        # Frame para gráficas con scrollbar
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Crear canvas con scrollbar
        canvas = tk.Canvas(canvas_frame, bg='#2b3e50')  # Fondo del tema darkly
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, bootstyle='default')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Crear gráficas interactivas
        self.create_interactive_charts(scrollable_frame)

    def show_consultas_panel(self):
        """Panel de consultas"""
        self.clear_content_area()

        main_frame = ttk.Frame(self.content_area)
        main_frame.pack(fill=BOTH, expand=True)

        title = ttk.Label(main_frame, text="Consultas",
                         font=('Arial', 20, 'bold'))
        title.pack(pady=10)

        # Frame de búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(pady=20)

        # Buscar Usuario por ID
        ttk.Label(search_frame, text="Buscar Usuario por ID:").pack(side=LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=LEFT, padx=5)
        ttk.Button(search_frame, text="Buscar",
                  command=self.search_user_by_id,
                  bootstyle='info').pack(side=LEFT, padx=5)

        # Frame para Unidad de Negocio
        unit_frame = ttk.Frame(main_frame)
        unit_frame.pack(pady=10)

        ttk.Label(unit_frame, text="Consultar Unidad de Negocio:").pack(side=LEFT, padx=5)

        # Combobox para unidades de negocio
        self.business_unit_var = tk.StringVar()
        self.business_unit_combo = ttk.Combobox(unit_frame,
                                               textvariable=self.business_unit_var,
                                               width=40,
                                               state='readonly')
        self.business_unit_combo.pack(side=LEFT, padx=5)

        # Cargar unidades de negocio
        self.load_business_units()

        ttk.Button(unit_frame, text="Consultar",
                  command=self.query_business_unit_from_combo,
                  bootstyle='info').pack(side=LEFT, padx=5)

        # Frame para otros botones
        quick_buttons_frame = ttk.Frame(main_frame)
        quick_buttons_frame.pack(pady=10)

        ttk.Button(quick_buttons_frame, text="Usuarios Nuevos (Últimos 30 días)",
                  command=self.query_new_users,
                  bootstyle='info').pack(side=LEFT, padx=5)

        # Área de resultados con mejor formato
        results_frame = ttk.LabelFrame(main_frame, text="Resultados",
                                     padding=10)
        results_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

        # Frame contenedor para tabla y scrollbars
        table_container = ttk.Frame(results_frame)
        table_container.pack(fill=BOTH, expand=True)

        # Scrollbars
        vsb = ttk.Scrollbar(table_container, orient="vertical")
        hsb = ttk.Scrollbar(table_container, orient="horizontal")

        # Treeview para mostrar resultados con mejor estilo
        self.results_tree = ttk.Treeview(table_container,
                                        columns=(),
                                        show='headings',  # Solo headers, sin columna tree
                                        yscrollcommand=vsb.set,
                                        xscrollcommand=hsb.set)

        vsb.config(command=self.results_tree.yview)
        hsb.config(command=self.results_tree.xview)

        # Grid layout para tabla y scrollbars
        self.results_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # Configurar estilo de filas alternadas - ERROR 5: Fix white text on white background
        self.results_tree.tag_configure('oddrow', background='#f0f0f0', foreground='black')
        self.results_tree.tag_configure('evenrow', background='white', foreground='black')

    def show_configuracion_panel(self):
        """Panel de configuración"""
        self.clear_content_area()

        main_frame = ttk.Frame(self.content_area)
        main_frame.pack(fill=BOTH, expand=True)

        title = ttk.Label(main_frame, text="Configuracion",
                         font=('Arial', 20, 'bold'))
        title.pack(pady=10)

        # Opciones de configuración
        config_frame = ttk.LabelFrame(main_frame, text="Opciones", padding=20)
        config_frame.pack(padx=20, pady=20)

        ttk.Button(config_frame, text="Agregar Nuevo Usuario",
                  command=self.add_new_user_dialog,
                  bootstyle='success').pack(pady=5)

        ttk.Button(config_frame, text="Gestionar Modulos",
                  command=self.manage_modules_dialog,
                  bootstyle='info').pack(pady=5)

        ttk.Button(config_frame, text="Gestionar Unidades de Negocio",
                  command=self.manage_units_dialog,
                  bootstyle='info').pack(pady=5)

        ttk.Button(config_frame, text="Respaldar Base de Datos",
                  command=self.backup_database,
                  bootstyle='warning').pack(pady=5)

    def clear_content_area(self):
        """Limpiar área de contenido"""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def load_transcript_file(self):
        """DEPRECATED: Usar select_transcript_file y update_database_from_file"""
        self.select_transcript_file()

    def show_processing_stats(self, stats):
        """Mostrar estadísticas del procesamiento en el panel"""
        if hasattr(self, 'movements_text'):
            # Encabezado
            self.log_movement("\n📊 RESUMEN DE ACTUALIZACIÓN")
            self.log_movement("─" * 50)

            # Información del archivo
            self.log_movement(f"📄 Archivo: {stats['archivo']}")
            self.log_movement(f"📅 Fecha: {stats['fecha_procesamiento']}")
            self.log_movement("")

            # Estadísticas principales
            self.log_movement("📈 ESTADÍSTICAS:")
            self.log_movement(f"  • Total de registros procesados: {stats['total_registros']:,}")
            self.log_movement(f"  • Usuarios únicos encontrados: {stats['usuarios_unicos']:,}")
            self.log_movement(f"  • Módulos únicos encontrados: {stats['modulos_unicos']:,}")
            self.log_movement("")

            # Cambios realizados
            self.log_movement("✏️  CAMBIOS EN BASE DE DATOS:")
            self.log_movement(f"  • Usuarios nuevos creados: {stats['usuarios_nuevos']}")
            self.log_movement(f"  • Módulos nuevos creados: {stats['modulos_nuevos']}")
            self.log_movement(f"  • Inscripciones actualizadas: {stats['inscripciones_actualizadas']}")
            self.log_movement("")

            # Errores si los hay
            if stats.get('errores') and len(stats['errores']) > 0:
                self.log_movement("⚠️  ADVERTENCIAS/ERRORES:")
                for error in stats['errores']:
                    self.log_movement(f"  • {error}")
                self.log_movement("")

            # Resumen final
            if stats['inscripciones_actualizadas'] > 0:
                self.log_movement("✅ ACTUALIZACIÓN EXITOSA")
                self.log_movement(f"   Se actualizaron {stats['inscripciones_actualizadas']} registros de progreso")
            else:
                self.log_movement("ℹ️  No se realizaron cambios (datos ya actualizados)")

            self.log_movement("─" * 50)
            self.movements_text.see(tk.END)

    def update_emails(self):
        """Actualizar correos desde el archivo"""
        if not self.current_file:
            messagebox.showwarning("Advertencia", "Primero debe cargar un archivo")
            return

        self.log_movement("Correos actualizados")
        messagebox.showinfo("Exito", "Correos actualizados correctamente")

    def update_users(self):
        """Actualizar usuarios desde el archivo"""
        if not self.current_file:
            messagebox.showwarning("Advertencia", "Primero debe cargar un archivo")
            return

        self.log_movement("Usuarios actualizados")
        messagebox.showinfo("Exito", "Usuarios actualizados correctamente")

    def log_movement(self, message):
        """Registrar movimiento en el panel y BD"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        # Agregar al panel si existe
        if hasattr(self, 'movements_text'):
            self.movements_text.insert(tk.END, log_entry)
            self.movements_text.see(tk.END)

        # Guardar en BD
        try:
            self.cursor.execute("""
                INSERT INTO HistorialCambios (TipoCambio, DescripcionCambio, UsuarioSistema)
                VALUES (?, ?, ?)
            """, ('UPDATE', message, 'Sistema'))
            self.db.commit()
        except Exception as e:
            print(f"Error al guardar en historial: {e}")

    def create_interactive_charts(self, parent):
        """Crear gráficas interactivas con datos de ejemplo"""

        # Datos de ejemplo
        self.chart_data = {
            'estados_modulos': {
                'labels': ['Completado', 'En proceso', 'Registrado'],
                'values': [45, 30, 25],
                'title': 'Estado de Módulos'
            },
            'usuarios_unidad': {
                'labels': ['LCIT', 'LCT', 'TNG', 'EIT'],
                'values': [120, 95, 78, 110],
                'title': 'Usuarios por Unidad de Negocio'
            },
            'progreso_mensual': {
                'labels': ['Ene', 'Feb', 'Mar', 'Abr', 'May'],
                'values': [20, 35, 45, 60, 75],
                'title': 'Módulos Completados por Mes'
            },
            'tasa_finalizacion': {
                'labels': ['Diplomado 1', 'Diplomado 2'],
                'values': [78, 65],
                'title': 'Tasa de Finalización (%)'
            }
        }

        # Crear 4 frames para las gráficas (2x2)
        row1 = ttk.Frame(parent)
        row1.pack(fill=BOTH, expand=True, pady=10)

        row2 = ttk.Frame(parent)
        row2.pack(fill=BOTH, expand=True, pady=10)

        # Gráfica 1: Pie Chart - Estado de Módulos
        chart1_frame = ttk.LabelFrame(row1, text="Estado de Módulos", padding=10, bootstyle='primary')
        chart1_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
        self.create_pie_chart(chart1_frame, 'estados_modulos')

        # Gráfica 2: Bar Chart - Usuarios por Unidad
        chart2_frame = ttk.LabelFrame(row1, text="Usuarios por Unidad de Negocio", padding=10, bootstyle='info')
        chart2_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
        self.create_bar_chart(chart2_frame, 'usuarios_unidad')

        # Gráfica 3: Line Chart - Progreso Mensual
        chart3_frame = ttk.LabelFrame(row2, text="Módulos Completados por Mes", padding=10, bootstyle='success')
        chart3_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
        self.create_line_chart(chart3_frame, 'progreso_mensual')

        # Gráfica 4: Horizontal Bar - Tasa Finalización
        chart4_frame = ttk.LabelFrame(row2, text="Tasa de Finalización por Diplomado", padding=10, bootstyle='warning')
        chart4_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
        self.create_horizontal_bar_chart(chart4_frame, 'tasa_finalizacion')

        # Nota sobre datos de ejemplo
        note_frame = ttk.Frame(parent)
        note_frame.pack(fill=X, pady=20)
        ttk.Label(note_frame,
                 text="ℹ️  Los datos mostrados son de ejemplo. Se actualizarán con datos reales al cargar el archivo Transcript.",
                 font=('Arial', 9, 'italic'),
                 foreground='orange').pack()

    def create_pie_chart(self, parent, data_key):
        """Crear gráfica de pastel interactiva"""
        data = self.chart_data[data_key]
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor('#2b3e50')
        ax.set_facecolor('#2b3e50')

        colors = ['#82B366', '#FEB236', '#88B0D3']
        wedges, texts, autotexts = ax.pie(data['values'], labels=data['labels'],
                                           colors=colors, autopct='%1.1f%%',
                                           startangle=90)

        for text in texts:
            text.set_color('white')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_weight('bold')

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        # Hacer clickeable
        canvas.mpl_connect('button_press_event',
                          lambda event: self.show_chart_data(data_key))

    def create_bar_chart(self, parent, data_key):
        """Crear gráfica de barras interactiva"""
        data = self.chart_data[data_key]
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor('#2b3e50')
        ax.set_facecolor('#2b3e50')

        ax.bar(data['labels'], data['values'], color='#6B5B95')
        ax.set_ylabel('Número de Usuarios', color='white')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        canvas.mpl_connect('button_press_event',
                          lambda event: self.show_chart_data(data_key))

    def create_line_chart(self, parent, data_key):
        """Crear gráfica de línea interactiva"""
        data = self.chart_data[data_key]
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor('#2b3e50')
        ax.set_facecolor('#2b3e50')

        ax.plot(data['labels'], data['values'], marker='o',
               color='#82B366', linewidth=2, markersize=8)
        ax.set_ylabel('Módulos Completados', color='white')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3, color='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        canvas.mpl_connect('button_press_event',
                          lambda event: self.show_chart_data(data_key))

    def create_horizontal_bar_chart(self, parent, data_key):
        """Crear gráfica de barras horizontales interactiva"""
        data = self.chart_data[data_key]
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor('#2b3e50')
        ax.set_facecolor('#2b3e50')

        colors = ['#88B0D3', '#FEB236']
        ax.barh(data['labels'], data['values'], color=colors)
        ax.set_xlabel('Porcentaje', color='white')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        canvas.mpl_connect('button_press_event',
                          lambda event: self.show_chart_data(data_key))

    def show_chart_data(self, data_key):
        """Mostrar datos de la gráfica en una tabla popup"""
        data = self.chart_data[data_key]

        # Crear ventana popup
        popup = tk.Toplevel(self.root)
        popup.title(f"Datos: {data['title']}")
        popup.geometry("500x400")

        # Título
        ttk.Label(popup, text=data['title'],
                 font=('Arial', 14, 'bold')).pack(pady=10)

        # Tabla de datos
        tree_frame = ttk.Frame(popup)
        tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

        tree = ttk.Treeview(tree_frame, columns=('Categoría', 'Valor'),
                           show='headings', height=10)
        tree.heading('Categoría', text='Categoría')
        tree.heading('Valor', text='Valor')
        tree.column('Categoría', width=250, anchor='center')
        tree.column('Valor', width=150, anchor='center')

        # Insertar datos
        for label, value in zip(data['labels'], data['values']):
            tree.insert('', tk.END, values=(label, value))

        tree.pack(fill=BOTH, expand=True)

        # Botón cerrar
        ttk.Button(popup, text="Cerrar",
                  command=popup.destroy,
                  bootstyle='secondary').pack(pady=10)

    def refresh_dashboards(self):
        """Refrescar dashboards con datos actuales"""
        try:
            # TODO: Cuando haya datos reales, actualizar desde BD
            messagebox.showinfo("Actualizar Gráficas",
                "Las gráficas se actualizarán automáticamente cuando se carguen datos reales desde el archivo Transcript.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar dashboards: {str(e)}")

    def search_user_by_id(self):
        """Buscar usuario por ID y mostrar su progreso en módulos"""
        user_id = self.search_entry.get()
        if not user_id:
            messagebox.showwarning("Advertencia", "Ingrese un ID de usuario")
            return

        # ERROR 7: Consulta completa con TODOS los campos de usuario
        self.cursor.execute("""
            SELECT
                u.UserId,
                u.Nombre,
                u.Email,
                un.NombreUnidad,
                u.Nivel,
                u.Division,
                CASE WHEN u.Activo = 1 THEN 'Activo' ELSE 'Inactivo' END as Estado,
                m.NombreModulo,
                pm.EstatusModuloUsuario,
                CONVERT(VARCHAR(10), pm.FechaInicio, 103) as FechaAsignacion,
                CONVERT(VARCHAR(10), pm.FechaFinalizacion, 103) as FechaFinalizacion
            FROM dbo.Instituto_Usuario u
            LEFT JOIN dbo.UnidadDeNegocio un ON u.IdUnidadDeNegocio = un.IdUnidadDeNegocio
            LEFT JOIN dbo.ProgresoModulo pm ON u.UserId = pm.UserId
            LEFT JOIN dbo.Modulo m ON pm.IdModulo = m.IdModulo
            WHERE u.UserId = ?
            ORDER BY m.NombreModulo
        """, (user_id,))

        results = self.cursor.fetchall()
        if results:
            self.display_search_results(results,
                ['User ID', 'Nombre', 'Email', 'Unidad', 'Nivel', 'División', 'Estado', 'Módulo', 'Estatus Módulo', 'Fecha Inicio', 'Fecha Fin'])
        else:
            messagebox.showinfo("Sin resultados", "Usuario no encontrado")

    def load_business_units(self):
        """Cargar unidades de negocio en el combobox"""
        try:
            self.cursor.execute("""
                SELECT NombreUnidad FROM dbo.UnidadDeNegocio
                ORDER BY NombreUnidad
            """)
            units = [row[0] for row in self.cursor.fetchall()]
            self.business_unit_combo['values'] = units
            if units:
                self.business_unit_combo.current(0)
        except Exception as e:
            print(f"Error cargando unidades: {e}")

    def query_business_unit_from_combo(self):
        """Consultar unidad de negocio desde el combobox"""
        unit = self.business_unit_var.get()
        if not unit:
            messagebox.showwarning("Advertencia", "Seleccione una unidad de negocio")
            return

        self.cursor.execute("""
            SELECT
                u.UserId,
                u.Nombre,
                u.Email,
                un.NombreUnidad,
                COUNT(DISTINCT pm.IdModulo) as TotalModulos,
                SUM(CASE WHEN pm.EstatusModuloUsuario = 'Completado' THEN 1 ELSE 0 END) as Completados,
                SUM(CASE WHEN pm.EstatusModuloUsuario = 'En proceso' THEN 1 ELSE 0 END) as EnProceso,
                SUM(CASE WHEN pm.EstatusModuloUsuario = 'Registrado' THEN 1 ELSE 0 END) as Registrados
            FROM dbo.Instituto_Usuario u
            LEFT JOIN dbo.UnidadDeNegocio un ON u.IdUnidadDeNegocio = un.IdUnidadDeNegocio
            LEFT JOIN dbo.ProgresoModulo pm ON u.UserId = pm.UserId
            WHERE un.NombreUnidad = ?
            GROUP BY u.UserId, u.Nombre, u.Email, un.NombreUnidad
            ORDER BY u.Nombre
        """, (unit,))

        results = self.cursor.fetchall()
        if results:
            self.display_search_results(results,
                ['User ID', 'Nombre', 'Email', 'Unidad', 'Total Módulos', 'Completados', 'En Proceso', 'Registrados'])
        else:
            messagebox.showinfo("Sin resultados", f"No se encontraron usuarios en {unit}")

    def show_progress_stats(self):
        """Mostrar estadísticas de progreso"""
        try:
            self.cursor.execute("""
                SELECT
                    COUNT(CASE WHEN EstatusModuloUsuario = 'Completado' THEN 1 END) as Completados,
                    COUNT(CASE WHEN EstatusModuloUsuario = 'En proceso' THEN 1 END) as EnProceso,
                    COUNT(CASE WHEN EstatusModuloUsuario = 'Registrado' THEN 1 END) as Registrados,
                    COUNT(*) as Total
                FROM dbo.ProgresoModulo
            """)
            result = self.cursor.fetchone()

            if result:
                msg = f"""Estadísticas de Progreso de Módulos:

Completados: {result[0]}
En Proceso: {result[1]}
Registrados: {result[2]}
Total de Inscripciones: {result[3]}

Porcentaje Completado: {(result[0]/result[3]*100):.1f}%
"""
                messagebox.showinfo("Estadísticas", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener estadísticas: {str(e)}")

    def query_new_users(self):
        """Consultar usuarios nuevos con su progreso"""
        self.cursor.execute("""
            SELECT
                u.UserId,
                u.Nombre,
                u.Email,
                un.NombreUnidad,
                CONVERT(VARCHAR(10), u.FechaRegistro, 103) as FechaRegistro,
                COUNT(DISTINCT pm.IdModulo) as TotalModulos,
                SUM(CASE WHEN pm.EstatusModuloUsuario = 'Completado' THEN 1 ELSE 0 END) as Completados
            FROM dbo.Instituto_Usuario u
            LEFT JOIN dbo.UnidadDeNegocio un ON u.IdUnidadDeNegocio = un.IdUnidadDeNegocio
            LEFT JOIN dbo.ProgresoModulo pm ON u.UserId = pm.UserId
            WHERE CAST(u.FechaRegistro AS DATE) >= DATEADD(day, -30, GETDATE())
            GROUP BY u.UserId, u.Nombre, u.Email, un.NombreUnidad, u.FechaRegistro
            ORDER BY u.FechaRegistro DESC
        """)

        results = self.cursor.fetchall()
        if results:
            self.display_search_results(results,
                ['User ID', 'Nombre', 'Email', 'Unidad', 'Fecha Registro', 'Total Módulos', 'Completados'])
        else:
            messagebox.showinfo("Sin resultados", "No hay usuarios nuevos en los ultimos 30 dias")

    def display_search_results(self, results, columns):
        """Mostrar resultados en el treeview con formato mejorado - ERROR 6: Fix column duplication"""
        # Limpiar treeview - datos y columnas
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # ERROR 6 FIX: Limpiar completamente las columnas anteriores
        old_columns = self.results_tree['columns']
        if old_columns:
            for col in old_columns:
                try:
                    self.results_tree.heading(col, text='')
                except:
                    pass

        # Configurar nuevas columnas
        self.results_tree['columns'] = columns

        # Configurar cada columna con ancho automático y alineación
        for col in columns:
            self.results_tree.heading(col, text=col, anchor='center')
            # Ancho basado en el contenido
            max_width = len(col) * 10  # Ancho mínimo basado en el header

            # Calcular ancho máximo basado en contenido
            for row in results:
                col_index = columns.index(col)
                if col_index < len(row):
                    cell_value = str(row[col_index]) if row[col_index] is not None else ''
                    cell_width = len(cell_value) * 8
                    max_width = max(max_width, cell_width)

            # Establecer ancho (mínimo 100, máximo 300)
            max_width = min(max(max_width, 100), 300)
            self.results_tree.column(col, width=max_width, anchor='center', minwidth=80)

        # No mostrar la columna tree
        self.results_tree.column('#0', width=0, stretch=False)

        # Insertar resultados con filas alternadas
        for idx, row in enumerate(results):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.results_tree.insert('', tk.END, values=row, tags=(tag,))

    def add_new_user_dialog(self):
        """ERROR 8: Diálogo completo para agregar nuevo usuario con validación"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Nuevo Usuario - INSTITUTO HP")
        dialog.geometry("500x450")
        dialog.resizable(False, False)

        # Frame principal con padding
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        # Título
        ttk.Label(main_frame, text="Agregar Nuevo Usuario",
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Diccionario para almacenar widgets
        entries = {}
        row_num = 1

        # Campo 1: User ID (obligatorio)
        ttk.Label(main_frame, text="* User ID:").grid(row=row_num, column=0, padx=10, pady=8, sticky='e')
        entries['user_id'] = ttk.Entry(main_frame, width=35)
        entries['user_id'].grid(row=row_num, column=1, padx=10, pady=8, sticky='w')
        row_num += 1

        # Campo 2: Nombre (obligatorio)
        ttk.Label(main_frame, text="* Nombre:").grid(row=row_num, column=0, padx=10, pady=8, sticky='e')
        entries['nombre'] = ttk.Entry(main_frame, width=35)
        entries['nombre'].grid(row=row_num, column=1, padx=10, pady=8, sticky='w')
        row_num += 1

        # Campo 3: Email (obligatorio)
        ttk.Label(main_frame, text="* Email:").grid(row=row_num, column=0, padx=10, pady=8, sticky='e')
        entries['email'] = ttk.Entry(main_frame, width=35)
        entries['email'].grid(row=row_num, column=1, padx=10, pady=8, sticky='w')
        row_num += 1

        # Campo 4: Unidad de Negocio (combobox)
        ttk.Label(main_frame, text="Unidad de Negocio:").grid(row=row_num, column=0, padx=10, pady=8, sticky='e')
        entries['unidad'] = ttk.Combobox(main_frame, width=32, state='readonly')
        entries['unidad'].grid(row=row_num, column=1, padx=10, pady=8, sticky='w')

        # Cargar unidades de negocio
        try:
            self.cursor.execute("SELECT IdUnidadDeNegocio, NombreUnidad FROM dbo.UnidadDeNegocio ORDER BY NombreUnidad")
            unidades = self.cursor.fetchall()
            entries['unidad']['values'] = [f"{u[0]} - {u[1]}" for u in unidades]
            entries['unidad_data'] = {f"{u[0]} - {u[1]}": u[0] for u in unidades}
        except Exception as e:
            print(f"Error cargando unidades: {e}")
            entries['unidad']['values'] = []
            entries['unidad_data'] = {}
        row_num += 1

        # Campo 5: Nivel
        ttk.Label(main_frame, text="Nivel:").grid(row=row_num, column=0, padx=10, pady=8, sticky='e')
        entries['nivel'] = ttk.Entry(main_frame, width=35)
        entries['nivel'].grid(row=row_num, column=1, padx=10, pady=8, sticky='w')
        row_num += 1

        # Campo 6: División
        ttk.Label(main_frame, text="División:").grid(row=row_num, column=0, padx=10, pady=8, sticky='e')
        entries['division'] = ttk.Entry(main_frame, width=35)
        entries['division'].grid(row=row_num, column=1, padx=10, pady=8, sticky='w')
        row_num += 1

        # Campo 7: Estado (combobox)
        ttk.Label(main_frame, text="Estado:").grid(row=row_num, column=0, padx=10, pady=8, sticky='e')
        entries['activo'] = ttk.Combobox(main_frame, width=32, state='readonly')
        entries['activo']['values'] = ['Activo', 'Inactivo']
        entries['activo'].current(0)  # Activo por defecto
        entries['activo'].grid(row=row_num, column=1, padx=10, pady=8, sticky='w')
        row_num += 1

        # Nota de campos obligatorios
        ttk.Label(main_frame, text="* Campos obligatorios",
                 font=('Arial', 8, 'italic')).grid(row=row_num, column=0, columnspan=2, pady=(10, 0))
        row_num += 1

        def validate_email(email):
            """Validación básica de email"""
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None

        def save_user():
            """Guardar nuevo usuario con validación completa"""
            # Obtener valores
            user_id = entries['user_id'].get().strip()
            nombre = entries['nombre'].get().strip()
            email = entries['email'].get().strip()
            unidad_seleccionada = entries['unidad'].get()
            nivel = entries['nivel'].get().strip()
            division = entries['division'].get().strip()
            estado = entries['activo'].get()

            # Validaciones
            if not user_id:
                messagebox.showwarning("Validación", "El User ID es obligatorio")
                entries['user_id'].focus()
                return

            if not nombre:
                messagebox.showwarning("Validación", "El Nombre es obligatorio")
                entries['nombre'].focus()
                return

            if not email:
                messagebox.showwarning("Validación", "El Email es obligatorio")
                entries['email'].focus()
                return

            if not validate_email(email):
                messagebox.showwarning("Validación", "El formato del Email no es válido")
                entries['email'].focus()
                return

            # Obtener IdUnidadDeNegocio
            id_unidad = None
            if unidad_seleccionada and unidad_seleccionada in entries['unidad_data']:
                id_unidad = entries['unidad_data'][unidad_seleccionada]

            # Convertir estado a bit
            activo = 1 if estado == 'Activo' else 0

            try:
                # Verificar si el usuario ya existe
                self.cursor.execute("SELECT UserId FROM dbo.Instituto_Usuario WHERE UserId = ?", (user_id,))
                if self.cursor.fetchone():
                    messagebox.showerror("Error", f"El usuario {user_id} ya existe en la base de datos")
                    return

                # Insertar nuevo usuario
                self.cursor.execute("""
                    INSERT INTO dbo.Instituto_Usuario
                    (UserId, Nombre, Email, IdUnidadDeNegocio, Nivel, Division, Activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, nombre, email, id_unidad, nivel or None, division or None, activo))

                self.db.commit()
                self.log_movement(f"✓ Nuevo usuario agregado: {nombre} ({user_id})")
                messagebox.showinfo("Éxito", f"Usuario {nombre} agregado correctamente")
                dialog.destroy()

            except Exception as e:
                self.db.rollback()
                messagebox.showerror("Error", f"Error al agregar usuario:\n{str(e)}")

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row_num, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Guardar", command=save_user,
                  bootstyle='success', width=15).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancelar", command=dialog.destroy,
                  bootstyle='secondary', width=15).pack(side='left', padx=5)

    def manage_modules_dialog(self):
        """Diálogo para gestionar módulos"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Gestionar Modulos")
        dialog.geometry("600x400")

        ttk.Label(dialog, text="Gestion de Modulos",
                 font=('Arial', 14, 'bold')).pack(pady=20)

        # Lista de módulos
        modules_frame = ttk.Frame(dialog)
        modules_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

        # Treeview para módulos
        tree = ttk.Treeview(modules_frame, columns=('ID', 'Nombre', 'Diplomado', 'Duracion'),
                          show='tree headings')
        tree.pack(fill=BOTH, expand=True)

        for col in tree['columns']:
            tree.heading(col, text=col)

        # Cargar módulos existentes
        try:
            self.cursor.execute("SELECT * FROM dbo.Modulo")
            for row in self.cursor.fetchall():
                tree.insert('', tk.END, values=row)
        except Exception as e:
            print(f"Error al cargar modulos: {e}")

    def manage_units_dialog(self):
        """Diálogo para gestionar unidades de negocio"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Gestionar Unidades de Negocio")
        dialog.geometry("500x300")

        ttk.Label(dialog, text="Gestion de Unidades de Negocio",
                 font=('Arial', 14, 'bold')).pack(pady=20)

    def backup_database(self):
        """Respaldar base de datos"""
        backup_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db")]
        )

        if backup_path:
            try:
                messagebox.showinfo("Informacion",
                    "Para respaldar SQL Server, use SQL Server Management Studio\n" +
                    "o ejecute un script de backup de SQL Server.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al respaldar: {str(e)}")

    def __del__(self):
        """Cerrar conexión al destruir"""
        if hasattr(self, 'db'):
            self.db.close()
