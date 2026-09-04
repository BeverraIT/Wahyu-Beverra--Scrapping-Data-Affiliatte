# -*- coding: utf-8 -*-
"""
Ambil sesi login dari Chrome yang biasa dipakai, supaya tidak login dua kali.

Dipakai sekali di komputer yang Chrome-nya SUDAH login ke toko-toko itu.
Orang yang Chrome-nya belum login tidak butuh ini -- cukup klik "Login Toko".

  python impor_profil.py                      <- cari Chrome biasa otomatis
  python impor_profil.py --toko minzo         <- satu toko saja
  python impor_profil.py --dari "D:\\ChromeToko"  <- folder lain

CARA MENCOCOKKAN TOKO -> PROFIL CHROME
Satu Chrome bisa punya banyak profil (Default, Profile 1, ...), dan tidak ada
namanya yang menyebut toko. Menebak dari "profil mana yang cookie-nya paling
banyak" BERBAHAYA: bisa saja sesi toko lain yang terbawa, lalu data toko A
tersimpan dengan nama toko B tanpa ketahuan.

Jadi pencocokannya pakai bukti: profil dipilih hanya kalau riwayatnya
benar-benar pernah membuka URL dengan shop_id toko itu. Kalau tidak ada bukti,
toko itu DILEWATI dan disuruh login manual -- lebih baik login sekali lagi
daripada dapat data toko yang salah.

Chrome harus DITUTUP dulu: file cookie SQLite yang sedang dipakai tidak bisa
disalin utuh.
"""
import os
import shutil
import sqlite3
import sys
import tempfile

import konfigurasi as K
from mesin_cdp import chrome_pakai_profil, salin_profil

# Profil bawaan Chrome yang tidak pernah dipakai orang untuk login
BUKAN_PROFIL = {"System Profile", "Guest Profile"}


def akar_chrome():
    """Kandidat --user-data-dir Chrome yang biasa dipakai orang."""
    lokal = os.environ.get("LOCALAPPDATA") or ""
    programfiles = os.environ.get("PROGRAMFILES") or ""
    kandidat = [
        os.path.join(lokal, "Google", "Chrome", "User Data"),
        os.path.join(lokal, "Google", "Chrome Beta", "User Data"),
        os.path.join(lokal, "Chromium", "User Data"),
    ]
    if programfiles:
        kandidat.append(os.path.join(lokal, "Google", "Chrome SxS", "User Data"))
    return [p for p in kandidat if os.path.isdir(p)]


def profil_di(akar):
    """Nama profile-directory di dalam satu user-data-dir."""
    if not os.path.isdir(akar):
        return []
    keluar = []
    for nama in sorted(os.listdir(akar)):
        if nama in BUKAN_PROFIL:
            continue
        p = os.path.join(akar, nama)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "Preferences")):
            keluar.append(nama)
    return keluar


def _tanya_sqlite(berkas, sql, params=()):
    """Baca database Chrome lewat salinan -- aslinya bisa terkunci."""
    if not os.path.exists(berkas):
        return None
    tmp = tempfile.mkdtemp()
    try:
        salin = os.path.join(tmp, "db")
        shutil.copy2(berkas, salin)
        con = sqlite3.connect(salin)
        try:
            return con.execute(sql, params).fetchone()[0]
        finally:
            con.close()
    except Exception:
        return None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def bukti_toko(profil_dir, shop_id):
    """Berapa kali profil ini membuka halaman dengan shop_id toko tersebut.
    Ini bukti pencocokan, bukan tebakan."""
    if not shop_id:
        return 0
    return _tanya_sqlite(
        os.path.join(profil_dir, "History"),
        "SELECT count(*) FROM urls WHERE url LIKE ?",
        (f"%shop_id={shop_id}%",)) or 0


def cookie_terkunci(akar, prof):
    """True kalau cookie profil ini dikunci App-Bound Encryption (v20).

    Chrome sejak v127 mengenkripsi cookie dengan kunci yang terikat ke
    aplikasi (Local State -> os_crypt.app_bound_encrypted_key, nilai cookie
    berawalan 'v20'). Cookie begitu SENGAJA tidak bisa dibaca kalau filenya
    disalin ke folder lain -- itu memang tujuannya, mencegah pencurian sesi.

    Menyalinnya tetap "berhasil" tanpa error, tapi hasilnya profil yang
    kelihatan punya cookie padahal tidak bisa login. Jadi harus dideteksi
    di sini, sebelum menyalin, supaya tidak memberi harapan palsu.

    Cookie lama berawalan 'v10' masih bisa disalin (kunci DPAPI, terikat ke
    akun Windows, bukan ke aplikasi).
    """
    ck = os.path.join(akar, prof, "Network", "Cookies")
    if not os.path.exists(ck):
        return False
    tmp = tempfile.mkdtemp()
    try:
        salin = os.path.join(tmp, "c.db")
        shutil.copy2(ck, salin)
        con = sqlite3.connect(salin)
        try:
            for (v,) in con.execute(
                    "SELECT encrypted_value FROM cookies"
                    " WHERE host_key LIKE '%tokopedia%' LIMIT 50"):
                if bytes(v)[:3] == b"v20":
                    return True
        finally:
            con.close()
    except Exception:
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return False


