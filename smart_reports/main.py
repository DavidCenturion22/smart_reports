"""
SMART REPORTS - Instituto Hutchison Ports
Punto de entrada principal
Versión 2.0
"""

import sys
import os

# Agregar el directorio padre al path para imports absolutos
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ttkbootstrap as ttk
from smart_reports.ui.main_window import MainWindow


def main():
    """Función principal de la aplicación"""
    root = ttk.Window(themename="darkly")
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
