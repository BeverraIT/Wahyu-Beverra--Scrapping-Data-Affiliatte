# -*- coding: utf-8 -*-
"""
LANGKAH 2 (otomatis penuh).

Alur:
  buka analitik produk -> set periode 1 bulan -> ambil top 10 produk
  -> buka detail tiap produk -> validasi periode -> panen daftar creator
  -> simpan JSON mentah per produk di hasil/mentah/

Catatan penting (pelajaran dari mesin Tarik Omset, jangan diulang):
  * tanggal WAJIB diklik dengan event mouse asli, bukan .click() JS
  * sukses = kalender menutup sendiri DAN nilai input cocok persis (bandingkan
    sebagai angka, bukan substring -- "Agt 15" pernah lolos karena mengandung "1")
  * halaman bisa mereset tanggal ke hari ini; setelah set tanggal langsung
    lanjut aksi berikutnya, jangan menyentuh UI lain
"""
import json
import os
import sys
import time
from datetime import date, timedelta

import konfigurasi as K
from mesin_cdp import Mesin

AWAL, AKHIR, LABEL = K.periode_aktif()

# Kalau otomatisasi mentok, skrip minta bantuan manual (set periode / buka
# detail produk) lalu lanjut sendiri. Matikan dengan --otomatis, mis. kalau
# menarik banyak toko sekaligus dan tidak mau ditungguin.
# GUI SELALU mematikannya -- tidak ada terminal untuk menjawab input().
INTERAKTIF = True

# GUI memasang fungsinya sendiri di sini supaya log muncul di jendela,
# bukan di terminal yang tidak dilihat siapa pun.
PENCATAT = None

# GUI memasang fungsi di sini untuk berhenti di tengah jalan.
BERHENTI = None


def pakai_periode(tahun, bulan):
    """Ganti periode saat program sudah jalan (dipakai GUI).
    AWAL/AKHIR sengaja variabel modul supaya semua fungsi di bawah ikut."""
    global AWAL, AKHIR, LABEL
    K.PERIODE_MANUAL = (tahun, bulan)
    AWAL, AKHIR, LABEL = K.periode_aktif()
    return AWAL, AKHIR, LABEL


def dibatalkan():
    return bool(BERHENTI and BERHENTI())


def catat(pesan):
    baris = f"[{time.strftime('%H:%M:%S')}] {pesan}"
    if PENCATAT:
        PENCATAT(baris)
    else:
        print(baris)
    try:
        with open(os.path.join(K.DIR_LOG, f"log_{time.strftime('%Y%m%d')}.txt"),
                  "a", encoding="utf-8") as f:
            f.write(baris + "\n")
    except Exception:
        pass


# ------------------------------------------------------------------
# Membongkar response Affiliate Center
# ------------------------------------------------------------------
def baca_segmen(body):
    """Bongkar bentuk baku response:
    data.segments[] -> {filter, time_descriptor, list_control, timed_lists[].stats[]}
    """
    try:
        data = json.loads(body)
    except Exception:
        return []
    keluar = []
    for seg in ((data.get("data") or {}).get("segments") or []):
        baris = []
        for tl in (seg.get("timed_lists") or []):
            baris.extend(tl.get("stats") or [])
        keluar.append({
            "filter": seg.get("filter") or {},
            "waktu": seg.get("time_descriptor") or {},
            "halaman": (seg.get("list_control") or {}).get("next_pagination") or {},
            "baris": baris,
        })
    return keluar


def rentang(waktu):
    """time_descriptor -> (tanggal_awal, tanggal_akhir_inklusif).
    'end' dari API bersifat EKSKLUSIF: Agustus dikirim sebagai 08-01 s/d 09-01."""
    try:
        a = date.fromisoformat(str(waktu["start"])[:10])
        b = date.fromisoformat(str(waktu["end"])[:10])
    except Exception:
        return None
    return a, b - timedelta(days=1)


def periode_segmen_cocok(seg):
    r = rentang(seg.get("waktu") or {})
    return bool(r) and r[0] == AWAL and r[1] == AKHIR


