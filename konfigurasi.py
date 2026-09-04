# -*- coding: utf-8 -*-
"""
Konfigurasi terpusat "Tarik Creator Affiliate".

Daftar tokonya TIDAK lagi ditulis di sini -- dibaca dari toko.json supaya
bisa diubah lewat aplikasi tanpa menyentuh kode, dan supaya file yang sama
bisa dibagikan ke semua PC kantor.
"""
import json
import os
from datetime import date
from calendar import monthrange

import lokasi as L

# ============================================================
# 1. TOKO  (dibaca dari toko.json)
# ============================================================
# Tiap toko punya:
#   nama, slug, shop_id, port          -> dari toko.json
#   profil_chrome                      -> folder profil MILIK APLIKASI,
#                                         di LOCALAPPDATA, dibuat sendiri
#   profil_dir = "Default"             -> profil aplikasi selalu Default;
#                                         tidak menumpang profil Chrome orang
#   aktif                              -> centang di aplikasi, per komputer
#
# Sesi login diisi lewat tombol "Login Toko" di aplikasi, bukan dengan
# menyalin folder profil dari komputer lain.

_BAWAAN = {
    "toko": [
        {"nama": "Toko Baru", "slug": "toko1", "shop_id": "", "port": 9331},
    ]
}


def _muat_json(jalur, bawaan):
    try:
        with open(jalur, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return bawaan
    except Exception as e:
        raise SystemExit(f"{os.path.basename(jalur)} rusak / bukan JSON: {e}")


def muat_setelan():
    return _muat_json(L.BERKAS_SETELAN, {})


def simpan_setelan(setelan):
    with open(L.BERKAS_SETELAN, "w", encoding="utf-8") as f:
        json.dump(setelan, f, ensure_ascii=False, indent=1)


def muat_toko():
    """Bangun ulang TOKO dari toko.json (daftar kantor, ikut git)
    + toko_lokal.json (tambahan sendiri, di luar git) + setelan pribadi."""
    data = _muat_json(L.BERKAS_TOKO, _BAWAAN)
    lokal = _muat_json(L.BERKAS_TOKO_LOKAL, {"toko": []})
    setelan = muat_setelan()
    dicentang = setelan.get("toko_aktif")      # None = semua dianggap aktif

    gabung = list(data.get("toko") or [])
    sudah = {(t.get("nama") or "").strip().lower() for t in gabung}
    for t in (lokal.get("toko") or []):
        # kalau kantor akhirnya menambahkan toko yang sama, versi kantor menang
        if (t.get("nama") or "").strip().lower() not in sudah:
            gabung.append(t)

    hasil = {}
    for i, t in enumerate(gabung):
        nama = (t.get("nama") or "").strip()
        slug = (t.get("slug") or "").strip() or f"toko{i + 1}"
        if not nama:
            continue
        hasil[nama] = {
            "slug": slug,
            "shop_id": str(t.get("shop_id") or "").strip(),
            "profil_chrome": L.profil_toko(slug),
            "profil_dir": "Default",
            "port_cdp": int(t.get("port") or (9331 + i)),
            "aktif": nama in dicentang if dicentang is not None else True,
            # opsional, hanya untuk memindahkan sesi dari Chrome lain
            "profil_sumber": t.get("profil_sumber") or "",
            "profil_dir_sumber": t.get("profil_dir_sumber") or "Default",
        }
    return hasil


def tambah_toko_lokal(nama, cfg):
    """Simpan toko tambahan ke toko_lokal.json (di luar git).

    Sengaja TIDAK menulis ke toko.json: file itu dilacak git, jadi kalau
    tiap orang menambah toko di situ, `git pull` bakal bentrok terus.
    Untuk membagikan toko ke semua orang kantor, pindahkan entrinya ke
    toko.json lalu commit + push.
    """
    isi = _muat_json(L.BERKAS_TOKO_LOKAL, {"toko": []})
    daftar = [t for t in (isi.get("toko") or [])
              if (t.get("nama") or "").strip().lower() != nama.strip().lower()]
    daftar.append({"nama": nama, "slug": cfg["slug"],
                   "shop_id": cfg["shop_id"], "port": cfg["port_cdp"]})
    isi["toko"] = daftar
    isi["_catatan"] = ("Toko tambahan di komputer ini saja, tidak ikut git."
                       " Untuk dipakai sekantor, pindahkan ke toko.json.")
    with open(L.BERKAS_TOKO_LOKAL, "w", encoding="utf-8") as f:
        json.dump(isi, f, ensure_ascii=False, indent=1)


TOKO = muat_toko()


def toko_aktif(nama=None):
    """Toko yang akan dikerjakan. `nama` untuk memilih satu saja."""
    if nama:
        cocok = [(n, c) for n, c in TOKO.items() if nama.lower() in n.lower()]
        if not cocok:
            raise SystemExit(
                f"Toko '{nama}' tidak ada. Pilihan: {', '.join(TOKO)}")
        return cocok[:1]
    aktif = [(n, c) for n, c in TOKO.items() if c.get("aktif")]
    if not aktif:
        raise SystemExit("Tidak ada toko yang dicentang. Buka aplikasinya"
                         " (Jalankan.bat) atau centang di toko.json.")
    return aktif


def toko_dari_argv(argv):
    """Baca argumen --toko "Nama". Kalau tidak ada, pakai semua yang aktif."""
    if "--toko" in argv:
        i = argv.index("--toko")
        if i + 1 < len(argv):
            return toko_aktif(argv[i + 1])
    return toko_aktif()

# ============================================================
# 2. PERIODE
# ============================================================
# Set manual: (tahun, bulan). Kalau None -> otomatis pakai bulan lalu (bulan penuh terakhir).
PERIODE_MANUAL = None  # contoh: (2026, 8)

NAMA_BULAN_ID = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                 "Juli", "Agustus", "September", "Oktober", "November", "Desember"]


