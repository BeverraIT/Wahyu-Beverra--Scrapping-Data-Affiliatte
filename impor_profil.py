# -*- coding: utf-8 -*-
"""
Pindahkan sesi login dari Chrome lain ke profil milik aplikasi.

Dipakai SEKALI saja, kalau di komputer ini sudah ada Chrome yang login ke
toko-toko itu dan sayang kalau harus login ulang satu per satu. Orang baru
di kantor tidak butuh ini -- cukup klik "Login Toko" di aplikasinya.

  python impor_profil.py --dari "C:\\Users\\User\\ChromeToko"
  python impor_profil.py --dari "..." --toko yarra

Untuk tiap toko, folder sumber dicari berdasarkan slug (mis. "yarra" akan
mencocokkan folder "yarra_bot" lalu "yarra"), lalu di dalamnya dipilih
profile-directory yang cookie SESI-nya (seller-id + affiliate-id) paling
banyak -- bukan yang total cookienya paling banyak. Hasilnya disalin jadi "Default" di profil aplikasi.

Chrome sumber harus ditutup dulu: file cookie SQLite yang sedang dipakai
tidak bisa disalin utuh.
"""
import os
import shutil
import sqlite3
import sys
import tempfile

import konfigurasi as K
from mesin_cdp import chrome_pakai_profil, salin_profil


def _nilai_sesi(profil_dir):
    """Seberapa 'sudah login' profile-directory ini.

    Sengaja HANYA menghitung cookie seller-id + affiliate-id, bukan semua
    cookie tokopedia. Folder "Default" biasanya punya cookie tokopedia
    terbanyak (iklan, tracking) padahal justru bukan yang login -- sesi
    aslinya ada di folder bernama toko."""
    ck = os.path.join(profil_dir, "Network", "Cookies")
    if not os.path.exists(ck):
        return 0
    tmp = tempfile.mkdtemp()
    try:
        salin = os.path.join(tmp, "c.db")
        shutil.copy2(ck, salin)
        con = sqlite3.connect(salin)
        n = con.execute(
            "SELECT count(*) FROM cookies WHERE host_key LIKE '%seller-id%'"
            " OR host_key LIKE '%affiliate-id%'").fetchone()[0]
        con.close()
        return n
    except Exception:
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def cari_sumber(akar, slug):
    """Cari (user_data_dir, profile_directory) yang sesinya paling lengkap."""
    kandidat_induk = [os.path.join(akar, slug + "_bot"), os.path.join(akar, slug)]
    terbaik = None
    for induk in kandidat_induk:
        if not os.path.isdir(induk):
            continue
        for prof in sorted(os.listdir(induk)):
            pd = os.path.join(induk, prof)
            if not os.path.isdir(pd):
                continue
            n = _nilai_sesi(pd)
            if n and (terbaik is None or n > terbaik[2]):
                terbaik = (induk, prof, n)
    return terbaik


def main():
    if "--dari" not in sys.argv:
        print(__doc__)
        return 1
    akar = sys.argv[sys.argv.index("--dari") + 1]
    if not os.path.isdir(akar):
        print(f"[x] Folder tidak ada: {akar}")
        return 1

    daftar = K.toko_dari_argv(sys.argv) if "--toko" in sys.argv else list(K.TOKO.items())
    berhasil = kosong = 0
    for nama, cfg in daftar:
        print(f"\n=== {nama} (slug: {cfg['slug']})")
        temu = cari_sumber(akar, cfg["slug"])
        if not temu:
            print(f"  [-] tidak ketemu profil yang sudah login di {akar}")
            kosong += 1
            continue
        induk, prof, n = temu
        print(f"  sumber: {induk}  [{prof}]  ({n} cookie sesi)")

        if chrome_pakai_profil(induk):
            print("  [x] Chrome yang memakai profil itu MASIH JALAN. Tutup dulu.")
            kosong += 1
            continue
        try:
            hasil = salin_profil(induk, cfg["profil_chrome"], prof,
                                 bersih=True, log=lambda t: print("  " + t),
                                 profil_dir_tujuan="Default")
        except Exception as e:
            print(f"  [x] gagal: {e}")
            kosong += 1
            continue
        print(f"  [OK] -> {hasil}")
        berhasil += 1

    print("\n" + "=" * 56)
    print(f"{berhasil} toko terimpor, {kosong} dilewati")
    if berhasil:
        print("\nCek hasilnya:  python cek_toko.py")
        print("Toko yang gagal: buka aplikasinya, klik \"Login Toko\".")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
