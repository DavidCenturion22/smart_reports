"""
UI Components package - Componentes reutilizables de la interfaz

Incluye:
- Componentes originales (EditableTreeview, LoadingSpinner)
- Componentes modernos (MetricCard, ChartCard, ModernSidebar)
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from smart_reports.config.settings import COLORS


# ==================== COMPONENTES ORIGINALES ====================

class EditableTreeview(ttk.Treeview):
    """Treeview editable con rastreo de cambios completo"""

    def __init__(self, parent, editable_columns=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.editable_columns = editable_columns if editable_columns is not None else []
        self.edited_cells = {}
        self.original_values = {}
        self.row_data = {}

        self.bind('<Double-Button-1>', self.on_double_click)
        self.tag_configure('edited', background=COLORS['edited'], foreground='#000000')

    def on_double_click(self, event):
        """Editar celda al hacer doble clic"""
        region = self.identify_region(event.x, event.y)
        if region != 'cell':
            return

        column = self.identify_column(event.x)
        item = self.identify_row(event.y)

        if not column or not item:
            return

        column_index = int(column.replace('#', '')) - 1

        if self.editable_columns and column_index not in self.editable_columns:
            return

        values = self.item(item, 'values')
        if column_index < 0 or column_index >= len(values):
            return

        current_value = str(values[column_index])
        cell_key = (item, column_index)

        if cell_key not in self.original_values:
            self.original_values[cell_key] = current_value

        bbox = self.bbox(item, column)
        if not bbox:
            return

        entry = ttk.Entry(self, bootstyle="warning")
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        entry.insert(0, current_value)
        entry.select_range(0, tk.END)
        entry.focus()

        def save_edit(event=None):
            new_value = entry.get()
            if new_value != current_value:
                new_values = list(values)
                new_values[column_index] = new_value
                self.item(item, values=new_values)
                self.edited_cells[cell_key] = new_value

                current_tags = list(self.item(item, 'tags'))
                if 'edited' not in current_tags:
                    current_tags.append('edited')
                    self.item(item, tags=current_tags)
            entry.destroy()

        def cancel_edit(event=None):
            entry.destroy()

        entry.bind('<Return>', save_edit)
        entry.bind('<Escape>', cancel_edit)
        entry.bind('<FocusOut>', save_edit)

    def get_edited_data(self):
        """Retorna datos editados en formato útil para actualizaciones BD"""
        result = {}
        for (item_id, col_index), new_value in self.edited_cells.items():
            if item_id not in result:
                result[item_id] = {}
            result[item_id][col_index] = {
                'new_value': new_value,
                'old_value': self.original_values.get((item_id, col_index))
            }
        return result

    def get_item_values(self, item_id):
        """Obtiene todos los valores de un item"""
        return self.item(item_id, 'values')

    def clear_edits(self):
        """Revierte todos los cambios y restaura valores originales"""
        for (item_id, col_index), original_value in self.original_values.items():
            try:
                values = list(self.item(item_id, 'values'))
                values[col_index] = original_value
                self.item(item_id, values=values)

                current_tags = list(self.item(item_id, 'tags'))
                if 'edited' in current_tags:
                    current_tags.remove('edited')
                    self.item(item_id, tags=current_tags)
            except:
                pass

        self.edited_cells.clear()
        self.original_values.clear()

    def commit_edits(self):
        """Confirma las ediciones (limpia el tracking pero mantiene los valores)"""
        for item_id in set(item for item, _ in self.edited_cells.keys()):
            try:
                current_tags = list(self.item(item_id, 'tags'))
                if 'edited' in current_tags:
                    current_tags.remove('edited')
                    self.item(item_id, tags=current_tags)
            except:
                pass

        self.edited_cells.clear()
        self.original_values.clear()

    def has_unsaved_changes(self):
        """Verifica si hay cambios sin guardar"""
        return len(self.edited_cells) > 0

    def get_change_count(self):
        """Retorna el número de celdas editadas"""
        return len(self.edited_cells)

    def set_editable_columns(self, columns):
        """Define qué columnas son editables (por índice)"""
        self.editable_columns = columns

    def highlight_row(self, item_id, color='#E8F5E9'):
        """Resalta una fila específica"""
        self.item(item_id, tags=('highlight',))
        self.tag_configure('highlight', background=color)

    def clear_highlights(self):
        """Limpia todos los resaltados excepto las ediciones"""
        for item in self.get_children():
            tags = list(self.item(item, 'tags'))
            if 'highlight' in tags:
                tags.remove('highlight')
                self.item(item, tags=tags)


class LoadingSpinner(ttk.Frame):
    """Spinner de carga simple"""

    def __init__(self, parent, text="Cargando...", **kwargs):
        super().__init__(parent, **kwargs)

        self.label = ttk.Label(self, text=text, font=('Arial', 12))
        self.label.pack(pady=20)

        self.progressbar = ttk.Progressbar(self, mode='indeterminate', length=200)
        self.progressbar.pack(pady=10)

    def start(self):
        """Inicia animación"""
        self.progressbar.start(10)

    def stop(self):
        """Detiene animación"""
        self.progressbar.stop()


# ==================== COMPONENTES MODERNOS ====================

from smart_reports.ui.components.metric_card import MetricCard
from smart_reports.ui.components.chart_card import ChartCard
from smart_reports.ui.components.modern_sidebar import ModernSidebar


__all__ = [
    # Componentes originales (para main_window.py)
    'EditableTreeview',
    'LoadingSpinner',
    # Componentes modernos (para main_window_modern.py)
    'MetricCard',
    'ChartCard',
    'ModernSidebar'
]
