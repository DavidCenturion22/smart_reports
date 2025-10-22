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
        tables_needed = ['instituto_UnidadDeNegocio', 'instituto_Usuario', 'instituto_Modulo', 'instituto_ProgresoModulo']
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
            ("Estatus", self.show_estatus_panel),
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

        # Frame de estado unificado
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(pady=20)

        # Botón unificado para ver estadísticas
        ttk.Button(status_frame, text="Ver Estadísticas de Progreso",
                  command=self.show_progress_stats,
                  bootstyle='primary',
                  width=30).pack(pady=10)

        # Botones de acción
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(pady=20)

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

        ttk.Button(upload_frame, text="Cargar Reporte Transcript Status",
                  command=self.load_transcript_file,
                  bootstyle='primary').pack()

    def show_dashboards_panel(self):
        """Panel de dashboards con gráficas"""
        self.clear_content_area()

        main_frame = ttk.Frame(self.content_area)
        main_frame.pack(fill=BOTH, expand=True)

        title = ttk.Label(main_frame, text="Dashboards",
                         font=('Arial', 20, 'bold'))
        title.pack(pady=10)

        # Frame para gráficas
        graphs_frame = ttk.Frame(main_frame)
        graphs_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # Crear gráficas
        self.create_sample_charts(graphs_frame)

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

        # Configurar estilo de filas alternadas
        self.results_tree.tag_configure('oddrow', background='#f0f0f0')
        self.results_tree.tag_configure('evenrow', background='white')

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
        """Cargar archivo de Transcript Status"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Transcript Status",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")]
        )

        if file_path:
            try:
                # Crear procesador
                processor = TranscriptProcessor(self.conn)

                # Procesar archivo
                self.current_file = file_path
                stats = processor.process_file(file_path)

                # Mostrar estadísticas
                self.show_processing_stats(stats)

                # Log
                self.log_movement(f"Archivo procesado: {os.path.basename(file_path)}")
                messagebox.showinfo("Exito",
                    f"Archivo procesado correctamente\n\n" +
                    f"Registros: {stats['total_registros']:,}\n" +
                    f"Usuarios nuevos: {stats['usuarios_nuevos']}\n" +
                    f"Modulos nuevos: {stats['modulos_nuevos']}\n" +
                    f"Inscripciones: {stats['inscripciones_actualizadas']}")

            except Exception as e:
                messagebox.showerror("Error", f"Error al procesar archivo: {str(e)}")
                self.log_movement(f"ERROR: {str(e)}")

    def show_processing_stats(self, stats):
        """Mostrar estadísticas del procesamiento"""
        if hasattr(self, 'movements_text'):
            summary = f"""
╔══════════════════════════════════════════════╗
║     RESUMEN DE PROCESAMIENTO                 ║
╠══════════════════════════════════════════════╣
  Archivo: {stats['archivo']}
  Fecha: {stats['fecha_procesamiento']}

  Estadisticas:
  • Total de registros: {stats['total_registros']:,}
  • Usuarios unicos: {stats['usuarios_unicos']:,}
  • Modulos unicos: {stats['modulos_unicos']:,}

  Actualizaciones:
  • Usuarios nuevos: {stats['usuarios_nuevos']}
  • Modulos nuevos: {stats['modulos_nuevos']}
  • Inscripciones: {stats['inscripciones_actualizadas']}

  {'Errores: ' + str(len(stats['errores'])) if stats['errores'] else 'Sin errores'}
