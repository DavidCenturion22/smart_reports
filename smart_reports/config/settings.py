"""
Configuración global del sistema Smart Reports
"""

# Configuración de Base de Datos
DATABASE_CONFIG = {
    'server': '10.133.18.111',
    'database': 'TNGCORE',
    'username': 'tngdatauser',
    'password': 'Password1',
    'driver': 'ODBC Driver 17 for SQL Server'
}

# Colores corporativos
COLORS = {
    'primary': '#6B5B95',      # Morado principal
    'secondary': '#88B0D3',    # Azul secundario
    'success': '#82B366',      # Verde
    'warning': '#FEB236',      # Naranja
    'danger': '#FF6361',       # Rojo
    'dark': '#4A4A4A',         # Gris oscuro
    'light': '#F7F7F7',        # Gris claro
    'edited': '#FFF59D'        # Amarillo para celdas editadas
}

# Configuración de la aplicación
APP_CONFIG = {
    'title': 'SMART REPORTS - INSTITUTO HP',
    'version': '2.0',
    'geometry': '1400x800',
    'theme': 'darkly',
    'company': 'Instituto Hutchison Ports'
}

# Rutas de archivos
PATHS = {
    'logo': 'assets/logo.png',
    'reports': 'reports/',
    'logs': 'logs/',
    'backups': 'backups/'
}

# Estados de módulos
MODULE_STATUSES = ['Completado', 'En proceso', 'Registrado', 'No iniciado']

# Configuración de PDFs
PDF_CONFIG = {
    'page_size': 'letter',
    'title_font_size': 24,
    'subtitle_font_size': 16,
    'normal_font_size': 10,
    'logo_width': 2,  # inches
    'logo_height': 0.8  # inches
}
