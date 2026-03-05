@echo off
echo ========================================
echo Seven Knights Multi Screen - Builder
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/5] Skipping pip install (assuming dependencies are met)...

echo.
echo [2/5] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "obfuscated" rmdir /s /q "obfuscated"
REM Don't delete SevenKnightsKiller.spec - we need it!
echo [OK] Cleaned

echo.
echo [3/5] Obfuscating code with PyArmor...
pyarmor gen -O obfuscated kill_bootstrap_ui.py
if errorlevel 1 (
    echo [ERROR] PyArmor obfuscation failed
    pause
    exit /b 1
)
echo [OK] Code obfuscated

echo.
echo [4/5] Building executable with PyInstaller...
pyinstaller --clean -F -w -n SevenKnightsMultiScreen -i icon.ico --add-data "icon.ico;." --collect-all customtkinter --hidden-import customtkinter obfuscated\kill_bootstrap_ui.py
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed
    echo [TIP] Try running: pip install --upgrade pyinstaller
    pause
    exit /b 1
)
echo [OK] Executable built

echo.
echo [5/5] Cleaning up temporary files...
rmdir /s /q "obfuscated"
rmdir /s /q "build"
echo [OK] Cleaned up

echo.
echo ========================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Output: dist\SevenKnightsMultiScreen.exe
echo.
pause
