@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title Tarik Creator Affiliate

rem ============================================================
rem  CATATAN UNTUK YANG MENGEDIT FILE INI
rem
rem  1. File .bat WAJIB disimpan dengan akhir baris CRLF (Windows).
rem     Kalau tersimpan LF saja, cmd.exe salah membaca blok if(...)
rem     dan skrip berhenti di tengah tanpa pesan apa-apa.
rem  2. Hindari blok if(...) bertingkat. Pakai label + goto seperti
rem     di bawah: lebih panjang, tapi tidak bisa salah baca.
rem  3. Jangan pakai file penanda untuk menandai "sudah terpasang".
rem     Penanda ikut tersalin ke PC lain dan bikin pemasangan
rem     dilewati padahal modulnya belum ada. Tanya Python langsung.
rem ============================================================

rem ---------- cari Python ----------
set "PY="
where py >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if defined PY goto ada_python

where python >nul 2>&1
if not errorlevel 1 set "PY=python"
if defined PY goto ada_python

echo.
echo   Python belum terpasang di komputer ini.
echo.
echo   Pasang dulu dari https://www.python.org/downloads/
echo   PENTING: centang "Add Python to PATH" waktu memasang.
echo.
pause
exit /b 1

:ada_python
%PY% --version
if errorlevel 1 goto python_rusak

rem ---------- cek kebutuhan langsung ke Python ----------
%PY% -c "import requests, websocket, openpyxl" >nul 2>&1
if not errorlevel 1 goto cek_tkinter

echo.
echo   Menyiapkan aplikasi. Sekali saja di komputer ini, mohon tunggu...
echo.
%PY% -m pip install --disable-pip-version-check websocket-client requests openpyxl
if not errorlevel 1 goto pasang_selesai

echo.
echo   Coba lagi tanpa hak administrator...
echo.
%PY% -m pip install --user --disable-pip-version-check websocket-client requests openpyxl

:pasang_selesai
%PY% -c "import requests, websocket, openpyxl" >nul 2>&1
if not errorlevel 1 goto cek_tkinter

echo.
echo   Gagal memasang kebutuhan aplikasi.
echo.
echo   Coba salah satu:
echo     1. Pastikan komputer ini terhubung internet, lalu jalankan lagi.
echo     2. Buka Command Prompt, ketik perintah ini:
echo        %PY% -m pip install websocket-client requests openpyxl
echo     3. Kalau internet kantor memblokirnya, minta bantuan IT.
echo.
pause
exit /b 1

:cek_tkinter
rem tkinter tidak bisa dipasang lewat pip, jadi dicek terpisah
%PY% -c "import tkinter" >nul 2>&1
if not errorlevel 1 goto buka_aplikasi

echo.
echo   Python di komputer ini tidak punya tkinter, jadi jendela aplikasi
echo   tidak bisa dibuka.
echo.
echo   Pasang ulang Python dari python.org (installer resminya sudah
echo   membawa tkinter), centang "Add Python to PATH".
echo.
pause
exit /b 1

:buka_aplikasi
%PY% gui.py
if not errorlevel 1 goto selesai

echo.
echo   Aplikasi berhenti karena ada masalah. Pesannya ada di atas.
echo.
pause
exit /b 1

:python_rusak
echo.
echo   Python ketemu tapi tidak bisa dijalankan.
echo   Pasang ulang dari https://www.python.org/downloads/
echo.
pause
exit /b 1

:selesai
exit /b 0