def periode_aktif():
    """Kembalikan (tanggal_awal, tanggal_akhir, label) untuk 1 bulan penuh."""
    if PERIODE_MANUAL:
        th, bl = PERIODE_MANUAL
    else:
        hari_ini = date.today()
        bl = hari_ini.month - 1 or 12
        th = hari_ini.year if hari_ini.month > 1 else hari_ini.year - 1
    awal = date(th, bl, 1)
    akhir = date(th, bl, monthrange(th, bl)[1])
    return awal, akhir, f"{NAMA_BULAN_ID[bl]} {th}"


# ============================================================
# 3. TARGET PENGAMBILAN
# ============================================================
JUMLAH_PRODUK_TOP = 10       # top 10 produk
JUMLAH_CREATOR_PER_PRODUK = 50   # 50 creator per produk -> 500 baris

# ============================================================
# 4. CHROME / CDP
# ============================================================
CHROME_PATH_KANDIDAT = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
]
PORT_CDP = 9333

# Browser bekerja di latar belakang (headless) waktu menarik data, supaya
# tidak mengganggu orang yang sedang memakai komputernya.
# LOGIN SELALU DITAMPILKAN, apa pun nilai ini -- orangnya harus bisa mengetik.
#
# Menyembunyikannya dengan cara MEMINDAHKAN jendela ke luar layar TIDAK bisa:
# sudah diuji, Affiliate Center tidak menarik data sama sekali (0 produk
# setelah 35 detik) karena Chrome menahan halaman yang dianggap tak terlihat.
# Headless beda: halamannya tetap dirender, cuma tidak ditampilkan.
TAMPILKAN_BROWSER = False

# Peninggalan cara lama. Biarkan False -- lihat penjelasan di atas.
OFFSCREEN = False

# Taruh jendela di tengah layar waktu ditampilkan, supaya tidak muncul di
# pojok atau di luar jangkauan monitor.
JENDELA_TENGAH = True
# Posisi & ukuran jendela waktu OFFSCREEN = False.
# Chrome mengingat posisi jendela terakhir di dalam profil, jadi bekas run
# offscreen bikin jendela tetap tak kelihatan. Nilai ini dipakai untuk
# menariknya paksa kembali ke dalam layar.
JENDELA_POSISI = (0, 0)
JENDELA_UKURAN = (1280, 660)

URL_DASAR = "https://affiliate-id.tokopedia.com/data/product-performance"

# Dua endpoint yang benar-benar berisi data. Dikunci dari rekam_endpoint.py
# (lihat hasil/rekaman_endpoint.json), bukan tebakan lagi.
ENDPOINT_PRODUK = "product_analytics/product/list"
ENDPOINT_CREATOR = "product_analytics/creator/list"
POLA_API = [ENDPOINT_PRODUK, ENDPOINT_CREATOR]

# Bentuk response dua endpoint itu sama:
#   data.segments[]
#     .filter            -> {"product_id": ..., "seller_id": ...}
#     .time_descriptor   -> {"start": "2026-08-01T00:00:00", "end": "2026-09-01T00:00:00"}
#                           'end' EKSKLUSIF: Agustus = 08-01 s/d 09-01
#     .list_control.next_pagination -> {"has_more":, "next_page":, "total":, "total_page":}
#     .timed_lists[].stats[]        -> baris datanya
JALUR_SEGMEN = ("data", "segments")

