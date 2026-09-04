# -*- coding: utf-8 -*-
"""
Cek cepat semua toko sebelum menarik data sungguhan.

Untuk tiap toko: buka Affiliate Center pakai profil aplikasi, pastikan tidak
dilempar ke halaman login, dan pastikan endpoint product/list benar-benar
menjawab. Sekitar 15-60 detik per toko -- jauh lebih murah daripada tahu ada
toko bermasalah setelah menunggu penarikan tujuh toko.

Isi pengecekannya ada di akun.py, dipakai bareng dengan tombol "Cek" di
aplikasi supaya hasil keduanya tidak pernah berbeda.

Jalan di latar belakang (headless) mengikuti setelan aplikasi. Pakai
--tampil kalau mau melihat halamannya, mis. waktu mencari tahu kenapa
sebuah toko gagal.

CATATAN: menyembunyikan dengan cara memindahkan jendela ke luar layar
(OFFSCREEN=True) TIDAK bisa -- sudah diuji, halamannya tidak menarik data
sama sekali karena Chrome menahan halaman yang dianggap tak terlihat.
Headless beda: halamannya tetap dirender.

  python cek_toko.py
  python cek_toko.py --toko kece
  python cek_toko.py --tampil
"""
import sys
import time

import akun
import konfigurasi as K


def main():
    if "--tampil" in sys.argv:
        K.TAMPILKAN_BROWSER = True
    daftar = K.toko_dari_argv(sys.argv)
    print(f"Cek {len(daftar)} toko (periode bawaan halaman, bukan periode target)\n")
    semua = []
    for i, (nama, cfg) in enumerate(daftar, 1):
        print(f"[{i}/{len(daftar)}] {nama} ... ", end="", flush=True)
        h = akun.cek(nama, cfg, log=lambda *_: None)
        semua.append(h)
        print(f"{h['status']} - {h['pesan']}  ({h['periode']})")
        time.sleep(1)

    print("\n" + "=" * 62)
    ok = [h for h in semua if h["status"] == akun.SIAP]
    print(f"{len(ok)}/{len(semua)} toko siap ditarik")
    for h in semua:
        if h["status"] != akun.SIAP:
            print(f"  [X] {h['toko']}: {h['status']} - {h['pesan']}")
            if h["url"]:
                print(f"      URL akhir: {h['url'][:90]}")
    if len(ok) < len(semua):
        print("\nToko yang gagal: buka aplikasinya (Jalankan.bat),")
        print('lalu klik "Login Toko" di baris toko itu.')
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
