@echo off
echo ========================================
echo   INSTALACION DE DEPENDENCIAS
echo   SMART REPORTS - INSTITUTO HP
echo ========================================
echo.
echo Este proceso instalara todas las dependencias
echo necesarias para el proyecto en Python global.
echo.
echo Las dependencias son:
echo   - pyodbc (Conexion SQL Server)
echo   - pandas (Procesamiento de datos)
echo   - numpy (Calculos numericos)
echo   - ttkbootstrap (Interfaz grafica moderna)
echo   - matplotlib (Graficas)
echo   - pillow (Manejo de imagenes)
echo   - openpyxl (Archivos Excel)
echo   - pyinstaller (Generacion de .exe)
echo.
pause
echo.
echo [INFO] Instalando dependencias desde requirements.txt...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERROR] Hubo un problema al instalar
    echo ========================================
    echo.
    echo Verifica que:
    echo   1. Tengas Python instalado
    echo   2. pip este configurado correctamente
    echo   3. Tengas conexion a internet
    echo.
) else (
    echo.
    echo ========================================
    echo [OK] Dependencias instaladas!
    echo ========================================
    echo.
    echo Ya puedes:
    echo   - Compilar el .exe con: compilar.bat
    echo   - Ejecutar el codigo con: python src\main.py
    echo.
)

pause
