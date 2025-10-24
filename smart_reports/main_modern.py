"""
SMART REPORTS - Instituto Hutchison Ports
Punto de entrada principal - VERSIÓN MODERNA
Versión 2.0
"""

import sys
import os

# Agregar el directorio padre al path para imports absolutos
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import customtkinter as ctk
from smart_reports.ui.main_window_modern import MainWindow


def main():
    """Función principal de la aplicación - Versión Moderna"""
    # Configurar CustomTkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    # Crear ventana principal
    root = ctk.CTk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
