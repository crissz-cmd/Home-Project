@echo off
setlocal
cd /d "%~dp0"
if "%SCAP_PUBLIC_KEY_B64%"=="" (
  echo ERROR: Set SCAP_PUBLIC_KEY_B64 before building.
  exit /b 1
)
python -m pip install --upgrade pip
if errorlevel 1 exit /b 1
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
> license_public_key.py echo # Generated for this build.
>> license_public_key.py echo PUBLIC_KEY_B64 = "%SCAP_PUBLIC_KEY_B64%"
python -m PyInstaller --clean --noconfirm ScapHolders.spec
if errorlevel 1 exit /b 1
if not exist "dist\ScapHolders.exe" (
  echo ERROR: PyInstaller did not produce dist\ScapHolders.exe
  exit /b 1
)
echo BUILD COMPLETE: dist\ScapHolders.exe
endlocal