# ============================================================
# 4b. SELEKTOR UI (dikunci dari hasil/rekaman_klik.json)
# ============================================================
# Design system halaman ini namanya "kora". Alur yang direkam:
#   input tanggal -> klik tanggal awal -> klik tanggal akhir
#   lalu per produk: "Lihat detailnya" -> Halaman 2..5 -> tombol "Produk"
#
# PENTING: daftar creator itu PAGINASI KLIK (10 baris/halaman), bukan
# infinite scroll. 50 creator = halaman 1 + klik halaman 2,3,4,5.
# Dicoba berurutan, yang pertama ketemu dipakai.
SEL_INPUT_TANGGAL = [
    ".kora-picker-range .kora-picker-input input",
    ".kora-picker .kora-picker-input input",
    ".kora-picker input",
]
SEL_TANGGAL_TERSEDIA = ".kora-picker-cell-in-view .kora-picker-date-value"
SEL_HALAMAN = ".kora-pagination-list li.kora-pagination-item"

# Popup pengumuman yang kadang muncul menutupi halaman. Selama modalnya
# terbuka, klik apa pun di belakangnya tidak tembus -- otomatisasi macet
# tanpa sebab yang kelihatan. Jadi ditutup dulu sebelum mulai.
SEL_WADAH_POPUP = ("[role=dialog], .kora-modal, .kora-modal-content,"
                   " .kora-dialog, .kora-drawer")
# Tombol penutupnya dicocokkan PERSIS (bukan "mengandung") dan hanya yang
# ada DI DALAM modal -- kalau tidak, tombol "Oke" lain di halaman ikut kena.
TEKS_TUTUP_POPUP = ["oke", "ok", "mengerti", "saya mengerti", "saya paham",
                    "lanjut", "lanjutkan", "tutup", "got it", "selesai"]
SEL_SILANG_POPUP = ("[aria-label*='close' i], [aria-label*='tutup' i],"
                    " .kora-modal-close, .kora-drawer-close")

# Tokopedia mengumumkan halaman ini akan dinonaktifkan dan diganti halaman
# "Performa". Kalau tulisan ini muncul, alatnya perlu direkam ulang sebelum
# halamannya benar-benar dimatikan.
TEKS_PERINGATAN_TUTUP = ["akan segera dinonaktifkan", "akan dinonaktifkan"]
TEKS_TOMBOL_DETAIL = "lihat detail"     # tombol di kolom kanan tiap baris produk
TEKS_TOMBOL_KEMBALI = "Produk"          # tombol kembali ke daftar produk

# Halaman ini menembak ratusan XHR ke domain TikTok (i18n, captcha, telemetry).
# Banyak di antaranya juga punya "/api/" dan isinya list berisi 'title'/'key',
# jadi heuristik pencari data salah tebak kalau tidak disaring dulu.
# Data yang kita mau selalu dari domain Affiliate Center sendiri.
HOST_API = ["affiliate-id.tokopedia.com"]
POLA_ABAIKAN = [
    "check_and_get_text", "starling", "abtest", "captcha", "verification",
    "feelgood", "ttwstatic", "byteoversea", "config_center", "/config?",
    "monitor", "slardar", "webid", "/log", "metric", "batch_",
]

# ============================================================
# 5. FOLDER
# ============================================================
# Semua lokasi dihitung di lokasi.py (portabel, tanpa path komputer tertentu).
BASE = L.BASE
DIR_HASIL = L.DIR_HASIL
DIR_MENTAH = L.DIR_MENTAH
DIR_LOG = L.DIR_LOG
DIR_SS = L.DIR_SS

# ============================================================
# 6. PEMETAAN KOLOM (isi setelah tahu nama field asli dari rekam_endpoint.py)
# ============================================================
# ---------- Sheet SIAP_PASTE: harus sama persis dengan header AFFILIATE 3 ----------
# (judul kolom, sumber, tipe)
#   sumber "@no"    -> nomor urut creator di dalam produk (1..50)
#   sumber "@kode"  -> kode produk, lihat KODE_PRODUK di bawah
#   sumber ""       -> sengaja dikosongkan (diisi tangan di sheet)
#   sumber "=xxx"   -> isi tetap "xxx"
#   selain itu      -> jalur field di JSON creator
#   tipe: teks | angka | rupiah
KOLOM_SIAP_PASTE = [
    ("No",                  "@no",                      "angka"),
    ("Produk Top 10",       "@kode",                    "teks"),
    ("Creator Name Top 50", "creator_meta.handle",      "teks"),
    ("FU",                  "",                         "teks"),
    ("SAMPLE",              "",                         "teks"),
    ("Creator Nickname",    "creator_meta.alias_name",  "teks"),
    ("GMV",                 "gmv.amount",               "rupiah"),
    ("Items sold",          "item_sold_cnt",            "angka"),
    ("Videos",              "video_cnt",                "angka"),
    ("LIVE streams",        "live_cnt",                 "angka"),
    ("Est. commission",     "est_commission.amount",    "rupiah"),
    ("Samples",             "sample_cnt",               "angka"),
    ("Refunded GMV",        "refund_gmv.amount",        "rupiah"),
    ("Refunded items sold", "refund_item_cnt",          "angka"),
    ("Est. flat fee",       "=--",                      "teks"),
    ("Note",                "",                         "teks"),
]

