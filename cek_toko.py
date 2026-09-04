# -*- coding: utf-8 -*-
"""
Cek cepat semua toko sebelum menarik data sungguhan.

Untuk tiap toko: buka Affiliate Center pakai profil aplikasi, pastikan tidak
dilempar ke halaman login, dan pastikan endpoint product/list benar-benar
menjawab. Sekitar 15-60 detik per toko -- jauh lebih murah daripada tahu ada
toko bermasalah setelah menunggu penarikan tujuh toko.

Isi pengecekannya ada di akun.py, dipakai bareng dengan tombol "Cek" di
aplikasi supaya hasil keduanya tidak pernah berbeda.

Jendelanya HARUS kelihatan. Sudah diuji: kalau dijalankan di luar layar
(OFFSCREEN=True), halaman ini tidak menarik data sama sekali -- Chrome
menganggap jendelanya tidak terlihat dan menahan fetch-nya. Catatan lama
"jalan headed-tapi-di-luar-layar" dari mesin Tarik Omset TIDAK berlaku di sini.

  python cek_toko.py
  python cek_toko.py --toko kece
"""
import sys
import time

import akun
import konfigurasi as K


def main():
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
