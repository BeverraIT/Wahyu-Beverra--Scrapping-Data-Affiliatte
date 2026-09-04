@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title Perbarui Tarik Creator Affiliate

rem  File .bat WAJIB CRLF. Lihat catatan di Jalankan.bat.

echo ============================================
echo   PERBARUI APLIKASI
echo ============================================
echo.

where git >nul 2>&1
if not errorlevel 1 goto ada_git

echo   Git belum terpasang di komputer ini.
echo.
echo   Pasang dulu dari https://git-scm.com/download/win
echo   (pilihan bawaannya sudah benar, tinggal Next terus)
echo.
pause
exit /b 1

:ada_git
git rev-parse --is-inside-work-tree >nul 2>&1
if not errorlevel 1 goto ada_repo

echo   Folder ini bukan hasil "git clone", jadi tidak bisa diperbarui
echo   otomatis.
echo.
echo   Minta alamat repo ke admin, lalu di folder kosong jalankan:
echo     git clone ^<alamat-repo^> TarikCreator
echo.
pause
exit /b 1

:ada_repo
echo   Mengambil pembaruan...
echo.
git pull --ff-only
if not errorlevel 1 goto pull_ok

echo.
echo   Gagal memperbarui.
echo.
echo   Biasanya karena ada file di folder ini yang ikut berubah.
echo   Kalau kamu tidak pernah mengedit kodenya, buang perubahan itu:
echo.
echo     git restore .
echo.
echo   lalu jalankan Perbarui.bat lagi. Kalau masih gagal, minta bantuan admin.
echo.
pause
exit /b 1

:pull_ok
echo.
echo   Selesai. Membuka aplikasi...
echo.
call Jalankan.bat
exit /b 0
