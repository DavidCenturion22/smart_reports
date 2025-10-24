# SMART REPORTS - REDISEÑO VISUAL v2.0

## 🎨 Resumen del Rediseño

Se ha realizado un **rediseño visual completo** de la aplicación Smart Reports, modernizando la interfaz de usuario mientras se mantiene **toda la lógica backend intacta**.

## 🚀 Cómo Ejecutar

### Versión Moderna (Nueva):
```bash
cd smart_reports
python main_modern.py
```

### Versión Original (Anterior):
```bash
cd smart_reports
python main.py
```

## 📦 Nuevas Dependencias

La versión moderna requiere **CustomTkinter**:

```bash
pip install customtkinter
```

Las demás dependencias permanecen igual.

## 🏗️ Arquitectura del Rediseño

### Nuevos Componentes Creados

```
smart_reports/
├── ui/
│   ├── components/
│   │   ├── metric_card.py          # Card para métricas con iconos
│   │   ├── chart_card.py           # Card para gráficos matplotlib
│   │   └── modern_sidebar.py       # Sidebar moderna con navegación
│   ├── panels/
│   │   └── modern_dashboard.py     # Dashboard rediseñado
│   ├── main_window_modern.py       # Ventana principal moderna
│   └── main_window_backup.py       # Backup del original
└── main_modern.py                   # Entry point versión moderna
```

### Archivos Preservados

- `main_window.py` - **ORIGINAL INTACTO** (funciona con ttkbootstrap)
- Toda la lógica en `database/`, `services/`, `config/` - **SIN CAMBIOS**

## 🎨 Diseño Visual

### Paleta de Colores

```python
PRIMARY_COLORS = {
    'background': '#1a1d2e',      # Fondo principal oscuro
    'surface': '#2b2d42',         # Cards y superficies
    'surface_light': '#3a3d5c',   # Hover states

    'accent_yellow': '#ffd93d',   # Amarillo vibrante
    'accent_blue': '#6c63ff',     # Azul/púrpura
    'accent_cyan': '#4ecdc4',     # Cyan/turquesa
    'accent_orange': '#ff6b6b',   # Naranja/rojo
    'accent_green': '#51cf66',    # Verde éxito

    'text_primary': '#ffffff',    # Texto principal
    'text_secondary': '#a0a0b0',  # Texto secundario
    'text_muted': '#6c6c80',      # Texto deshabilitado
}
```

### Características Visuales

- ✅ **Bordes redondeados** (corner_radius=15-20px)
- ✅ **Sombras sutiles** para profundidad
- ✅ **Efectos hover** en cards y botones
- ✅ **Tipografía moderna** (Segoe UI)
- ✅ **Iconos emoji** para mejor UX
- ✅ **Gráficos estilizados** con matplotlib

## 📊 Secciones Rediseñadas

### 1. Dashboard (Panel de Control)

**Componentes:**
- 3 métricas principales (Total Usuarios, Módulos Activos, Tasa Completado)
- Gráficos de distribución por unidad de negocio (barras + donut)
- Progreso por módulo (barras apiladas)
- Top performers y distribución de estados

**Visualizaciones:**
- Gráficos de barras horizontales
- Gráficos donut/pie
- Gráficos de barras apiladas
- Todos con colores vibrantes y estilo oscuro

### 2. Actualizar Datos

**Mejoras:**
- Cards separadas por pasos (1. Seleccionar, 2. Actualizar, 3. Movimientos)
- Botones grandes con iconos
- Panel de movimientos con textbox estilizado
- Colores distintivos por acción

### 3. Consultas

**Mejoras:**
- Búsqueda por ID con entrada moderna
- Selector de unidad de negocio estilizado
- Botones de consultas rápidas
- Tabla de resultados con tema oscuro
- Filas alternadas para mejor legibilidad

### 4. Configuración

**Mejoras:**
- Grid de cards grandes (2x2)
- Iconos grandes y coloridos
- Hover effects con cambio de borde
- Descripción clara de cada opción

## 🔧 Componentes Reutilizables

### MetricCard

```python
from smart_reports.ui.components.metric_card import MetricCard

card = MetricCard(
    parent,
    title='Total de Usuarios',
    value='1,247',
    change_percent=12.3,  # Opcional
    icon='👥',           # Opcional
    color='#6c63ff'
)
```