def periode_terbaca(m):
    """Periode yang sedang aktif menurut response terakhir, bukan tebakan
    dari teks halaman. Kembalikan (awal, akhir) atau None."""
    terakhir = None
    for r in m.panen_respon():
        for seg in baca_segmen(r["body"]):
            hasil = rentang(seg["waktu"])
            if hasil:
                terakhir = hasil
    return terakhir


def _cocok_sekarang(m):
    aktif = periode_terbaca(m)
    return bool(aktif) and aktif[0] == AWAL and aktif[1] == AKHIR, aktif


# Cari input tanggal dari beberapa kandidat selektor sekaligus.
JS_INPUT_TANGGAL = (
    "%s.map(s => document.querySelector(s)).find(e => e)"
    % json.dumps(K.SEL_INPUT_TANGGAL)
)


def klik_input_tanggal(m):
    if m.klik_dari_js(JS_INPUT_TANGGAL):
        return True
    ada = m.js(f"{json.dumps(K.SEL_INPUT_TANGGAL)}"
               ".map(s => s + '=' + document.querySelectorAll(s).length).join(', ')")
    catat(f"  ! input tanggal tidak ketemu ({ada})")
    return False


def _isi_tanggal_diketik(m):
    """Cara 1: ketik langsung di dua input rentang tanggal.
    Format yang dipakai halaman = ISO (nilai terekam: '2026-08-25')."""
    if not klik_input_tanggal(m):
        return False
    time.sleep(0.8)
    for tanggal in (AWAL, AKHIR):
        m.pilih_semua()
        m.ketik(f"{tanggal:%Y-%m-%d}")
        time.sleep(0.5)
        m.tekan("Enter")
        time.sleep(1.0)
    time.sleep(2.0)
    return True


def _isi_tanggal_diklik(m):
    """Cara 2: klik sel tanggal di kalender, persis seperti yang direkam.
    Sel yang dipakai hanya yang 'in-view' (bukan sisa bulan sebelah), dan
    dicocokkan sebagai ANGKA -- '31' pernah lolos lewat pencocokan teks."""
    if not klik_input_tanggal(m):
        return False
    time.sleep(1.0)
    for tanggal in (AWAL, AKHIR):
        ok = m.klik_dari_js(f"""
            [...document.querySelectorAll({json.dumps(K.SEL_TANGGAL_TERSEDIA)})]
              .find(e => parseInt(e.textContent.trim(), 10) === {tanggal.day})
        """)
        if not ok:
            return False
        time.sleep(1.2)
    time.sleep(2.0)
    return True


def set_periode(m, interaktif=True):
    """Set periode ke 1 bulan penuh. Sukses diukur dari time_descriptor
    response, bukan dari tampilan -- kalender kelihatan benar tapi nilainya
    tidak commit itu jebakan lama."""
    cocok, aktif = _cocok_sekarang(m)
    if cocok:
        catat(f"  periode aktif: {aktif[0]} s/d {aktif[1]} - cocok")
        return True

    catat(f"  periode aktif: {aktif[0]} s/d {aktif[1]}, mau: {AWAL} s/d {AKHIR}"
          if aktif else f"  periode belum terbaca, mau: {AWAL} s/d {AKHIR}")

    # Klik kalender duluan: cara ketik terbukti TIDAK pernah commit di UI ini
    # (nilai berubah di layar, tapi request-nya tetap pakai periode lama).
    # Ditahan sebagai cadangan kalau suatu saat kalendernya berubah.
    for nama, cara in (("klik kalender", _isi_tanggal_diklik), ("ketik", _isi_tanggal_diketik)):
        try:
            m.bersihkan_respon()
            if not cara(m):
                catat(f"  ! cara {nama}: elemennya tidak ketemu")
                continue
        except Exception as e:
            catat(f"  ! cara {nama} gagal: {type(e).__name__}: {e}")
            continue
        cocok, aktif = _cocok_sekarang(m)
        if cocok:
            catat(f"  periode diset lewat {nama}: {aktif[0]} s/d {aktif[1]}")
            return True
        catat(f"  ! cara {nama} belum commit"
              + (f" (terbaca {aktif[0]} s/d {aktif[1]})" if aktif else ""))

    m.tangkap_layar(f"periode_{AWAL:%Y%m}")
    if not interaktif:
        return False
    print()
    print(f"    >> Set periode manual di Chrome ke {AWAL} s/d {AKHIR} ({LABEL}).")
    input("    >> Tekan ENTER kalau sudah... ")
    cocok, aktif = _cocok_sekarang(m)
    if cocok:
        catat(f"  periode sekarang: {aktif[0]} s/d {aktif[1]} - cocok")
        return True
    catat("  ! periode masih belum cocok, data bisa salah periode")
    return False


