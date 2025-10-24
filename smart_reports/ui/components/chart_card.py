"""
Componente ChartCard - Card con gráficos matplotlib estilizados
"""
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


class ChartCard(ctk.CTkFrame):
    """Card para mostrar gráficos con matplotlib con diseño moderno"""

    def __init__(self, parent, title, chart_type='bar', width=400, height=300, **kwargs):
        """
        Args:
            parent: Widget padre
            title: Título del gráfico
            chart_type: Tipo de gráfico ('bar', 'horizontal_bar', 'donut', 'line', 'area', 'stacked_bar')
            width: Ancho del card
            height: Altura del card
        """
        super().__init__(
            parent,
            fg_color='#2b2d42',
            corner_radius=20,
            border_width=1,
            border_color='#3a3d5c',
            width=width,
            height=height,
            **kwargs
        )

        self.chart_type = chart_type
        self.canvas_widget = None

        # Header
        header = ctk.CTkFrame(self, fg_color='transparent')
        header.pack(fill='x', padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=('Segoe UI', 18, 'bold'),
            text_color='#ffffff',
            anchor='w'
        )
        title_label.pack(side='left')

        # Container para el gráfico
        self.chart_container = ctk.CTkFrame(self, fg_color='transparent')
        self.chart_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))

    def create_chart(self, data, labels=None, data2=None, data3=None):
        """
        Crea el gráfico con estilo moderno

        Args:
            data: Datos principales (lista de números)
            labels: Etiquetas para el eje x o segmentos (lista de strings)
            data2: Datos secundarios para gráficos apilados (opcional)
            data3: Datos terciarios para gráficos apilados (opcional)
        """
        # Limpiar gráfico anterior si existe
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()

        # Configurar estilo matplotlib
        plt.style.use('dark_background')

        # Crear figura
        fig = Figure(figsize=(6, 4), facecolor='#2b2d42')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2b2d42')

        # Configurar grid sutil
        ax.grid(True, alpha=0.1, linestyle='--', linewidth=0.5, color='#a0a0b0')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#3a3d5c')
        ax.spines['bottom'].set_color('#3a3d5c')

        # Colores modernos
        colors = ['#ffd93d', '#6c63ff', '#4ecdc4', '#ff6b6b', '#51cf66', '#ff8c42', '#a78bfa', '#fb923c']

        if self.chart_type == 'bar':
            bars = ax.bar(range(len(data)), data, color=colors[:len(data)], alpha=0.8, width=0.6, edgecolor='#2b2d42', linewidth=2)
            # Agregar valores encima de barras
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', color='white', fontsize=10, fontweight='bold')
            if labels:
                ax.set_xticks(range(len(labels)))
                ax.set_xticklabels(labels, rotation=45, ha='right')

        elif self.chart_type == 'horizontal_bar':
            bars = ax.barh(range(len(data)), data, color=colors[:len(data)], alpha=0.8, height=0.6, edgecolor='#2b2d42', linewidth=2)
            # Agregar valores al final de barras
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f' {int(width)}',
                       ha='left', va='center', color='white', fontsize=10, fontweight='bold')
            if labels:
                ax.set_yticks(range(len(labels)))
                ax.set_yticklabels(labels)

        elif self.chart_type == 'donut':
            wedges, texts, autotexts = ax.pie(
                data,
                labels=labels,
                colors=colors[:len(data)],
                autopct='%1.1f%%',
                startangle=90,
                pctdistance=0.85,
                wedgeprops=dict(width=0.5, edgecolor='#2b2d42', linewidth=3)
            )
            # Estilo de texto
            for text in texts:
                text.set_color('white')
                text.set_fontsize(10)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(11)
                autotext.set_fontweight('bold')

        elif self.chart_type == 'line':
            ax.plot(range(len(data)), data, color='#6c63ff', linewidth=3, marker='o',
                   markersize=8, markerfacecolor='#ffd93d', markeredgewidth=2,
                   markeredgecolor='#6c63ff')
            ax.fill_between(range(len(data)), data, alpha=0.3, color='#6c63ff')
            if labels:
                ax.set_xticks(range(len(labels)))
                ax.set_xticklabels(labels, rotation=45, ha='right')

        elif self.chart_type == 'area':
            ax.fill_between(range(len(data)), data, alpha=0.6, color='#4ecdc4')
            ax.plot(range(len(data)), data, color='#4ecdc4', linewidth=2)
            if labels:
                ax.set_xticks(range(len(labels)))
                ax.set_xticklabels(labels, rotation=45, ha='right')

        elif self.chart_type == 'stacked_bar':
            # Gráfico de barras apiladas (requiere data, data2, data3)
            x = np.arange(len(data))
            width = 0.6

            p1 = ax.bar(x, data, width, label='Completado', color='#51cf66', alpha=0.9, edgecolor='#2b2d42', linewidth=2)

            if data2 is not None:
                p2 = ax.bar(x, data2, width, bottom=data, label='En Progreso', color='#ffd93d', alpha=0.9, edgecolor='#2b2d42', linewidth=2)

                if data3 is not None:
                    bottom = [data[i] + data2[i] for i in range(len(data))]
                    p3 = ax.bar(x, data3, width, bottom=bottom, label='Registrado', color='#6c6c80', alpha=0.9, edgecolor='#2b2d42', linewidth=2)

            if labels:
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=45, ha='right')

            # Leyenda con fondo oscuro
            legend = ax.legend(loc='upper right', framealpha=0.9, facecolor='#3a3d5c', edgecolor='#4a4d6c')
            for text in legend.get_texts():
                text.set_color('white')

        # Configurar labels con color
        ax.tick_params(colors='#a0a0b0', labelsize=9)
        plt.tight_layout()

        # Insertar en tkinter
        self.canvas_widget = FigureCanvasTkAgg(fig, self.chart_container)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill='both', expand=True)

        return self.canvas_widget

    def clear(self):
        """Limpiar el gráfico"""
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
            self.canvas_widget = None