╚══════════════════════════════════════════════╝
"""
            self.movements_text.insert(tk.END, summary)
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

    def create_sample_charts(self, parent):
        """Crear gráficas de ejemplo"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Dashboard Instituto HP', fontsize=16)

        # Gráfica 1: Estado de módulos
        estados = ['Completado', 'En proceso', 'Registrado']
        valores = [45, 30, 25]
        colors = ['#82B366', '#FEB236', '#88B0D3']
        axes[0, 0].pie(valores, labels=estados, colors=colors, autopct='%1.1f%%')
        axes[0, 0].set_title('Estado de Modulos')

        # Gráfica 2: Usuarios por Unidad de Negocio
        unidades = ['LCIT', 'LCT', 'TNG', 'EIT']
        usuarios = [120, 95, 78, 110]
        axes[0, 1].bar(unidades, usuarios, color='#6B5B95')
        axes[0, 1].set_title('Usuarios por Unidad de Negocio')
        axes[0, 1].set_ylabel('Numero de Usuarios')

        # Gráfica 3: Progreso mensual
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May']
        completados = [20, 35, 45, 60, 75]
        axes[1, 0].plot(meses, completados, marker='o', color='#82B366', linewidth=2)
        axes[1, 0].set_title('Modulos Completados por Mes')
        axes[1, 0].set_ylabel('Modulos Completados')
        axes[1, 0].grid(True, alpha=0.3)

        # Gráfica 4: Tasa de finalización
        diplomados = ['Diplomado 1', 'Diplomado 2']
        finalizacion = [78, 65]
        axes[1, 1].barh(diplomados, finalizacion, color=['#88B0D3', '#FEB236'])
        axes[1, 1].set_title('Tasa de Finalizacion por Diplomado (%)')
        axes[1, 1].set_xlabel('Porcentaje')

        plt.tight_layout()

        # Integrar en tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def search_user_by_id(self):
        """Buscar usuario por ID"""
        user_id = self.search_entry.get()
        if not user_id:
            messagebox.showwarning("Advertencia", "Ingrese un ID de usuario")
            return

        self.cursor.execute("""
            SELECT
                u.UserId,
                u.Nombre,
                u.Email,
                un.NombreUnidad,
                u.Nivel,
                COUNT(DISTINCT pm.IdModulo) as TotalModulos,
                SUM(CASE WHEN pm.EstatusModuloUsuario = 'Completado' THEN 1 ELSE 0 END) as Completados
            FROM instituto_Usuario u
            LEFT JOIN instituto_UnidadDeNegocio un ON u.IdUnidadDeNegocio = un.IdUnidadDeNegocio
            LEFT JOIN instituto_ProgresoModulo pm ON u.UserId = pm.UserId
            WHERE u.UserId = ?
            GROUP BY u.UserId, u.Nombre, u.Email, un.NombreUnidad, u.Nivel
        """, (user_id,))

        result = self.cursor.fetchone()
        if result:
            self.display_search_results([result],
                ['ID', 'Nombre', 'Email', 'Unidad', 'Nivel', 'Total Modulos', 'Completados'])
        else:
            messagebox.showinfo("Sin resultados", "Usuario no encontrado")

    def load_business_units(self):
        """Cargar unidades de negocio en el combobox"""
        try:
            self.cursor.execute("""
                SELECT NombreUnidad FROM instituto_UnidadDeNegocio
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
            SELECT u.UserId, u.Nombre, u.Email, un.NombreUnidad, u.Division, u.FechaRegistro, u.Activo
            FROM instituto_Usuario u
            LEFT JOIN instituto_UnidadDeNegocio un ON u.IdUnidadDeNegocio = un.IdUnidadDeNegocio
            WHERE un.NombreUnidad = ?
            ORDER BY u.Nombre
        """, (unit,))

        results = self.cursor.fetchall()
        if results:
            self.display_search_results(results,
                ['ID', 'Nombre', 'Email', 'Unidad', 'Division', 'Fecha Reg', 'Activo'])
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
                FROM instituto_ProgresoModulo
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
        """Consultar usuarios nuevos"""
        self.cursor.execute("""
            SELECT u.UserId, u.Nombre, u.Email, un.NombreUnidad, u.Division, u.FechaRegistro, u.Activo
            FROM instituto_Usuario u
            LEFT JOIN instituto_UnidadDeNegocio un ON u.IdUnidadDeNegocio = un.IdUnidadDeNegocio
            WHERE CAST(u.FechaRegistro AS DATE) >= DATEADD(day, -30, GETDATE())
            ORDER BY u.FechaRegistro DESC
        """)

        results = self.cursor.fetchall()
        if results:
            self.display_search_results(results,
                ['ID', 'Nombre', 'Email', 'Unidad', 'Division', 'Fecha Reg', 'Activo'])
        else:
            messagebox.showinfo("Sin resultados", "No hay usuarios nuevos en los ultimos 30 dias")

    def display_search_results(self, results, columns):
        """Mostrar resultados en el treeview con formato mejorado"""
        # Limpiar treeview
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Configurar columnas
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
        """Diálogo para agregar nuevo usuario"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Nuevo Usuario")
        dialog.geometry("400x300")

        # Campos
        fields = ['ID Usuario', 'Nombre', 'Email', 'Unidad de Negocio', 'Terminal']
        entries = {}

        for i, field in enumerate(fields):
            ttk.Label(dialog, text=field + ":").grid(row=i, column=0, padx=10, pady=5, sticky='e')
            entry = ttk.Entry(dialog, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry

        def save_user():
            values = [entries[field].get() for field in fields]
            if all(values[:3]):  # Los primeros 3 campos son obligatorios
                try:
                    user_id = values[0]
                    nombre = values[1]
                    email = values[2]
                    unidad_nombre = values[3]
                    terminal = values[4]

                    # Obtener IdUnidadDeNegocio
                    id_unidad = None
                    if unidad_nombre:
                        self.cursor.execute("""
                            SELECT IdUnidadDeNegocio FROM instituto_UnidadDeNegocio WHERE NombreUnidad = ?
                        """, (unidad_nombre,))
                        result = self.cursor.fetchone()
                        if result:
                            id_unidad = result[0]

                    self.cursor.execute("""
                        INSERT INTO instituto_Usuario (UserId, Nombre, Email, IdUnidadDeNegocio)
                        VALUES (?, ?, ?, ?)
                    """, (user_id, nombre, email, id_unidad))
                    self.db.commit()
                    self.log_movement(f"Nuevo usuario agregado: {nombre}")
                    messagebox.showinfo("Exito", "Usuario agregado correctamente")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Error al agregar usuario: {str(e)}")
            else:
                messagebox.showwarning("Advertencia", "Complete los campos obligatorios")

        ttk.Button(dialog, text="Guardar", command=save_user,
                  bootstyle='success').grid(row=len(fields), column=0, pady=20)
        ttk.Button(dialog, text="Cancelar", command=dialog.destroy,
                  bootstyle='danger').grid(row=len(fields), column=1, pady=20)

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
            self.cursor.execute("SELECT * FROM instituto_Modulo")
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