# ------------------------------------------------------------------
# Pengambilan data
# ------------------------------------------------------------------
def teks(nilai, bawaan=""):
    """Ambil string dari nilai yang bentuknya tidak menentu.
    Sebagian endpoint mengembalikan dict/list (i18n, rich text), bukan string.
    Tanpa ini, nama[:45] di bawah meledak jadi KeyError: slice(None, 45, None)."""
    if isinstance(nilai, str):
        return nilai
    if isinstance(nilai, (int, float)):
        return str(nilai)
    if isinstance(nilai, dict):
        for k in ("value", "defaultValue", "text", "name", "title", "en"):
            if isinstance(nilai.get(k), str):
                return nilai[k]
    if isinstance(nilai, list) and nilai:
        return teks(nilai[0], bawaan)
    return bawaan


def jalur(baris, path, bawaan=None):
    """Ambil nilai lewat jalur bertitik: 'creator_meta.alias_name'."""
    cur = baris
    for bagian in path.split("."):
        if not isinstance(cur, dict):
            return bawaan
        cur = cur.get(bagian)
        if cur is None:
            return bawaan
    return cur


def id_creator(c):
    return teks(jalur(c, "creator_meta.id")) or teks(jalur(c, "creator_meta.handle"))


def panen(m, endpoint, hanya_periode=True):
    """Kumpulkan baris dari satu endpoint, buang duplikat, urut sesuai datang.
    Response periode lain (mis. bawaan 7 hari) dibuang supaya tidak tercampur."""
    baris, halaman, lihat = [], {}, set()
    for r in m.panen_respon(pola=[endpoint]):
        for seg in baca_segmen(r["body"]):
            if hanya_periode and not periode_segmen_cocok(seg):
                continue
            halaman = seg["halaman"] or halaman
            pid_seg = teks(seg["filter"].get("product_id"))
            for b in seg["baris"]:
                kunci = json.dumps(b, sort_keys=True)[:200]
                if kunci in lihat:
                    continue
                lihat.add(kunci)
                if pid_seg:
                    # dari filter segmen, bukan dari baris -- dipakai menyaring
                    # kalau response beberapa produk tercampur
                    b = dict(b, _product_id=pid_seg)
                baris.append(b)
    return baris, halaman


JS_TOMBOL_DETAIL = (
    "[...document.querySelectorAll('button')].filter(b => (b.innerText || '')"
    ".toLowerCase().includes(%s))" % json.dumps(K.TEKS_TOMBOL_DETAIL)
)


def tunggu_tabel_produk(m, minimal=1, batas=20):
    """Tunggu tabel produk selesai render: tombol 'Lihat detailnya' baris
    ke-`minimal` harus sudah ada sebelum diklik."""
    tenggat = time.time() + batas
    while time.time() < tenggat:
        jml = m.js(f"{JS_TOMBOL_DETAIL}.length") or 0
        if jml >= minimal:
            return jml
        time.sleep(0.6)
    return 0


def buka_detail_produk(m, nomor):
    """Klik tombol 'Lihat detailnya' di baris ke-nomor (1-based)."""
    return m.klik_dari_js(f"{JS_TOMBOL_DETAIL}[{nomor - 1}]")


def kembali_ke_produk(m):
    """Klik tombol 'Produk' di header untuk balik ke daftar produk."""
    return m.klik_dari_js(f"""
        [...document.querySelectorAll('button')]
          .find(b => (b.innerText || '').trim() === {json.dumps(K.TEKS_TOMBOL_KEMBALI)})
    """)


