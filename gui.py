# -*- coding: utf-8 -*-
"""
Tarik Creator Affiliate -- tampilan aplikasi.

Pakai tkinter (sudah bawaan Python, tidak perlu install apa-apa lagi).

Aturan penting di dalam sini:
  * Semua kerja berat jalan di THREAD terpisah. Kalau dijalankan langsung,
    jendelanya membeku dan orang mengira aplikasinya hang.
  * Thread TIDAK BOLEH menyentuh widget tkinter. Semua kabar dari thread
    dikirim lewat antrean, lalu jendela membacanya tiap 100 ms.
"""
import os
import queue
import subprocess
import sys
import threading
import traceback
from datetime import date

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

import konfigurasi as K
import lokasi as L
import akun

JUDUL = "Tarik Creator Affiliate"

WARNA_STATUS = {
    akun.SIAP: "#1E7145",
    akun.BELUM_LOGIN: "#C00000",
    akun.BELUM_ADA: "#8A6D00",
    akun.LAMBAT: "#8A6D00",
    akun.GAGAL: "#C00000",
}


class Aplikasi(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(JUDUL)
        self.geometry("960x660")
        self.minsize(820, 560)

        self.antrean = queue.Queue()
        self.kerja = None              # thread yang sedang jalan
        self.minta_berhenti = threading.Event()
        self.baris_toko = {}           # nama -> dict widget

        self._bangun_tampilan()
        K.TAMPILKAN_BROWSER = self.var_tampil.get()
        self._muat_daftar_toko()
        self.after(100, self._baca_antrean)
        self.protocol("WM_DELETE_WINDOW", self._tutup)

    # ---------------------------------------------------------------
    # Tampilan
    # ---------------------------------------------------------------
    def _bangun_tampilan(self):
        atas = ttk.Frame(self, padding=(12, 10))
        atas.pack(fill="x")

        ttk.Label(atas, text=JUDUL, font=("Segoe UI", 15, "bold")).pack(side="left")
        self.lbl_status = ttk.Label(atas, text="siap", foreground="#666")
        self.lbl_status.pack(side="right")

        # --- periode ---
        per = ttk.LabelFrame(self, text="Periode", padding=(12, 8))
        per.pack(fill="x", padx=12, pady=(0, 8))

        hari_ini = date.today()
        bl = hari_ini.month - 1 or 12
        th = hari_ini.year if hari_ini.month > 1 else hari_ini.year - 1

        self.var_bulan = tk.StringVar(value=K.NAMA_BULAN_ID[bl])
        self.var_tahun = tk.StringVar(value=str(th))
        ttk.Label(per, text="Bulan").pack(side="left")
        ttk.Combobox(per, textvariable=self.var_bulan, width=12, state="readonly",
                     values=K.NAMA_BULAN_ID[1:]).pack(side="left", padx=(6, 14))
        ttk.Label(per, text="Tahun").pack(side="left")
        ttk.Combobox(per, textvariable=self.var_tahun, width=7, state="readonly",
                     values=[str(y) for y in range(hari_ini.year - 3,
                                                   hari_ini.year + 1)]
                     ).pack(side="left", padx=6)
        ttk.Label(per, text="(bawaan: bulan penuh terakhir)",
                  foreground="#666").pack(side="left", padx=10)

        self.var_tampil = tk.BooleanVar(
            value=K.muat_setelan().get("tampilkan_browser", False))
        ttk.Checkbutton(per, text="Tampilkan browser saat menarik data",
                        variable=self.var_tampil,
                        command=self._simpan_tampil).pack(side="right")

        # --- daftar toko ---
        bingkai = ttk.LabelFrame(self, text="Toko", padding=(10, 6))
        bingkai.pack(fill="both", expand=False, padx=12, pady=(0, 8))

        kepala = ttk.Frame(bingkai)
        kepala.pack(fill="x")
        ttk.Button(kepala, text="Centang semua",
                   command=lambda: self._centang_semua(True)).pack(side="left")
        ttk.Button(kepala, text="Kosongkan",
                   command=lambda: self._centang_semua(False)).pack(side="left", padx=6)
        ttk.Button(kepala, text="Tambah Toko",
                   command=self._tambah_toko).pack(side="left", padx=6)
        ttk.Button(kepala, text="Cek Semua",
                   command=self._cek_toko).pack(side="left", padx=6)
        ttk.Button(kepala, text="Ambil Login dari Chrome",
                   command=self._impor_chrome).pack(side="left", padx=6)

        self.kotak_toko = ttk.Frame(bingkai)
        self.kotak_toko.pack(fill="x", pady=(8, 2))

        # --- tombol aksi ---
        aksi = ttk.Frame(self, padding=(12, 0))
        aksi.pack(fill="x")
        self.tb_tarik = ttk.Button(aksi, text="Tarik Data + Buat Excel",
                                   command=self._tarik)
        self.tb_tarik.pack(side="left")
        self.tb_excel = ttk.Button(aksi, text="Buat Excel saja",
                                   command=self._excel)
        self.tb_excel.pack(side="left", padx=6)
        self.tb_stop = ttk.Button(aksi, text="Hentikan", state="disabled",
                                  command=self._hentikan)
        self.tb_stop.pack(side="left", padx=6)
        ttk.Button(aksi, text="Buka Folder Hasil",
                   command=self._buka_hasil).pack(side="right")

        self.progres = ttk.Progressbar(self, mode="determinate")
        self.progres.pack(fill="x", padx=12, pady=(8, 4))

        # --- log ---
        kotak_log = ttk.LabelFrame(self, text="Catatan", padding=(6, 4))
        kotak_log.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.log = tk.Text(kotak_log, height=12, wrap="none",
                           font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4",
                           insertbackground="#d4d4d4")
        gulir = ttk.Scrollbar(kotak_log, command=self.log.yview)
        self.log.configure(yscrollcommand=gulir.set)
        gulir.pack(side="right", fill="y")
        self.log.pack(fill="both", expand=True)
        self.log.tag_config("galat", foreground="#f48771")
        self.log.tag_config("bagus", foreground="#89d185")

    def _muat_daftar_toko(self):
        for w in self.kotak_toko.winfo_children():
            w.destroy()
        self.baris_toko.clear()
        K.TOKO = K.muat_toko()

        if not K.TOKO:
            ttk.Label(self.kotak_toko,
                      text='Belum ada toko. Klik "Tambah Toko".',
                      foreground="#8A6D00").pack(anchor="w")
            return

        for nama, cfg in K.TOKO.items():
            baris = ttk.Frame(self.kotak_toko)
            baris.pack(fill="x", pady=1)

            var = tk.BooleanVar(value=cfg.get("aktif", True))
            ttk.Checkbutton(baris, variable=var, command=self._simpan_centang
                            ).pack(side="left")
            ttk.Label(baris, text=nama, width=22).pack(side="left")

            # Adanya folder profil BUKAN berarti sesinya masih hidup -- itu
            # baru ketahuan setelah tombol Cek. Jangan tulis "sudah login"
            # di sini, nanti orang percaya padahal sesinya sudah habis.
            ada = akun.sudah_ada_profil(cfg)
            lbl = ttk.Label(baris, width=38,
                            text="sudah pernah login" if ada else "belum login",
                            foreground="#666" if ada else WARNA_STATUS[akun.BELUM_ADA])
            lbl.pack(side="left")

            ttk.Button(baris, text="Login Toko", width=12,
                       command=lambda n=nama: self._login(n)).pack(side="left", padx=3)
            ttk.Button(baris, text="Cek", width=6,
                       command=lambda n=nama: self._cek_toko(n)).pack(side="left")

            self.baris_toko[nama] = {"var": var, "label": lbl}

    # ---------------------------------------------------------------
    # Bantuan tampilan
    # ---------------------------------------------------------------
    def _centang_semua(self, nyala):
        for b in self.baris_toko.values():
            b["var"].set(nyala)
        self._simpan_centang()

    def _simpan_centang(self):
        setelan = K.muat_setelan()
        setelan["toko_aktif"] = [n for n, b in self.baris_toko.items()
                                 if b["var"].get()]
        K.simpan_setelan(setelan)
        for n, b in self.baris_toko.items():
            if n in K.TOKO:
                K.TOKO[n]["aktif"] = b["var"].get()

    def _simpan_tampil(self):
        """Browser di latar belakang atau kelihatan waktu menarik data.
        Tidak berpengaruh ke Login Toko -- itu selalu ditampilkan."""
        setelan = K.muat_setelan()
        setelan["tampilkan_browser"] = self.var_tampil.get()
        K.simpan_setelan(setelan)
        K.TAMPILKAN_BROWSER = self.var_tampil.get()
        self._tulis("Browser saat menarik data: "
                    + ("ditampilkan" if self.var_tampil.get()
                       else "latar belakang"))

    def _dipilih(self):
        return [(n, K.TOKO[n]) for n, b in self.baris_toko.items()
                if b["var"].get() and n in K.TOKO]

    def _periode(self):
        bulan = K.NAMA_BULAN_ID.index(self.var_bulan.get())
        return int(self.var_tahun.get()), bulan

    def _buka_hasil(self):
        try:
            os.startfile(L.DIR_HASIL)                      # noqa: S606 (Windows)
        except Exception:
            subprocess.Popen(["explorer", L.DIR_HASIL])

    def _tutup(self):
        if self.kerja and self.kerja.is_alive():
            if not messagebox.askyesno(
                    JUDUL, "Masih ada pekerjaan berjalan. Tutup saja?"):
                return
            self.minta_berhenti.set()
        self.destroy()

    # ---------------------------------------------------------------
    # Jembatan thread -> jendela
    # ---------------------------------------------------------------
    def _kirim(self, jenis, **isi):
        self.antrean.put({"jenis": jenis, **isi})

    def _baca_antrean(self):
        try:
            while True:
                p = self.antrean.get_nowait()
                j = p["jenis"]
                if j == "log":
                    self._tulis(p["teks"], p.get("tag"))
                elif j == "status":
                    self.lbl_status.config(text=p["teks"])
                elif j == "progres":
                    self.progres.config(maximum=p.get("maks", 100),
                                        value=p.get("nilai", 0))
                elif j == "status_toko":
                    b = self.baris_toko.get(p["toko"])
                    if b:
                        b["label"].config(
                            text=p["teks"],
                            foreground=WARNA_STATUS.get(p.get("kode"), "#666"))
                elif j == "selesai":
                    self._selesai(p.get("pesan", ""))
                elif j == "muat_ulang":
                    self._muat_daftar_toko()
        except queue.Empty:
            pass
        self.after(100, self._baca_antrean)

    def _tulis(self, teks, tag=None):
        self.log.insert("end", teks + "\n", tag or ())
        self.log.see("end")

    def _mulai(self, nama_kerja, fungsi):
        if self.kerja and self.kerja.is_alive():
            messagebox.showinfo(JUDUL, "Masih ada pekerjaan yang berjalan.")
            return
        self.minta_berhenti.clear()
        self.tb_tarik.config(state="disabled")
        self.tb_excel.config(state="disabled")
        self.tb_stop.config(state="normal")
        self.lbl_status.config(text=nama_kerja + "...")

        def bungkus():
            try:
                fungsi()
            except Exception:
                self._kirim("log", teks=traceback.format_exc(), tag="galat")
                self._kirim("selesai", pesan=nama_kerja + " gagal")
            else:
                self._kirim("selesai", pesan=nama_kerja + " selesai")

        self.kerja = threading.Thread(target=bungkus, daemon=True)
        self.kerja.start()

    def _selesai(self, pesan):
        self.tb_tarik.config(state="normal")
        self.tb_excel.config(state="normal")
        self.tb_stop.config(state="disabled")
        self.lbl_status.config(text=pesan or "siap")
        self.progres.config(value=0)

    def _hentikan(self):
        self.minta_berhenti.set()
        self._tulis("Diminta berhenti, menunggu langkah sekarang selesai...", "galat")

    # ---------------------------------------------------------------
    # Aksi
    # ---------------------------------------------------------------
    def _login(self, nama):
        cfg = K.TOKO.get(nama)
        if not cfg:
            return
        catat = lambda t: self._kirim("log", teks=t)                  # noqa: E731

        def kerja():
            self._kirim("status_toko", toko=nama, teks="membuka Chrome...",
                        kode=akun.LAMBAT)
            ok, pesan = akun.login(nama, cfg, log=catat,
                                   berhenti=self.minta_berhenti.is_set)
            self._kirim("status_toko", toko=nama,
                        teks="sudah login" if ok else pesan.splitlines()[0][:38],
                        kode=akun.SIAP if ok else akun.BELUM_LOGIN)
            self._kirim("log", teks=f"[{nama}] {pesan}",
                        tag="bagus" if ok else "galat")

        self._mulai(f"Login {nama}", kerja)

    def _impor_chrome(self):
        """Ambil sesi login dari Chrome yang biasa dipakai orang ini."""
        import impor_profil as I

        daftar = self._dipilih()
        if not daftar:
            messagebox.showinfo(JUDUL, "Centang dulu toko yang mau diambil sesinya.")
            return
        if I.chrome_masih_jalan():
            messagebox.showwarning(
                JUDUL,
                "Tutup SEMUA jendela Google Chrome dulu.\n\n"
                "Selama Chrome jalan, file cookie-nya terkunci dan sesinya\n"
                "tersalin setengah jadi — kelihatan berhasil tapi nanti\n"
                "tetap diminta login.")
            return
        if not messagebox.askyesno(
                JUDUL,
                "Ambil sesi login dari Chrome yang biasa kamu pakai?\n\n"
                "CATATAN: Chrome versi baru mengunci cookienya supaya tidak\n"
                "bisa dipindah — itu pengaman anti-pencurian sesi. Kalau\n"
                "Chrome-mu termasuk yang baru, tokonya akan dilewati dan tetap\n"
                "harus Login Toko sekali. Itu wajar, bukan error.\n\n"
                "Pastikan semua jendela Chrome sudah ditutup."):
            return

        def catat(teks, tag=None):
            self._kirim("log", teks=teks, tag=tag)

        def kerja():
            self._kirim("progres", maks=len(daftar), nilai=0)
            berhasil, lewat = 0, []
            for i, (n, cfg) in enumerate(daftar, 1):
                if self.minta_berhenti.is_set():
                    break
                self._kirim("status", teks=f"ambil sesi {n} ({i}/{len(daftar)})")
                self._kirim("status_toko", toko=n, teks="mengambil sesi...",
                            kode=akun.LAMBAT)
                catat(f"=== {n}")
                ok, pesan = I.impor(n, cfg, log=catat)
                catat(f"  {'[OK]' if ok else '[-]'} {pesan}")
                self._kirim("status_toko", toko=n,
                            teks="sesi diambil, klik Cek" if ok else pesan,
                            kode=akun.SIAP if ok else akun.BELUM_ADA)
                if ok:
                    berhasil += 1
                else:
                    lewat.append(n)
                self._kirim("progres", maks=len(daftar), nilai=i)

            catat(f"Selesai: {berhasil} toko sesinya terambil, "
                  f"{len(lewat)} dilewati")
            if lewat:
                catat("Yang dilewati harus login manual lewat tombol "
                      '"Login Toko": ' + ", ".join(lewat), "galat")
            if berhasil:
                catat('Klik "Cek Semua" untuk memastikan sesinya benar-benar '
                      "hidup.", "bagus")

        self._mulai("Ambil sesi dari Chrome", kerja)

    def _cek_toko(self, nama=None):
        daftar = [(nama, K.TOKO[nama])] if nama else self._dipilih()
        if not daftar:
            messagebox.showinfo(JUDUL, "Centang dulu toko yang mau dicek.")
            return
        catat = lambda t: self._kirim("log", teks=t)                  # noqa: E731

        def kerja():
            self._kirim("progres", maks=len(daftar), nilai=0)
            for i, (n, cfg) in enumerate(daftar, 1):
                if self.minta_berhenti.is_set():
                    break
                self._kirim("status", teks=f"cek {n} ({i}/{len(daftar)})")
                self._kirim("status_toko", toko=n, teks="mengecek...",
                            kode=akun.LAMBAT)
                h = akun.cek(n, cfg, log=catat)
                self._kirim("status_toko", toko=n,
                            teks=f"{h['status']} - {h['pesan']}".splitlines()[0][:38],
                            kode=h["status"])
                self._kirim("log", teks=f"[{n}] {h['status']}: {h['pesan']}",
                            tag="bagus" if h["status"] == akun.SIAP else "galat")
                self._kirim("progres", maks=len(daftar), nilai=i)

        self._mulai("Cek toko", kerja)

    def _tarik(self):
        daftar = self._dipilih()
        if not daftar:
            messagebox.showinfo(JUDUL, "Centang dulu toko yang mau ditarik.")
            return
        belum = [n for n, c in daftar if not akun.sudah_ada_profil(c)]
        if belum:
            messagebox.showwarning(
                JUDUL, "Toko ini belum login:\n\n  " + "\n  ".join(belum) +
                '\n\nKlik "Login Toko" dulu di baris tokonya.')
            return
        tahun, bulan = self._periode()

        def kerja():
            import tarik_creator as T
            import generate_excel as G

            T.PENCATAT = lambda t: self._kirim("log", teks=t)
            T.BERHENTI = self.minta_berhenti.is_set
            T.INTERAKTIF = False        # tidak ada terminal untuk input()
            awal, akhir, label = T.pakai_periode(tahun, bulan)
            self._kirim("log", teks=f"=== Periode {label} ({awal} s/d {akhir}) ===")
            self._kirim("progres", maks=len(daftar), nilai=0)

            sukses = 0
            for i, (n, cfg) in enumerate(daftar, 1):
                if self.minta_berhenti.is_set():
                    break
                self._kirim("status", teks=f"tarik {n} ({i}/{len(daftar)})")
                self._kirim("status_toko", toko=n, teks="menarik data...",
                            kode=akun.LAMBAT)
                try:
                    berkas = T.jalankan_toko(n, cfg)
                    ok = bool(berkas)
                except Exception as e:
                    self._kirim("log", teks=f"[{n}] gagal: {type(e).__name__}: {e}",
                                tag="galat")
                    ok = False
                sukses += 1 if ok else 0
                self._kirim("status_toko", toko=n,
                            teks="data tersimpan" if ok else "gagal menarik",
                            kode=akun.SIAP if ok else akun.GAGAL)
                self._kirim("progres", maks=len(daftar), nilai=i)

            if sukses:
                self._kirim("status", teks="membuat Excel...")
                self._buat_excel(G)
            else:
                self._kirim("log", teks="Tidak ada data baru, Excel dilewati.",
                            tag="galat")

        self._mulai("Tarik data", kerja)

    def _excel(self):
        def kerja():
            import generate_excel as G
            self._buat_excel(G)

        self._mulai("Buat Excel", kerja)

    def _buat_excel(self, G):
        """Dipanggil dari dalam thread kerja."""
        import glob
        berkas = sorted(glob.glob(os.path.join(L.DIR_MENTAH, "*.json")))
        if not berkas:
            self._kirim("log", teks="Belum ada data mentah. Tarik data dulu.",
                        tag="galat")
            return
        for b in berkas:
            keluar, jumlah, tebakan = G.bangun(b)
            self._kirim("log", teks=f"[OK] {os.path.basename(keluar)} - {jumlah} baris",
                        tag="bagus")
            if tebakan:
                self._kirim("log", tag="galat", teks=(
                    f"  ! {len(tebakan)} kode 'Produk Top 10' masih tebakan"
                    " (diambil dari kata terakhir nama produk):"))
                for pk, pid, kode in tebakan:
                    self._kirim("log", teks=f"      produk #{pk}: {kode}")
                self._kirim("log", teks=(
                    "  ! Betulkan di Excel: sheet RINGKASAN, kolom Kode"
                    " (kuning). SIAP_PASTE ikut berubah sendiri."))

    def _tambah_toko(self):
        nama = simpledialog.askstring(JUDUL, "Nama toko:", parent=self)
        if not nama:
            return
        nama = nama.strip()
        if nama in K.TOKO:
            messagebox.showerror(JUDUL, f"Toko '{nama}' sudah ada.")
            return
        shop_id = simpledialog.askstring(
            JUDUL,
            "shop_id toko ini.\n\n"
            "Ambil dari URL Affiliate Center, bagian shop_id=...\n"
            "Contoh: ...?shop_region=ID&shop_id=7494510375204653632",
            parent=self)
        if not shop_id or not shop_id.strip().isdigit():
            messagebox.showerror(JUDUL, "shop_id harus berupa angka.")
            return

        slug = "".join(c for c in nama.lower() if c.isalnum()) or f"toko{len(K.TOKO)+1}"
        asli, n = slug, 2
        sudah = {c["slug"] for c in K.TOKO.values()}
        while slug in sudah:
            slug, n = f"{asli}{n}", n + 1
        port = max([c["port_cdp"] for c in K.TOKO.values()] or [9330]) + 1

        K.TOKO[nama] = {
            "slug": slug, "shop_id": shop_id.strip(),
            "profil_chrome": L.profil_toko(slug), "profil_dir": "Default",
            "port_cdp": port, "aktif": True,
            "profil_sumber": "", "profil_dir_sumber": "Default",
        }
        K.tambah_toko_lokal(nama, K.TOKO[nama])
        self._muat_daftar_toko()
        self._tulis(f"Toko '{nama}' ditambahkan (port {port}). "
                    f'Klik "Login Toko" di barisnya.', "bagus")
        self._tulis("Toko ini tersimpan di komputer ini saja. Supaya dipakai "
                    "sekantor, minta admin memasukkannya ke toko.json.", None)


def kebutuhan_kurang():
    """Modul yang belum terpasang di Python komputer ini."""
    perlu = {"requests": "requests",
             "websocket": "websocket-client",
             "openpyxl": "openpyxl"}
    kurang = []
    for modul, paket in perlu.items():
        try:
            __import__(modul)
        except ImportError:
            kurang.append(paket)
    return kurang


def main():
    try:
        app = Aplikasi()
    except tk.TclError as e:
        print("Tidak bisa membuka jendela:", e)
        return 1

    kurang = kebutuhan_kurang()
    if kurang:
        # Jendela tetap dibuka supaya pesannya terbaca. Traceback di layar
        # hitam tidak bisa dimengerti orang kantor.
        app._tulis("Aplikasi belum lengkap: " + ", ".join(kurang), "galat")
        app._tulis("Tutup aplikasi ini, lalu klik Jalankan.bat "
                   "(bukan gui.py) supaya kebutuhannya dipasang dulu.", "galat")
        messagebox.showerror(
            JUDUL,
            "Aplikasi belum lengkap di komputer ini.\n\n"
            "Belum terpasang: " + ", ".join(kurang) + "\n\n"
            "Tutup jendela ini, lalu buka lewat Jalankan.bat.\n"
            "Batch itu akan memasang kebutuhannya sendiri.")

    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
