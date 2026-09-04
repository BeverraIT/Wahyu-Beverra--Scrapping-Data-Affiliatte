@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Tarik Creator Affiliate

rem ============================================================
rem  Cari Python
rem ============================================================
set PY=
where py >nul 2>&1 && set PY=py -3
if "%PY%"=="" ( where python >nul 2>&1 && set PY=python )

if "%PY%"=="" (
  echo.
  echo   Python belum terpasang di komputer ini.
  echo.
  echo   Pasang dulu dari https://www.python.org/downloads/
  echo   PENTING: centang "Add Python to PATH" waktu memasang.
  echo.
  pause
  exit /b 1
)

rem ============================================================
rem  Cek kebutuhan dengan MENANYAI Python langsung.
rem
rem  Jangan pernah memakai file penanda seperti ".siap": file itu
rem  ikut tersalin waktu folder aplikasi dibagikan, jadi di PC baru
rem  pemasangan dilewati padahal modulnya belum ada.
rem ============================================================
%PY% -c "import requests, websocket, openpyxl" >nul 2>&1
if errorlevel 1 (
  echo.
  echo   Menyiapkan aplikasi. Sekali saja di komputer ini, mohon tunggu...
  echo.
  %PY% -m pip install --disable-pip-version-check websocket-client requests openpyxl
  if errorlevel 1 (
    echo.
    echo   Coba lagi tanpa hak administrator...
    echo.
    %PY% -m pip install --user --disable-pip-version-check websocket-client requests openpyxl
  )
)

rem ---- pastikan sekarang benar-benar sudah ada ----
%PY% -c "import requests, websocket, openpyxl" >nul 2>&1
if errorlevel 1 (
  echo.
  echo   Gagal memasang kebutuhan aplikasi.
  echo.
  echo   Coba salah satu:
  echo     1. Pastikan komputer ini terhubung internet, lalu jalankan lagi.
  echo     2. Buka Command Prompt, ketik:
  echo        %PY% -m pip install websocket-client requests openpyxl
  echo     3. Kalau kantor memblokir internet, minta bantuan IT.
  echo.
  pause
  exit /b 1
)

rem ---- tkinter tidak bisa dipasang lewat pip, cek terpisah ----
%PY% -c "import tkinter" >nul 2>&1
if errorlevel 1 (
  echo.
  echo   Python di komputer ini tidak punya tkinter, jadi jendela aplikasi
  echo   tidak bisa dibuka.
  echo.
  echo   Pasang ulang Python dari python.org (installer resminya sudah
  echo   membawa tkinter), centang "Add Python to PATH".
  echo.
  pause
  exit /b 1
)

rem ============================================================
rem  Buka aplikasi
rem ============================================================
%PY% gui.py
if errorlevel 1 (
  echo.
  echo   Aplikasi berhenti karena ada masalah. Pesannya ada di atas.
  echo.
  pause
)
