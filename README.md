# SMART REPORTS v2.0
## Instituto Hutchison Ports - Sistema de Gestion Academica

**Version:** 2.0 - Arquitectura Profesional
**Estado:** Listo para Produccion
**Fecha:** Octubre 2025

---

## RESUMEN EJECUTIVO

Proyecto completado al 100% con arquitectura profesional refactorizada
- Arquitectura modular MVC
- Codigo organizado por capas
- Todos los archivos migrados a smart_reports/
- Directorio src/ eliminado
- Documentacion obsoleta eliminada
- Sistema completamente funcional

---

## INICIO RAPIDO

### Ejecutar la aplicacion:
```bash
# Opcion 1: Archivo BAT (Recomendado)
EJECUTAR_AQUI.bat

# Opcion 2: Python directamente
python main.py
```

### Primera vez:
```bash
# 1. Instalar dependencias
instalar_dependencias.bat

# 2. Inicializar base de datos
python init_database.py

# 3. Ejecutar
python main.py
```

---

## ESTRUCTURA DEL PROYECTO

### Arquitectura Modular Profesional
```
instituto_hp_smart_reports/
│
├── main.py                          # Punto de entrada principal
├── EJECUTAR_AQUI.bat                # Ejecutar aplicacion (Windows)
├── compilar.bat                     # Compilar ejecutable
├── build_exe.spec                   # Configuracion PyInstaller
├── requirements.txt                 # Dependencias Python
│
├── smart_reports/                   # Paquete principal
│   ├── __init__.py
│   ├── main.py                      # Inicializador de la app
│   │
│   ├── config/                      # Configuracion
│   │   ├── __init__.py
│   │   └── settings.py              # Configuracion global
│   │
│   ├── database/                    # Capa de base de datos
│   │   ├── __init__.py
│   │   ├── connection.py            # Gestion de conexiones
│   │   └── queries.py               # Consultas SQL
│   │
│   ├── ui/                          # Interfaz de usuario
│   │   ├── __init__.py
│   │   ├── main_window.py           # Ventana principal
│   │   └── components.py            # Componentes reutilizables
│   │
│   └── services/                    # Logica de negocio
│       ├── __init__.py
│       ├── data_processor.py        # Procesamiento de archivos
│       └── pdf_generator.py         # Generacion de PDFs
│
├── init_database.py                 # Script de inicializacion BD
├── test_connection.py               # Prueba de conexion
└── test_db.py                       # Pruebas de base de datos
```

---

## FUNCIONALIDADES

### Panel de Estatus
- Cargar archivos Transcript Status (Excel/CSV)
- Procesamiento automatico de datos
- Visualizacion de estadisticas de procesamiento
- Actualizacion de correos y usuarios

### Dashboards
- Visualizacion de metricas clave
- Graficas interactivas con matplotlib
- Estado de modulos (grafica de pastel)
- Usuarios por unidad de negocio (barras)
- Progreso mensual (linea de tiempo)
- Tasa de finalizacion por diplomado

### Consultas
- Busqueda de usuario por ID
- Consulta de unidades de negocio
- Estado de modulos
- Usuarios nuevos (ultimos 30 dias)
- Resultados en tabla interactiva

### Configuracion
- Agregar nuevos usuarios
- Gestionar modulos
- Gestionar unidades de negocio
- Opciones de respaldo de base de datos

### Caracteristicas Tecnicas
- Tabla editable con rastreo de cambios
- Generacion de PDFs profesionales
- Auditoria automatica de cambios
- Procesamiento inteligente de archivos Transcript Status
- Gestion de conexiones con patron Singleton

---

## CONFIGURACION

### Base de Datos
Editar `smart_reports/config/settings.py`:
```python
DATABASE_CONFIG = {
    'server': '10.133.18.111',
    'database': 'TNGCORE',
    'username': 'tngdatauser',
    'password': 'Password1',
    'driver': 'ODBC Driver 17 for SQL Server'
}
```

### Dependencias
```bash
pip install -r requirements.txt
```

Dependencias principales:
- ttkbootstrap - Interfaz grafica moderna
- pyodbc - Conexion SQL Server
- pandas - Procesamiento de datos
- matplotlib - Visualizaciones
- reportlab - PDFs profesionales

---

## COMPILACION

Para generar ejecutable standalone:
```bash
compilar.bat
```

El ejecutable se genera en: `dist/SmartReports_InstitutoHP.exe`

---

## ARQUITECTURA

### Patron de Diseno
- MVC (Model-View-Controller) adaptado
- Singleton para conexion a base de datos
- Factory para procesadores de datos
- Separacion por capas

### Capas del Sistema

**Config Layer** - Configuracion centralizada
- Settings globales
- Constantes del sistema

**Database Layer** - Acceso a datos
- Conexion con patron Singleton
- Queries parametrizadas
- Gestion de transacciones

**UI Layer** - Interfaz de usuario
- Ventana principal con navegacion
- Componentes reutilizables
- Treeview editable personalizado

**Services Layer** - Logica de negocio
- TranscriptProcessor - Procesamiento de archivos
- PDFReportGenerator - Reportes profesionales
- DataProcessor - Transformacion de datos

---

## TROUBLESHOOTING

### Error de Conexion a BD
```
Verificar:
- SQL Server corriendo en 10.133.18.111
- ODBC Driver 17 instalado
- Credenciales correctas en settings.py
- Firewall permite conexion al puerto SQL
```

### Error de Importacion
```
Solucion:
- Verificar Python 3.8+
- Instalar dependencias: pip install -r requirements.txt
- Verificar PYTHONPATH
```

### Aplicacion no Inicia
```
1. Verificar dependencias instaladas
2. Ejecutar test_connection.py
3. Revisar logs de error
4. Ejecutar desde consola: python main.py
```

---

## CAMBIOS EN VERSION 2.0

- Arquitectura completamente refactorizada
- Estructura modular profesional
- Imports absolutos (smart_reports.module)
- Codigo organizado por capas
- Eliminacion de codigo duplicado
- Mejor separacion de responsabilidades
- Componentes reutilizables
- Patron Singleton para DB
- Directorio src/ eliminado
- Migracion completa a smart_reports/

---

## ESTADO DEL PROYECTO

| Componente | Estado |
|------------|--------|
| Arquitectura Modular | 100% Completo |
| UI Completa | 100% Completo |
| Base de Datos | 100% Completo |
| Procesamiento Datos | 100% Completo |
| PDFs Profesionales | 100% Completo |
| Documentacion | 100% Completo |

**Estado General: LISTO PARA PRODUCCION**

---

## SOPORTE

Para reportar errores o solicitar funcionalidades:
- Contactar al equipo de desarrollo
- Documentar el error con capturas
- Incluir logs si es posible

---

**Desarrollado para Instituto Hutchison Ports**
**Version 2.0 - Octubre 2025**
**Arquitectura Profesional - Listo para Produccion**

