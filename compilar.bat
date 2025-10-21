@echo off
echo ========================================
echo   COMPILAR SMART REPORTS - INSTITUTO HP
echo ========================================
echo.
echo Este proceso puede tardar varios minutos...
echo.

echo [1/2] Verificando PyInstaller...
python -m pip install --upgrade pyinstaller >nul 2>&1

echo.
echo [2/2] Compilando aplicacion a ejecutable...
python -m PyInstaller build_exe.spec --clean --noconfirm

echo.
echo [INFO] Verificando compilacion...
if exist "dist\SmartReports_InstitutoHP.exe" (
    echo.
    echo ========================================
    echo [OK] Compilacion completada con exito!
    echo ========================================
    echo.
    echo El ejecutable se encuentra en:
    echo   dist\SmartReports_InstitutoHP.exe
    echo.
    echo Puedes copiar este archivo a cualquier computadora
    echo con Windows y ejecutarlo directamente.
    echo.
) else (
    echo.
    echo ========================================
    echo [ERROR] La compilacion fallo
    echo ========================================
    echo.
    echo Revisa los mensajes de error anteriores.
    echo.
)

pause
