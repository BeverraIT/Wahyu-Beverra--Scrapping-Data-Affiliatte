# -*- coding: utf-8 -*-
"""
LANGKAH 1 (jalankan ini duluan, sekali saja).

Buka halaman Affiliate Center pakai profil toko, lalu REKAM semua XHR yang
lewat sementara kamu klik-klik manual. Hasilnya dipakai untuk mengunci
endpoint + nama field asli, sebelum otomatisasi penuh dinyalakan.

Cara pakai:
  python rekam_endpoint.py

Lalu di jendela Chrome yang muncul, lakukan MANUAL:
  1. masuk ke Analitik Produk
  2. set periode 1 bulan
  3. buka detail produk top 1
  4. buka tab daftar creator-nya, scroll sampai bawah
Tekan ENTER di terminal kalau sudah. Semua response tersimpan di
hasil/rekaman_endpoint.json + ringkasannya dicetak.
"""
import json
import os
import sys
import time

import konfigurasi as K
from mesin_cdp import Mesin


def ringkas(obj, kedalaman=0, maks=3):
    """Tampilkan struktur JSON tanpa membanjiri layar."""
    pad = "  " * kedalaman
    if kedalaman > maks:
        return pad + "..."
    if isinstance(obj, dict):
        baris = []
        for k, v in list(obj.items())[:25]:
            if isinstance(v, (dict, list)):
                baris.append(f"{pad}{k}:")
                baris.append(ringkas(v, kedalaman + 1, maks))
            else:
                baris.append(f"{pad}{k}: {str(v)[:60]}")
        return "\n".join(baris)
    if isinstance(obj, list):
        if not obj:
            return pad + "[] (kosong)"
        return f"{pad}[list, {len(obj)} item] contoh item:\n" + ringkas(obj[0], kedalaman + 1, maks)
    return pad + str(obj)[:60]


def main():
    nama_toko, cfg = K.toko_dari_argv(sys.argv)[0]
    print(f"[i] Toko: {nama_toko}")
    print(f"[i] Profil: {cfg['profil_chrome']} ({cfg.get('profil_dir') or 'Default'})")
    print(f"[i] shop_id: {cfg['shop_id']}  |  port CDP: {cfg.get('port_cdp') or K.PORT_CDP}")

    m = Mesin(cfg["profil_chrome"],
              port=cfg.get("port_cdp"),
              profil_dir=cfg.get("profil_dir")).buka()
    try:
        # tampilkan jendela supaya bisa diklik manual
        url = f"{K.URL_DASAR}?shop_region=ID&shop_id={cfg['shop_id']}&platform_data_source=shop"
        m.buka_url(url, tunggu=5)
        print()
        if m.dilampirkan:
            print("=== Tab BARU dibuka di Chrome toko yang sudah kamu jalankan. ===")
            print("Pakai tab itu, jangan ditutup sampai perekaman selesai.")
        else:
            if not K.OFFSCREEN:
                m.tampilkan_jendela()   # jaga-jaga: jendela kadang bergeser lagi
            print("=== Chrome terbuka di pojok kiri atas layar. ===")
            print("Kalau tetap tidak kelihatan: pastikan OFFSCREEN = False di konfigurasi.py,")
            print("dan tutup dulu semua Chrome yang memakai profil toko ini.")
        alamat = m.js("location.href") or ""
        if "errorpage" in alamat or "login" in alamat:
            print(f"[!] Halaman dilempar ke: {alamat}")
            print("[!] Berarti profil ini belum login atau shop_id salah.")
            print("[!] Cek 'profil_chrome' / 'profil_dir' / 'shop_id' di konfigurasi.py.")
        m.rekam_klik()
        print("Lakukan langkah manual (analitik produk -> periode 1 bulan -> detail produk 1 -> daftar creator).")
        print("Klik-klikmu ikut direkam supaya langkah itu bisa diotomatiskan.")
        input("\nTekan ENTER kalau sudah selesai... ")

        jejak = m.ambil_klik()
        if jejak:
            jalur_klik = os.path.join(K.DIR_HASIL, "rekaman_klik.json")
            with open(jalur_klik, "w", encoding="utf-8") as f:
                json.dump(jejak, f, ensure_ascii=False, indent=1)
            print(f"[OK] {len(jejak)} klik tersimpan: {jalur_klik}")
        else:
            print("[!] Tidak ada klik terekam.")

        time.sleep(1)
        print(f"[i] {len(m.respon_masuk)} XHR terekam, mengambil isinya...")
        kumpulan = []
        for r in m.respon_masuk:
            body = m.ambil_body(r["request_id"])
            if not body:
                continue
            item = {"url": r["url"], "status": r["status"], "body": body[:200000]}
            kumpulan.append(item)

        jalur = os.path.join(K.DIR_HASIL, "rekaman_endpoint.json")
        with open(jalur, "w", encoding="utf-8") as f:
            json.dump(kumpulan, f, ensure_ascii=False, indent=1)
        print(f"[OK] Tersimpan: {jalur}")

        print("\n===== KANDIDAT ENDPOINT DATA =====")
        for item in kumpulan:
            try:
                data = json.loads(item["body"])
            except Exception:
                continue
            teks = item["body"].lower()
            skor = sum(k in teks for k in
                       ("creator", "author", "nickname", "gmv", "product", "unique_id"))
            if skor < 2:
                continue
            print("\n" + "-" * 70)
            print(item["url"][:160])
            print(ringkas(data))
    finally:
        m.tutup()


if __name__ == "__main__":
    main()
