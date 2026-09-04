# -*- coding: utf-8 -*-
"""
LANGKAH 0: siapkan profil bot.

Salin sesi login toko dari Chrome KERJAAN ke profil terpisah, supaya
otomatisasi jalan di jendelanya sendiri dan tidak mengganggu Chrome yang
kamu pakai sehari-hari.

  python siapkan_profil.py           <- salin / segarkan sesi login
  python siapkan_profil.py --bersih  <- hapus profil bot lalu salin dari nol
  python siapkan_profil.py --paksa   <- lanjut walau Chrome sumber masih jalan

Chrome sumber HARUS ditutup dulu. Kalau masih hidup, file cookie-nya
(SQLite) terkunci dan salinannya bisa setengah jadi -- gejalanya: profil bot
kelihatan normal tapi tetap dilempar ke /errorpage.

Ulangi langkah ini kalau suatu saat bot kena /errorpage lagi: berarti sesi
login salinannya sudah kedaluwarsa.
"""
import os
import sys

import konfigurasi as K
from mesin_cdp import chrome_pakai_profil, salin_profil


def satu_toko(nama_toko, cfg, bersih, paksa):
    sumber = cfg.get("profil_sumber")
    tujuan = cfg["profil_chrome"]
    profil_dir = cfg.get("profil_dir") or "Default"

    if not sumber:
        print("[x] Toko ini tidak punya profil sumber untuk disalin.")
        print("[x] Cara yang dipakai sekarang: buka aplikasinya (Jalankan.bat),")
        print('[x] klik "Login Toko" di baris toko ini. Untuk memindahkan sesi')
        print("[x] dari Chrome lama, pakai: python impor_profil.py --dari <folder>")
        return 1

    print(f"[i] Toko    : {nama_toko}")
    print(f"[i] Sumber  : {sumber}  ({profil_dir})")
    print(f"[i] Tujuan  : {tujuan}  ({profil_dir})")
    print()

    if os.path.normcase(os.path.abspath(sumber)) == os.path.normcase(os.path.abspath(tujuan)):
        print("[x] profil_sumber dan profil_chrome sama. Profil bot harus folder terpisah.")
        return 1

    if chrome_pakai_profil(sumber):
        print("[!] Chrome yang memakai profil sumber MASIH JALAN.")
        print("[!] Tutup dulu semua jendelanya, baru ulangi perintah ini.")
        if not paksa:
            print("[!] (kalau yakin mau lanjut: python siapkan_profil.py --paksa)")
            return 1
        print("[!] --paksa dipakai, lanjut walau berisiko salinan setengah jadi.")

    if chrome_pakai_profil(tujuan):
        print("[x] Chrome bot masih jalan memakai profil tujuan. Tutup dulu.")
        return 1

    try:
        hasil = salin_profil(sumber, tujuan, profil_dir, bersih=bersih)
    except Exception as e:
        print(f"[x] Gagal menyalin: {e}")
        return 1

    print(f"[OK] Profil bot siap: {hasil}")
    print(f"[OK] Port bot: {cfg.get('port_cdp') or K.PORT_CDP}")
    return 0


def main():
    bersih = "--bersih" in sys.argv
    paksa = "--paksa" in sys.argv
    daftar = K.toko_dari_argv(sys.argv)

    gagal = []
    for i, (nama, cfg) in enumerate(daftar, 1):
        print(f"\n===== [{i}/{len(daftar)}] {nama} " + "=" * 30)
        if satu_toko(nama, cfg, bersih, paksa) != 0:
            gagal.append(nama)

    print("\n" + "=" * 50)
    print(f"Selesai: {len(daftar) - len(gagal)} berhasil, {len(gagal)} gagal")
    if gagal:
        print("Gagal: " + ", ".join(gagal))
        return 1
    print("\nLanjut:  python tarik_creator.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
