@echo off
cd /d "%~dp0"
echo ========================================================
echo  Building Arabic Keyboard Fixer (One-File EXE)
echo ========================================================
pyinstaller --noconfirm --onefile --windowed --name "ArabicKeyboardFixer" app.py
echo.
echo ========================================================
echo  Done! Your standalone EXE is in the "dist" folder.
echo ========================================================
pause
