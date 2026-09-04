# -*- coding: utf-8 -*-
"""
JALUR CADANGAN: rekaman -> JSON mentah, tanpa menarik ulang.

`rekam_endpoint.py` sudah menyimpan semua response XHR yang lewat sementara
kamu klik manual. Kalau klik manualmu tadi sudah melewati 10 produk dan 5
halaman creator per produk, datanya sebenarnya sudah lengkap di rekaman itu
-- tidak perlu menarik ulang.

Berguna dua hal:
  * langsung dapat Excel tanpa menunggu otomatisasi UI terbukti jalan
  * kalau suatu saat tampilan Affiliate Center berubah dan tarik_creator.py
    macet, rekam manual tetap bisa jadi jalan keluar

  python dari_rekaman.py
  python generate_excel.py
"""
import json
import os
import sys

import konfigurasi as K
import tarik_creator as T


def main():
    jalur_rekaman = os.path.join(K.DIR_HASIL, "rekaman_endpoint.json")
    if not os.path.exists(jalur_rekaman):
        print("[x] Belum ada hasil/rekaman_endpoint.json. Jalankan rekam_endpoint.py dulu.")
        return 1

    nama_toko, _ = K.toko_dari_argv(sys.argv)[0]
    with open(jalur_rekaman, encoding="utf-8") as f:
        rekaman = json.load(f)

    # --- produk: ambil segmen periode yang cocok, urutan dari server (GMV desc)
    produk, lihat = [], set()
    for it in rekaman:
        if K.ENDPOINT_PRODUK not in it["url"]:
            continue
        for seg in T.baca_segmen(it["body"]):
            if not T.periode_segmen_cocok(seg):
                continue
            for b in seg["baris"]:
                pid = T.teks(T.jalur(b, "product_meta.id"))
                if pid and pid not in lihat:
                    lihat.add(pid)
                    produk.append(b)

    # --- creator: kelompokkan per product_id, urutan halaman dipertahankan
    per_produk = {}
    for it in rekaman:
        if K.ENDPOINT_CREATOR not in it["url"]:
            continue
        for seg in T.baca_segmen(it["body"]):
            if not T.periode_segmen_cocok(seg):
                continue
            pid = T.teks(seg["filter"].get("product_id"))
            if not pid:
                continue
            simpan = per_produk.setdefault(pid, {"urut": [], "lihat": set()})
            for c in seg["baris"]:
                kunci = T.id_creator(c) or json.dumps(c, sort_keys=True)[:120]
                if kunci in simpan["lihat"]:
                    continue
                simpan["lihat"].add(kunci)
                simpan["urut"].append(c)

    if not produk:
        print(f"[x] Tidak ada data produk periode {T.AWAL} s/d {T.AKHIR} di rekaman.")
        print("[x] Periksa PERIODE_MANUAL di konfigurasi.py, atau rekam ulang.")
        return 1

    hasil = {"toko": nama_toko, "periode": T.LABEL,
             "awal": str(T.AWAL), "akhir": str(T.AKHIR), "produk": []}
    for i, p in enumerate(produk[:K.JUMLAH_PRODUK_TOP], 1):
        pid = T.teks(T.jalur(p, "product_meta.id"))
        nama = T.teks(T.jalur(p, "product_meta.name")) or f"Produk {i}"
        creator = per_produk.get(pid, {}).get("urut", [])[:K.JUMLAH_CREATOR_PER_PRODUK]
        tanda = "" if len(creator) >= K.JUMLAH_CREATOR_PER_PRODUK else "   <- KURANG"
        print(f"  [{i:2}] {len(creator):3} creator  {nama[:48]}{tanda}")
        hasil["produk"].append({
            "peringkat": i, "product_id": pid, "nama_produk": nama,
            "ringkasan_produk": p, "creator": creator,
        })

    berkas = os.path.join(
        K.DIR_MENTAH, f"{nama_toko.replace(' ', '_')}_{T.AWAL:%Y-%m}.json")
    with open(berkas, "w", encoding="utf-8") as f:
        json.dump(hasil, f, ensure_ascii=False, indent=1)
    total = sum(len(p["creator"]) for p in hasil["produk"])
    print(f"\n[OK] {len(hasil['produk'])} produk, {total} baris creator")
    print(f"[OK] Tersimpan: {berkas}")
    print("\nLanjut: python generate_excel.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