def klik_halaman(m, nomor):
    """Klik nomor halaman di paginasi tabel creator."""
    return m.klik_dari_js(f"""
        [...document.querySelectorAll({json.dumps(K.SEL_HALAMAN)})]
          .find(li => parseInt((li.textContent || '').trim(), 10) === {nomor})
    """)


def tunggu_baris(m, endpoint, minimal=1, batas=25, hanya_periode=True):
    """Tunggu sampai jumlah baris mencapai `minimal`, bukan tidur sekian detik.

    Halaman ini SPA: tabelnya masih berputar memuat beberapa detik setelah
    diklik. Panen terlalu cepat = nol baris padahal halamannya benar."""
    tenggat = time.time() + batas
    baris, halaman = panen(m, endpoint, hanya_periode)
    while len(baris) < minimal and time.time() < tenggat:
        time.sleep(0.7)
        baris, halaman = panen(m, endpoint, hanya_periode)
    return baris, halaman


def kumpulkan_creator(m, product_id, batas=None):
    """Halaman 1 termuat sendiri waktu detail dibuka; sisanya diklik per halaman.
    Daftar creator ini paginasi (10 baris/halaman), bukan infinite scroll."""
    batas = batas or K.JUMLAH_CREATOR_PER_PRODUK
    baris, halaman = tunggu_baris(m, K.ENDPOINT_CREATOR, 1, batas=25)
    if not baris:
        return []

    nomor = 2
    while len(baris) < batas and nomor <= 30:
        if halaman and not halaman.get("has_more", True):
            break
        sebelum = len(baris)
        if not klik_halaman(m, nomor):
            break
        baris, halaman = tunggu_baris(m, K.ENDPOINT_CREATOR, sebelum + 1, batas=12)
        if len(baris) == sebelum:
            # klik kadang termakan waktu tabel masih memuat -- coba sekali lagi
            if not klik_halaman(m, nomor):
                break
            baris, halaman = tunggu_baris(m, K.ENDPOINT_CREATOR, sebelum + 1, batas=12)
            if len(baris) == sebelum:
                catat(f"      ! halaman {nomor} tidak menambah data, berhenti")
                break
        nomor += 1

    # response beberapa produk bisa tercampur kalau tab belum sempat bersih
    if product_id:
        cocok = [b for b in baris
                 if not b.get("_product_id") or b["_product_id"] == product_id]
        baris = cocok or baris

    lihat, unik = set(), []
    for c in baris:
        kunci = id_creator(c) or json.dumps(c, sort_keys=True)[:120]
        if kunci in lihat:
            continue
        lihat.add(kunci)
        unik.append(c)
    return unik[:batas]