def cookie_sesi(profil_dir):
    """Jumlah cookie sesi Tokopedia. Dipakai hanya untuk keterangan, BUKAN
    untuk memilih profil -- lihat catatan di atas."""
    return _tanya_sqlite(
        os.path.join(profil_dir, "Network", "Cookies"),
        "SELECT count(*) FROM cookies WHERE host_key LIKE '%seller-id%'"
        " OR host_key LIKE '%affiliate-id%'") or 0


def cari_profil(shop_id, akar_tambahan=None, slug=None):
    """Cari (akar, profil, bukti, cookie) yang terbukti pernah membuka toko ini.
    Kembalikan None kalau tidak ada buktinya."""
    akar_semua = list(akar_chrome())
    if akar_tambahan:
        akar_semua.insert(0, akar_tambahan)
        # dukung juga susunan lama: <akar>/<slug>_bot dan <akar>/<slug>
        if slug:
            for sub in (slug + "_bot", slug):
                p = os.path.join(akar_tambahan, sub)
                if os.path.isdir(p):
                    akar_semua.append(p)

    terbaik = None
    pernah_buka = False          # ada yang membuka toko ini, tapi tidak login
    terkunci = False             # ketemu, tapi cookienya v20 (tidak bisa disalin)
    for akar in akar_semua:
        for prof in profil_di(akar):
            pd = os.path.join(akar, prof)
            bukti = bukti_toko(pd, shop_id)
            if not bukti:
                continue
            pernah_buka = True
            # Bukti riwayat saja TIDAK cukup. Profil bisa pernah membuka
            # halamannya lalu logout / sesinya kedaluwarsa. Kalau tetap
            # disalin, hasilnya profil kosong yang kelihatan berhasil
            # padahal nanti tetap diminta login.
            ck = cookie_sesi(pd)
            if not ck:
                continue
            if cookie_terkunci(akar, prof):
                terkunci = True
                continue
            if terbaik is None or bukti > terbaik[2]:
                terbaik = (akar, prof, bukti, ck)
    if terbaik:
        return terbaik
    if terkunci:
        return "terkunci_chrome_baru"
    return "pernah_buka_tapi_logout" if pernah_buka else None


def chrome_masih_jalan():
    """Chrome apa pun yang sedang jalan bikin cookie-nya terkunci."""
    return chrome_pakai_profil("Chrome")


def impor(nama_toko, cfg, akar_tambahan=None, log=print):
    """Salin sesi login untuk satu toko. Kembalikan (berhasil, pesan)."""
    shop_id = cfg.get("shop_id")
    if not shop_id:
        return False, "shop_id belum diisi"

    temu = cari_profil(shop_id, akar_tambahan, cfg.get("slug"))
    if temu == "terkunci_chrome_baru":
        return False, ("Chrome versi baru mengunci cookienya (v20) - tidak bisa "
                       "dipindah, harus Login Toko sekali")
    if temu == "pernah_buka_tapi_logout":
        return False, "Chrome pernah buka toko ini tapi sesinya sudah habis"
    if not temu:
        return False, "tidak ada profil Chrome yang pernah membuka toko ini"

    akar, prof, bukti, ck = temu
    log(f"  sumber: {akar} [{prof}] ({bukti}x buka toko ini, {ck} cookie sesi)")
    try:
        salin_profil(akar, cfg["profil_chrome"], prof, bersih=True,
                     log=lambda t: log("  " + t), profil_dir_tujuan="Default")
    except Exception as e:
        return False, f"gagal menyalin: {e}"
    return True, f"sesi diambil dari profil Chrome \"{prof}\""


def main():
    akar_tambahan = None
    if "--dari" in sys.argv:
        akar_tambahan = sys.argv[sys.argv.index("--dari") + 1]
        if not os.path.isdir(akar_tambahan):
            print(f"[x] Folder tidak ada: {akar_tambahan}")
            return 1

    daftar = (K.toko_dari_argv(sys.argv) if "--toko" in sys.argv
              else list(K.TOKO.items()))

    print("Chrome yang ditemukan:")
    for a in ([akar_tambahan] if akar_tambahan else []) + akar_chrome():
        print(f"  {a}")
        for p in profil_di(a):
            print(f"      {p}")
    print()

    if chrome_masih_jalan():
        print("[x] Chrome masih jalan. TUTUP SEMUA jendela Chrome dulu,")
        print("[x] kalau tidak file cookie-nya terkunci dan salinannya rusak.")
        return 1

    berhasil, lewat = 0, []
    for nama, cfg in daftar:
        print(f"=== {nama}")
        ok, pesan = impor(nama, cfg, akar_tambahan)
        print(f"  {'[OK]' if ok else '[-]'} {pesan}\n")
        if ok:
            berhasil += 1
        else:
            lewat.append(nama)

    print("=" * 58)
    print(f"{berhasil} toko sesinya terambil, {len(lewat)} dilewati")
    if lewat:
        print("\nDilewati (login manual saja lewat tombol \"Login Toko\"):")
        for n in lewat:
            print(f"  - {n}")
    if berhasil:
        print("\nPastikan hasilnya benar:  python cek_toko.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
