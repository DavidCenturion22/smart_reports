"""
Módulo de generación de PDFs para Smart Reports
Genera reportes profesionales de dashboards y consultas
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import os


class PDFReportGenerator:
    """Generador de reportes PDF profesionales"""

    def __init__(self, logo_path=None):
        self.logo_path = logo_path
        self.styles = getSampleStyleSheet()

        # Estilos personalizados
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#6B5B95'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#4A4A4A'),
            spaceAfter=12,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        )

        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT
        )

    def create_dashboard_pdf(self, filename, dashboard_title, figure, data_table=None, additional_info=None):
        """
        Crea un PDF de un dashboard con gráfico y datos

        Args:
            filename: Ruta del archivo PDF a crear
            dashboard_title: Título del dashboard
            figure: Figura de matplotlib
            data_table: Lista de listas con datos para tabla
            additional_info: Diccionario con información adicional
        """
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []

        # Encabezado con logo
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo = RLImage(self.logo_path, width=2*inch, height=0.8*inch)
                story.append(logo)
                story.append(Spacer(1, 0.3*inch))
            except:
                pass

        # Título
        title = Paragraph(f"<b>SMART REPORTS - Instituto HP</b>", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.2*inch))

        # Subtítulo con nombre del dashboard
        subtitle = Paragraph(dashboard_title, self.subtitle_style)
        story.append(subtitle)
        story.append(Spacer(1, 0.1*inch))

        # Fecha de generación
        date_text = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        date_para = Paragraph(date_text, self.normal_style)
        story.append(date_para)
        story.append(Spacer(1, 0.3*inch))

        # Gráfico (convertir figura matplotlib a imagen)
        if figure:
            img_buffer = BytesIO()
            figure.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)

            # Insertar imagen en PDF
            img = RLImage(img_buffer, width=6.5*inch, height=4*inch)
            story.append(img)
            story.append(Spacer(1, 0.3*inch))

        # Información adicional
        if additional_info:
            info_title = Paragraph("<b>Resumen de Datos</b>", self.subtitle_style)
            story.append(info_title)
            story.append(Spacer(1, 0.1*inch))

            for key, value in additional_info.items():
                info_text = f"<b>{key}:</b> {value}"
                info_para = Paragraph(info_text, self.normal_style)
                story.append(info_para)
                story.append(Spacer(1, 0.05*inch))

            story.append(Spacer(1, 0.2*inch))

        # Tabla de datos
        if data_table and len(data_table) > 0:
            table_title = Paragraph("<b>Datos Detallados</b>", self.subtitle_style)
            story.append(table_title)
            story.append(Spacer(1, 0.1*inch))

            # Crear tabla
            t = Table(data_table)

            # Estilo de tabla
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6B5B95')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ])

            t.setStyle(table_style)
            story.append(t)

        # Pie de página
        story.append(Spacer(1, 0.5*inch))
        footer_text = "Instituto Hutchison Ports - Sistema de Gestión Académica"
        footer = Paragraph(f"<i>{footer_text}</i>", self.normal_style)
        story.append(footer)

        # Generar PDF
        doc.build(story)
        return filename

    def create_query_results_pdf(self, filename, query_title, columns, data, filters=None):
        """
        Crea un PDF con resultados de una consulta

        Args:
            filename: Ruta del archivo PDF
            query_title: Título de la consulta
            columns: Lista de nombres de columnas
            data: Lista de filas de datos
            filters: Diccionario con filtros aplicados
        """
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []

        # Encabezado
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo = RLImage(self.logo_path, width=2*inch, height=0.8*inch)
                story.append(logo)
                story.append(Spacer(1, 0.2*inch))
            except:
                pass

        # Título
        title = Paragraph(f"<b>Reporte de Consulta</b>", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.2*inch))

        # Subtítulo
        subtitle = Paragraph(query_title, self.subtitle_style)
        story.append(subtitle)
        story.append(Spacer(1, 0.1*inch))

        # Fecha y hora
        date_text = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        date_para = Paragraph(date_text, self.normal_style)
        story.append(date_para)
        story.append(Spacer(1, 0.1*inch))

        # Filtros aplicados
        if filters:
            filters_title = Paragraph("<b>Filtros Aplicados:</b>", self.subtitle_style)
            story.append(filters_title)
            for key, value in filters.items():
                filter_text = f"• {key}: {value}"
                filter_para = Paragraph(filter_text, self.normal_style)
                story.append(filter_para)
            story.append(Spacer(1, 0.2*inch))

        # Resumen
        summary_text = f"<b>Total de registros:</b> {len(data)}"
        summary = Paragraph(summary_text, self.normal_style)
        story.append(summary)
        story.append(Spacer(1, 0.3*inch))

        # Tabla de resultados
        if data:
            # Preparar datos para tabla (incluir encabezados)
            table_data = [columns] + data

            # Crear tabla
            t = Table(table_data, repeatRows=1)

            # Estilo
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#88B0D3')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ])

            t.setStyle(table_style)
            story.append(t)
        else:
            no_data = Paragraph("<i>No se encontraron resultados</i>", self.normal_style)
            story.append(no_data)

        # Pie de página
        story.append(Spacer(1, 0.5*inch))
        footer_text = "Instituto Hutchison Ports - Confidencial"
        footer = Paragraph(f"<i>{footer_text}</i>", self.normal_style)
        story.append(footer)

        # Generar PDF
        doc.build(story)
        return filename


# Funciones auxiliares para usar en main.py

def export_figure_to_pdf(figure, filename, title="Dashboard"):
    """
    Función rápida para exportar una figura matplotlib a PDF

    Args:
        figure: Figura de matplotlib
        filename: Nombre del archivo PDF
        title: Título del dashboard
    """
    generator = PDFReportGenerator()
    return generator.create_dashboard_pdf(filename, title, figure)


def export_query_to_pdf(filename, title, columns, data, filters=None):
    """
    Función rápida para exportar resultados de consulta a PDF

    Args:
        filename: Nombre del archivo PDF
        title: Título de la consulta
        columns: Lista de columnas
        data: Datos de la consulta
        filters: Filtros aplicados (opcional)
    """
    generator = PDFReportGenerator()
    return generator.create_query_results_pdf(filename, title, columns, data, filters)
