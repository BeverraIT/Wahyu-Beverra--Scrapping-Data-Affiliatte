@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Tarik Creator Affiliate - Menu Lanjutan

echo ==========================================
echo   TARIK CREATOR AFFILIATE - MENU LANJUTAN
echo   (pemakai biasa: klik Jalankan.bat)
echo ==========================================
echo.
echo   [7] Cek semua toko (cepat, sebelum tarik)
echo   [5] Impor sesi login dari Chrome lama (jarang dipakai)
echo   [1] Rekam endpoint (jalankan sekali di awal)
echo   [2] Tarik data creator (otomatis)
echo   [6] Rakit dari rekaman (tanpa tarik ulang)
echo   [3] Buat Excel siap paste
echo   [4] Tarik + buat Excel sekaligus
echo   [0] Keluar
echo.
set /p pilih=Pilih menu:

if "%pilih%"=="7" python cek_toko.py
if "%pilih%"=="5" echo Memindahkan sesi dari Chrome lama: python impor_profil.py --dari ^<folder^>
if "%pilih%"=="5" echo Untuk login biasa: buka Jalankan.bat lalu klik "Login Toko".
if "%pilih%"=="1" python rekam_endpoint.py
if "%pilih%"=="2" python tarik_creator.py
if "%pilih%"=="6" (python dari_rekaman.py && python generate_excel.py)
if "%pilih%"=="3" python generate_excel.py
if "%pilih%"=="4" (python tarik_creator.py && python generate_excel.py)
if "%pilih%"=="0" exit

echo.
pause