# Kolom uang ditulis sebagai ANGKA dengan format "Rp"#,##0 -- tampil
# "Rp267.603.178" tapi tetap bisa dijumlah di sheet tujuan.
# Kalau format itu tidak ikut terbawa waktu paste (di sheet cuma muncul
# "267603178"), set True: nilainya ditulis sebagai TEKS "Rp267.603.178" apa
# adanya. Konsekuensinya tidak bisa dijumlah lagi.
RUPIAH_SEBAGAI_TEKS = False

# Kode pendek untuk kolom "Produk Top 10", per product_id.
# Kalau product_id tidak terdaftar di sini, dipakai KATA TERAKHIR nama produk
# (huruf besar) -- itu cuma tebakan, jadi periksa daftar yang dicetak
# generate_excel.py dan betulkan yang salah di sini.
def muat_kode_produk():
    """Kode pendek "Produk Top 10" per product_id, dari kode_produk.json.

    Disimpan di berkas terpisah (bukan di kode) karena memang sering
    dibetulkan tangan: tebakan dari nama produk hampir selalu salah.
    Sesudah dibetulkan di Excel, simpan_kode.py menuliskannya ke sini
    supaya bulan depan tidak perlu dibetulkan lagi.
    """
    return _muat_json(L.BERKAS_KODE, {}).get("kode", {})


def simpan_kode_produk(kode):
    isi = _muat_json(L.BERKAS_KODE, {})
    isi["_catatan"] = ("Kode kolom 'Produk Top 10'. Betulkan lewat Excel"
                       " (kolom Kode kuning di sheet RINGKASAN) lalu jalankan"
                       " simpan_kode.py, atau ubah langsung di sini.")
    isi["kode"] = kode
    with open(L.BERKAS_KODE, "w", encoding="utf-8") as f:
        json.dump(isi, f, ensure_ascii=False, indent=1, sort_keys=True)


KODE_PRODUK = muat_kode_produk()

# ---------- Sheet per produk (01..10): lebih lengkap, termasuk ID ----------
# kiri = judul kolom di Excel, kanan = daftar jalur field di JSON creator.
# Jalur bersarang pakai titik. Jalur pertama yang ada isinya dipakai.
# Nama field di bawah sudah dipastikan dari rekaman, bukan tebakan.
PETA_KOLOM = {
    "Nama Creator": ["creator_meta.alias_name"],
    "Username":     ["creator_meta.handle"],
    "Creator ID":   ["creator_meta.id"],
    "Followers":    ["creator_meta.follower_cnt"],
    "GMV":          ["gmv.amount"],
    "Komisi":       ["est_commission.amount"],
    "Item Terjual": ["item_sold_cnt"],
    "Video":        ["video_cnt"],
    "LIVE":         ["live_cnt"],
    "Refund GMV":   ["refund_gmv.amount"],
    "Item Refund":  ["refund_item_cnt"],
    "Sampel":       ["sample_cnt"],
}
# Catatan: API TIDAK mengirim jumlah PESANAN (order count) per creator, yang ada
# cuma item_sold_cnt. Kalau sheet AFFILIATE 3 punya kolom "Pesanan", biarkan
# kosong atau pakai "Item Terjual" -- jangan disamakan diam-diam.

# Kolom ringkasan produk (dipakai sheet RINGKASAN).
PETA_KOLOM_PRODUK = {
    "Nama Produk":   ["product_meta.name"],
    "Product ID":    ["product_meta.id"],
    "GMV Produk":    ["gmv.amount"],
    "Komisi Produk": ["est_commission.amount"],
    "Item Terjual":  ["item_sold_cnt"],
    "Jumlah Creator": ["sales_creator_cnt"],
    "Video":         ["video_cnt"],
    "LIVE":          ["live_cnt"],
}
