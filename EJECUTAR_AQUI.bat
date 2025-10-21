@echo off
echo ========================================
echo   SMART REPORTS - INSTITUTO HP
echo   Version 2.0 - Arquitectura Profesional
echo ========================================
echo.
echo Iniciando aplicacion...
echo.

REM Verificar si existe el ejecutable
if exist "dist\SmartReports_InstitutoHP.exe" (
    start "" "dist\SmartReports_InstitutoHP.exe"
) else (
    echo [AVISO] No se encuentra el ejecutable compilado.
    echo Ejecutando version Python directamente...
    echo.
    python main.py
    if %ERRORLEVEL% neq 0 (
        echo.
        echo [ERROR] No se pudo ejecutar la aplicacion.
        echo.
        echo Opciones:
        echo 1. Compilar el ejecutable con: compilar.bat
        echo 2. Verificar que Python este instalado
        echo.
        pause
    )
)