### ChartCard

```python
from smart_reports.ui.components.chart_card import ChartCard

chart = ChartCard(
    parent,
    title='Usuarios por Unidad',
    chart_type='horizontal_bar'  # bar, donut, line, area, stacked_bar
)
chart.create_chart(data=[100, 200, 150], labels=['A', 'B', 'C'])
```

### ModernSidebar

```python
from smart_reports.ui.components.modern_sidebar import ModernSidebar

callbacks = {
    'dashboard': self.show_dashboard,
    'consultas': self.show_consultas,
    'actualizar': self.show_actualizar,
    'configuracion': self.show_configuracion,
}

sidebar = ModernSidebar(parent, callbacks)
sidebar.set_active('dashboard')  # Establecer activo programáticamente
```

## ✅ Funcionalidad Preservada

**TODA la lógica backend permanece intacta:**

- ✅ Conexión a SQL Server
- ✅ Procesamiento de archivos Excel (TranscriptProcessor)
- ✅ Queries SQL (sin cambios)
- ✅ Actualización de base de datos
- ✅ Consultas de usuarios
- ✅ Generación de reportes
- ✅ Validaciones y mapeo de columnas

**NO se modificó:**
- `database/queries.py`
- `database/connection.py`
- `services/data_processor.py`
- `services/pdf_generator.py`
- `config/settings.py`

## 🎯 Ventajas del Rediseño

### Visuales
- Interfaz moderna y profesional
- Mejor contraste y legibilidad
- Colores vibrantes que destacan información importante
- Animaciones sutiles (hover effects)

### UX (Experiencia de Usuario)
- Navegación más clara con sidebar
- Agrupación lógica de funciones en cards
- Feedback visual inmediato
- Iconos que facilitan identificación rápida

### Técnicas
- Componentes reutilizables y modulares
- Separación clara de UI y lógica de negocio
- Fácil de extender con nuevas visualizaciones
- Compatible con versión anterior

## 🔄 Migración

### Para usar la versión moderna:

1. **Instalar CustomTkinter:**
   ```bash
   pip install customtkinter
   ```

2. **Ejecutar versión moderna:**
   ```bash
   python main_modern.py
   ```

### Para volver a la versión original:

```bash
python main.py
```

Ambas versiones **comparten la misma base de datos y lógica**, por lo que son intercambiables sin pérdida de datos.

## 📝 Notas Técnicas

### CustomTkinter vs TTKBootstrap

| Aspecto | TTKBootstrap (Original) | CustomTkinter (Moderna) |
|---------|------------------------|-------------------------|
| Base | Tkinter nativo | Tkinter + rendering custom |
| Temas | Bootstrap-inspired | Modern/macOS-inspired |
| Widgets | ttk.* | ctk.* |
| Bordes redondeados | Limitado | Nativo |
| Animaciones | No | Sí (limitadas) |
| Performance | Rápido | Ligeramente más lento |
| Compatibilidad | Máxima | Buena |

### Matplotlib Integration

Los gráficos usan **matplotlib** con estilo oscuro personalizado:
- Fondo transparente integrado con cards
- Grid sutil para mejor legibilidad
- Colores coordinados con paleta de la app
- Texto blanco optimizado para fondo oscuro

## 🐛 Problemas Conocidos

1. **Primera carga lenta**: CustomTkinter puede tardar 1-2 segundos en cargar la primera vez
2. **Gráficos matplotlib**: No se actualizan con animaciones, solo al refrescar
3. **Treeview en consultas**: Usa tkinter.ttk nativo (no ctk) por compatibilidad

## 🔮 Futuras Mejoras

- [ ] Animaciones de transición entre paneles
- [ ] Gráficos interactivos (plotly o similar)
- [ ] Modo claro/oscuro toggle
- [ ] Exportar dashboard a PDF
- [ ] Filtros avanzados en consultas
- [ ] Drag & drop para archivos Excel

## 👥 Créditos

- **Diseño**: Basado en principios de Material Design y macOS Big Sur
- **Iconos**: Emojis Unicode nativos
- **Framework UI**: CustomTkinter 5.2+
- **Gráficos**: Matplotlib 3.5+

## 📄 Licencia

© 2025 Instituto Hutchison Ports - Todos los derechos reservados