def jalankan_toko(nama_toko, cfg):
    catat(f"=== {nama_toko} | periode {LABEL} ({AWAL} s/d {AKHIR}) ===")
    m = Mesin(cfg["profil_chrome"], log=catat,
              port=cfg.get("port_cdp"),
              profil_dir=cfg.get("profil_dir")).buka()
    hasil_toko = {"toko": nama_toko, "periode": LABEL,
                  "awal": str(AWAL), "akhir": str(AKHIR), "produk": []}
    try:
        url = f"{K.URL_DASAR}?shop_region=ID&shop_id={cfg['shop_id']}&platform_data_source=shop"
        m.bersihkan_respon()
        m.buka_url(url, tunggu=6)

        # Tunggu SPA-nya benar-benar menarik data. Periodenya masih bawaan
        # (7 hari), jadi saringan periode dimatikan dulu di sini. Tanpa ini,
        # set_periode jalan sebelum kalendernya sempat render.
        awal_ada, _ = tunggu_baris(m, K.ENDPOINT_PRODUK, 1, batas=60, hanya_periode=False)
        if not awal_ada:
            catat("  ! halaman tidak menarik data produk sama sekali dalam 60 detik")
            m.tangkap_layar("halaman_kosong")

        set_periode(m, interaktif=INTERAKTIF)

        # --- daftar produk (sudah terurut GMV menurun dari server) ---
        semua_produk, hal_produk = tunggu_baris(m, K.ENDPOINT_PRODUK, 1, batas=20)
        produk = semua_produk[:K.JUMLAH_PRODUK_TOP]
        total = hal_produk.get("total")
        catat(f"  produk terdeteksi: {len(produk)}"
              + (f" (dari {total} produk periode ini)" if total else ""))
        if not produk:
            catat("  ! Tidak ada response product/list untuk periode ini.")
            catat("  ! Pastikan periodenya sudah diset ke 1 bulan penuh di halaman.")
            return None

        for i, p in enumerate(produk, 1):
            if dibatalkan():
                catat("  ! dihentikan, hasil sejauh ini tetap disimpan")
                break
            pid = teks(jalur(p, "product_meta.id"))
            nama = teks(jalur(p, "product_meta.name")) or f"Produk {i}"
            catat(f"  [{i}/{len(produk)}] {nama[:45]} ({pid})")
            if not pid:
                catat("      ! product_meta.id kosong, dilewati")
                continue

            m.bersihkan_respon()
            if not tunggu_tabel_produk(m, i):
                catat(f"      ! tabel produk belum siap (butuh {i} baris)")
            if not buka_detail_produk(m, i):
                catat("      ! tombol 'Lihat detailnya' baris ini tidak ketemu")
                m.tangkap_layar(f"detail_{i:02d}")
                if not INTERAKTIF:
                    continue
                print()
                print(f"    >> Buka detail produk ini di Chrome: {nama[:60]}")
                input("    >> Tekan ENTER kalau sudah... ")
            time.sleep(1.0)

            creator = kumpulkan_creator(m, pid)
            catat(f"      creator terambil: {len(creator)}")
            if not creator:
                m.tangkap_layar(f"creator_kosong_{i:02d}")
            hasil_toko["produk"].append({
                "peringkat": i, "product_id": pid, "nama_produk": nama,
                "ringkasan_produk": p, "creator": creator,
            })

            if i < len(produk):
                if not kembali_ke_produk(m):
                    catat("      ! tombol kembali 'Produk' tidak ketemu")
                    m.tangkap_layar(f"kembali_{i:02d}")
                time.sleep(2.5)

        berkas = os.path.join(
            K.DIR_MENTAH,
            f"{nama_toko.replace(' ', '_')}_{AWAL:%Y-%m}.json")
        baru = sum(len(p["creator"]) for p in hasil_toko["produk"])

        # Jangan menimpa hasil yang lebih lengkap. Run yang setengah jadi
        # pernah menghapus data 500 baris tanpa peringatan.
        if os.path.exists(berkas):
            try:
                with open(berkas, encoding="utf-8") as f:
                    lama = sum(len(p.get("creator") or [])
                               for p in json.load(f).get("produk") or [])
            except Exception:
                lama = 0
            if lama > baru:
                berkas = berkas.replace(".json", "_parsial.json")
                catat(f"  ! hasil run ini ({baru} baris) lebih sedikit dari yang"
                      f" sudah ada ({lama} baris)")
                catat(f"  ! yang lama TIDAK ditimpa, run ini disimpan terpisah")

        with open(berkas, "w", encoding="utf-8") as f:
            json.dump(hasil_toko, f, ensure_ascii=False, indent=1)
        catat(f"[OK] mentah tersimpan ({baru} baris): {berkas}")
        return berkas
    finally:
        m.tutup()


def main():
    global INTERAKTIF
    if "--otomatis" in sys.argv:
        INTERAKTIF = False
    daftar = K.toko_dari_argv(sys.argv)
    catat(f"=== {len(daftar)} toko, periode {LABEL} ===")
    berkas = []
    for nama, cfg in daftar:
        if dibatalkan():
            catat("Dihentikan sebelum toko berikutnya.")
            break
        try:
            b = jalankan_toko(nama, cfg)
            if b:
                berkas.append(b)
        except Exception as e:
            catat(f"[X] {nama} gagal: {type(e).__name__}: {e}")
    if berkas:
        catat("Lanjut: python generate_excel.py")
    else:
        catat("Tidak ada data tersimpan. Selesaikan langkah 1 dulu:"
              " python rekam_endpoint.py")


if __name__ == "__main__":
    main()
