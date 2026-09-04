# -*- coding: utf-8 -*-
"""
Semua lokasi folder, dihitung saat jalan -- tidak ada path komputer tertentu
yang ditulis di kode. Ini yang membuat aplikasi bisa dipakai di PC siapa pun.

Pembagiannya:
  * hasil + log + toko.json  -> di sebelah aplikasi, gampang dicari orang.
    Kalau foldernya tidak boleh ditulisi (mis. dipasang di Program Files),
    pindah ke Documents.
  * profil Chrome            -> selalu di LOCALAPPDATA. Ukurannya ratusan MB,
    isinya sesi login pribadi, dan TIDAK boleh ikut tersalin waktu folder
    aplikasi dibagikan ke orang lain.
"""
import os
import sys

NAMA_APP = "TarikCreatorAffiliate"


def _bisa_tulis(folder):
    try:
        os.makedirs(folder, exist_ok=True)
        uji = os.path.join(folder, ".uji_tulis")
        with open(uji, "w") as f:
            f.write("x")
        os.remove(uji)
        return True
    except Exception:
        return False


def _folder_aplikasi():
    if getattr(sys, "frozen", False):          # kalau dibungkus jadi .exe
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


BASE = _folder_aplikasi()

if _bisa_tulis(BASE):
    DIR_KERJA = BASE
else:
    DIR_KERJA = os.path.join(os.path.expanduser("~"), "Documents", NAMA_APP)
    os.makedirs(DIR_KERJA, exist_ok=True)

DIR_DATA = os.path.join(
    os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), NAMA_APP)
DIR_PROFIL = os.path.join(DIR_DATA, "profil")

DIR_HASIL = os.path.join(DIR_KERJA, "hasil")
DIR_MENTAH = os.path.join(DIR_HASIL, "mentah")
DIR_LOG = os.path.join(DIR_KERJA, "logs")
DIR_SS = os.path.join(DIR_KERJA, "debug_screenshots")

# Daftar toko: ikut dibagikan bersama aplikasi (shop_id bukan rahasia).
BERKAS_TOKO = os.path.join(DIR_KERJA, "toko.json")
# Setelan pribadi (toko mana yang dicentang, periode terakhir): per komputer.
BERKAS_SETELAN = os.path.join(DIR_DATA, "setelan.json")

for _d in (DIR_DATA, DIR_PROFIL, DIR_HASIL, DIR_MENTAH, DIR_LOG, DIR_SS):
    os.makedirs(_d, exist_ok=True)


def profil_toko(slug):
    """Folder profil Chrome milik aplikasi untuk satu toko."""
    return os.path.join(DIR_PROFIL, slug)
