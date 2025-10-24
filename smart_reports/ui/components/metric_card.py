"""
Componente MetricCard - Card moderna para mostrar métricas
"""
import customtkinter as ctk


class MetricCard(ctk.CTkFrame):
    """Card moderna para mostrar una métrica con valor, cambio porcentual e icono"""

    def __init__(self, parent, title, value, change_percent=None, icon=None, color='#6c63ff', **kwargs):
        """
        Args:
            parent: Widget padre
            title: Título de la métrica
            value: Valor principal a mostrar
            change_percent: Porcentaje de cambio (opcional)
            icon: Emoji o icono a mostrar (opcional)
            color: Color de acento para el icono y hover
        """
        super().__init__(
            parent,
            fg_color='#2b2d42',
            corner_radius=20,
            border_width=1,
            border_color='#3a3d5c',
            **kwargs
        )

        self.accent_color = color

        # Padding interno
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=0)

        row = 0

        # Icono (opcional)
        if icon:
            icon_label = ctk.CTkLabel(
                self,
                text=icon,
                font=('Segoe UI', 32),
                text_color=color
            )
            icon_label.grid(row=row, column=0, padx=20, pady=(20, 5), sticky='w')
            row += 1

        # Título
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=('Segoe UI', 14),
            text_color='#a0a0b0',
            anchor='w'
        )
        title_label.grid(row=row, column=0, padx=20, pady=(10 if icon else 20, 5), sticky='w')
        row += 1

        # Valor principal
        value_label = ctk.CTkLabel(
            self,
            text=str(value),
            font=('Segoe UI', 48, 'bold'),
            text_color='#ffffff',
            anchor='w'
        )
        value_label.grid(row=row, column=0, padx=20, pady=(0, 10), sticky='w')
        row += 1

        # Indicador de cambio (opcional)
        if change_percent is not None:
            change_color = '#51cf66' if change_percent >= 0 else '#ff6b6b'
            arrow = '↑' if change_percent >= 0 else '↓'

            change_label = ctk.CTkLabel(
                self,
                text=f'{arrow} {abs(change_percent):.1f}%',
                font=('Segoe UI', 16, 'bold'),
                text_color=change_color
            )
            change_label.grid(row=row, column=0, padx=20, pady=(0, 20), sticky='w')
        else:
            # Agregar padding inferior si no hay indicador
            spacer = ctk.CTkLabel(self, text='', height=10)
            spacer.grid(row=row, column=0)

        # Efecto hover
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

    def _on_enter(self, event):
        """Efecto hover - resaltar borde"""
        self.configure(border_color=self.accent_color)

    def _on_leave(self, event):
        """Salir del hover - restaurar borde"""
        self.configure(border_color='#3a3d5c')

    def update_value(self, new_value, new_change_percent=None):
        """Actualizar el valor de la métrica"""
        # Buscar y actualizar el label del valor
        for child in self.winfo_children():
            if isinstance(child, ctk.CTkLabel):
                # Identificar label de valor por su font size
                font_info = child.cget('font')
                if '48' in str(font_info):
                    child.configure(text=str(new_value))
                    break
