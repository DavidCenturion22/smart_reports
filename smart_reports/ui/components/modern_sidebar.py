"""
Componente ModernSidebar - Barra lateral moderna con navegación
"""
import customtkinter as ctk


class ModernSidebar(ctk.CTkFrame):
    """Sidebar moderna con logo, navegación y footer"""

    def __init__(self, parent, navigation_callbacks, **kwargs):
        """
        Args:
            parent: Widget padre
            navigation_callbacks: Dict con {nombre: callback_function}
        """
        super().__init__(
            parent,
            width=220,
            fg_color='#2b2d42',
            corner_radius=0,
            **kwargs
        )

        self.navigation_callbacks = navigation_callbacks
        self.nav_buttons = []
        self.active_button = None

        # Logo/Header
        self._create_header()

        # Navegación
        self._create_navigation()

        # Footer con versión
        self._create_footer()

    def _create_header(self):
        """Crear header con logo y título"""
        logo_frame = ctk.CTkFrame(self, fg_color='transparent', height=100)
        logo_frame.pack(fill='x', padx=20, pady=(20, 10))
        logo_frame.pack_propagate(False)

        # Título principal
        logo_label = ctk.CTkLabel(
            logo_frame,
            text='SMART\nREPORTS',
            font=('Segoe UI', 22, 'bold'),
            text_color='#ffffff',
            justify='left'
        )
        logo_label.pack(anchor='w', pady=(10, 0))

        # Subtítulo
        subtitle = ctk.CTkLabel(
            logo_frame,
            text='INSTITUTO HP',
            font=('Segoe UI', 11),
            text_color='#a0a0b0'
        )
        subtitle.pack(anchor='w', pady=(5, 0))

        # Línea separadora
        separator = ctk.CTkFrame(self, height=1, fg_color='#3a3d5c')
        separator.pack(fill='x', padx=20, pady=(10, 20))

    def _create_navigation(self):
        """Crear botones de navegación"""
        nav_items = [
            ('📊', 'Dashboard', 'dashboard'),
            ('🔍', 'Consultas', 'consultas'),
            ('📤', 'Actualizar Datos', 'actualizar'),
            ('⚙️', 'Configuración', 'configuracion'),
        ]

        for icon, text, key in nav_items:
            if key in self.navigation_callbacks:
                btn = ctk.CTkButton(
                    self,
                    text=f'{icon}  {text}',
                    font=('Segoe UI', 14),
                    fg_color='transparent',
                    text_color='#a0a0b0',
                    hover_color='#3a3d5c',
                    anchor='w',
                    height=50,
                    corner_radius=10,
                    command=lambda k=key: self._on_nav_click(k)
                )
                btn.pack(fill='x', padx=10, pady=5)
                self.nav_buttons.append((key, btn))

    def _create_footer(self):
        """Crear footer con información de versión"""
        # Spacer para empujar footer al fondo
        spacer = ctk.CTkFrame(self, fg_color='transparent')
        spacer.pack(fill='both', expand=True)

        # Footer
        footer = ctk.CTkFrame(self, fg_color='transparent', height=60)
        footer.pack(side='bottom', fill='x', padx=20, pady=20)
        footer.pack_propagate(False)

        # Línea separadora superior
        separator = ctk.CTkFrame(footer, height=1, fg_color='#3a3d5c')
        separator.pack(fill='x', pady=(0, 10))

        # Versión
        version = ctk.CTkLabel(
            footer,
            text='v2.0.0',
            font=('Segoe UI', 10),
            text_color='#6c6c80'
        )
        version.pack()

        # Copyright
        copyright_text = ctk.CTkLabel(
            footer,
            text='© 2025 Instituto HP',
            font=('Segoe UI', 9),
            text_color='#6c6c80'
        )
        copyright_text.pack()

    def _on_nav_click(self, key):
        """Manejar click en navegación"""
        # Actualizar estilos de botones
        for btn_key, btn in self.nav_buttons:
            if btn_key == key:
                btn.configure(
                    fg_color='#3a3d5c',
                    text_color='#ffffff'
                )
                self.active_button = btn
            else:
                btn.configure(
                    fg_color='transparent',
                    text_color='#a0a0b0'
                )

        # Ejecutar callback
        if key in self.navigation_callbacks:
            self.navigation_callbacks[key]()

    def set_active(self, key):
        """Establecer botón activo programáticamente"""
        self._on_nav_click(key)
