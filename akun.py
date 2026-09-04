# -*- coding: utf-8 -*-
"""
Login toko dan cek status, tanpa menyalin profil dari mana pun.

Tiap toko punya folder profil Chrome milik aplikasi sendiri di LOCALAPPDATA.
Pertama kali dipakai folder itu kosong: Chrome dibuka ke halaman Affiliate
Center, orang login seperti biasa, sesinya tersimpan di situ selamanya.

Dipakai oleh gui.py dan cek_toko.py.
"""
import os
import time

import konfigurasi as K

# mesin_cdp butuh requests + websocket-client. Sengaja diimpor di dalam
# fungsi, bukan di sini: supaya jendela aplikasi tetap bisa dibuka dan
# menampilkan pesan yang bisa dimengerti kalau modulnya belum terpasang,
# bukan traceback ModuleNotFoundError di layar hitam.

# Status yang mungkin
SIAP = "SIAP"
BELUM_LOGIN = "BELUM LOGIN"
BELUM_ADA = "BELUM DISIAPKAN"
LAMBAT = "TIDAK ADA DATA"
GAGAL = "GAGAL"


def url_toko(cfg):
    return (f"{K.URL_DASAR}?shop_region=ID&shop_id={cfg['shop_id']}"
            f"&platform_data_source=shop")


def sudah_ada_profil(cfg):
    """Profil sudah pernah dipakai login? (bukan jaminan sesinya masih hidup)"""
    return os.path.exists(os.path.join(
        cfg["profil_chrome"], cfg.get("profil_dir") or "Default",
        "Network", "Cookies"))


def _mesin(cfg, log):
    from mesin_cdp import Mesin
    return Mesin(cfg["profil_chrome"], log=log,
                 port=cfg.get("port_cdp"),
                 profil_dir=cfg.get("profil_dir")).buka()


def cek(nama_toko, cfg, log=print, batas=60):
    """Buka Affiliate Center, laporkan apakah toko ini siap ditarik.

    Dikembalikan dict: status, pesan, produk, periode, url.
    """
    hasil = {"toko": nama_toko, "status": GAGAL, "pesan": "",
             "produk": 0, "periode": "-", "url": ""}

    if not cfg.get("shop_id"):
        hasil.update(status=GAGAL, pesan="shop_id belum diisi")
        return hasil
    if not sudah_ada_profil(cfg):
        hasil.update(status=BELUM_ADA, pesan="belum pernah login di aplikasi ini")
        return hasil

    import tarik_creator as T          # diimpor di sini supaya GUI cepat dibuka
    try:
        m = _mesin(cfg, log=lambda *_: None)
    except Exception as e:
        hasil.update(status=GAGAL, pesan=f"Chrome tidak bisa dibuka: {e}")
        return hasil
    try:
        m.bersihkan_respon()
        m.buka_url(url_toko(cfg), tunggu=5)
        # 60 detik: profil yang baru pertama dinyalakan (cache dingin) pernah
        # butuh >35 detik sampai product/list menjawab.
        baris, _ = T.tunggu_baris(m, K.ENDPOINT_PRODUK, 1, batas=batas,
                                  hanya_periode=False)
        hasil["url"] = (m.js("location.href") or "")[:120]
        hasil["produk"] = len(baris)
        if "login" in hasil["url"] or "errorpage" in hasil["url"]:
            hasil.update(status=BELUM_LOGIN, pesan="sesi login habis, login lagi")
        elif not baris:
            hasil.update(status=LAMBAT,
                         pesan=f"tidak ada data dalam {batas} detik")
        else:
            got = m.panen_respon(pola=[K.ENDPOINT_PRODUK])
            r = T.rentang(T.baca_segmen(got[0]["body"])[0]["waktu"]) if got else None
            hasil["periode"] = f"{r[0]} s/d {r[1]}" if r else "-"
            hasil.update(status=SIAP, pesan=f"{len(baris)} produk terbaca")
    except Exception as e:
        hasil.update(status=GAGAL, pesan=f"{type(e).__name__}: {e}")
    finally:
        m.tutup()
    return hasil


def login(nama_toko, cfg, log=print, batas_menit=10, berhenti=None):
    """Buka Chrome ke Affiliate Center dan tunggu sampai orangnya selesai login.

    Selesai dideteksi sendiri: halaman berhenti di Affiliate Center (bukan
    halaman login) DAN endpoint product/list menjawab. Jadi tidak perlu
    menebak-nebak kapan login beres.

    `berhenti` = fungsi yang mengembalikan True kalau user membatalkan.
    """
    if not cfg.get("shop_id"):
        return False, "shop_id belum diisi"

    import tarik_creator as T
    log(f"[{nama_toko}] membuka Chrome...")
    try:
        m = _mesin(cfg, log=log)
    except Exception as e:
        return False, f"Chrome tidak bisa dibuka: {e}"
    try:
        m.bersihkan_respon()
        m.buka_url(url_toko(cfg), tunggu=4)
        log(f"[{nama_toko}] Silakan login di jendela Chrome yang terbuka.")
        log(f"[{nama_toko}] Jendela akan menutup sendiri kalau sudah berhasil.")

        tenggat = time.time() + batas_menit * 60
        while time.time() < tenggat:
            if berhenti and berhenti():
                return False, "dibatalkan"
            baris, _ = T.panen(m, K.ENDPOINT_PRODUK, hanya_periode=False)
            if baris:
                log(f"[{nama_toko}] Login berhasil, {len(baris)} produk terbaca.")
                return True, "login berhasil"
            time.sleep(2)
        return False, f"belum selesai dalam {batas_menit} menit"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
    finally:
        m.tutup()
