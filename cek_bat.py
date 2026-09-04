# -*- coding: utf-8 -*-
"""
Cek file .bat sebelum dibagikan ke komputer lain.

File .bat dengan akhir baris LF saja akan salah dibaca cmd.exe: sebagian
perintah jalan, sisanya tertelan, jendelanya tutup tanpa pesan apa pun.
Susah dilacak karena tidak ada error sama sekali -- makanya dicek di sini.

  python cek_bat.py
"""
import glob
import os
import sys


def periksa(jalur):
    b = open(jalur, "rb").read()
    crlf = b.count(b"\r\n")
    lf = b.count(b"\n") - crlf
    bom = b[:3] == b"\xef\xbb\xbf"
    masalah = []
    if lf:
        masalah.append(f"{lf} baris berakhir LF saja (harus CRLF)")
    if bom:
        masalah.append("ada BOM di awal file (baris pertama jadi tidak terbaca)")
    return crlf, lf, bom, masalah


def main():
    berkas = sorted(glob.glob("*.bat"))
    if not berkas:
        print("Tidak ada file .bat di folder ini.")
        return 0

    rusak = 0
    print(f"{'file':24} {'CRLF':>6} {'LF':>5}  status")
    print("-" * 62)
    for f in berkas:
        crlf, lf, bom, masalah = periksa(f)
        if masalah:
            rusak += 1
            print(f"{f:24} {crlf:6} {lf:5}  RUSAK")
            for m in masalah:
                print(f"{'':24} {'':6} {'':5}  -> {m}")
        else:
            print(f"{f:24} {crlf:6} {lf:5}  ok")

    print()
    if rusak:
        print(f"{rusak} file .bat bermasalah.")
        print("Perbaiki: buka di Notepad++ / VS Code, ganti akhir baris ke CRLF,")
        print("simpan. Atau jalankan: python cek_bat.py --perbaiki")
        if "--perbaiki" in sys.argv:
            print()
            for f in berkas:
                _, lf, bom, masalah = periksa(f)
                if not masalah:
                    continue
                b = open(f, "rb").read()
                if bom:
                    b = b[3:]
                b = b.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
                open(f, "wb").write(b)
                print(f"[OK] {f} diperbaiki")
        return 1

    print("Semua file .bat aman untuk dibagikan.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
