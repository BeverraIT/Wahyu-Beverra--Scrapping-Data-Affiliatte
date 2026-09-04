# -*- coding: utf-8 -*-
"""
Mesin CDP: buka Chrome dengan profil toko, sambung ke DevTools Protocol,
sediakan klik mouse asli + penangkap response XHR.

Dipakai bersama oleh rekam_endpoint.py dan tarik_creator.py.
Butuh: pip install websocket-client requests
"""
import json
import os
import shutil
import subprocess
import threading
import time

import requests
import websocket

import konfigurasi as K


def _cari_chrome():
    for p in K.CHROME_PATH_KANDIDAT:
        if p and os.path.exists(p):
            return p
    p = shutil.which("chrome") or shutil.which("google-chrome")
    if p:
        return p
    raise RuntimeError(
        "Google Chrome tidak ketemu di komputer ini.\n"
        "Pasang Chrome dari https://www.google.com/chrome/ lalu coba lagi.\n"
        "Kalau Chrome-nya ada tapi di folder tidak biasa, tambahkan jalurnya\n"
        "ke CHROME_PATH_KANDIDAT di konfigurasi.py.")


# Folder yang tidak perlu ikut disalin: isinya cache, bisa ratusan MB sampai
# GB, dan Chrome membuatnya lagi sendiri.
_ABAIKAN = shutil.ignore_patterns(
    "Cache", "Code Cache", "GPUCache", "GrShaderCache", "ShaderCache",
    "DawnCache", "DawnGraphiteCache", "DawnWebGPUCache", "CacheStorage",
    "Service Worker", "Crashpad", "CrashpadMetrics*", "BrowserMetrics*",
    "DeferredBrowserMetrics", "Local Traces", "optimization_guide_model_store",
    "component_crx_cache", "extensions_crx_cache", "downloads",
    "*.pma", "lockfile", "Singleton*",
)


def chrome_pakai_profil(profil):
    """True kalau ada chrome.exe yang sedang memakai user-data-dir ini.
    Menyalin profil selagi Chrome-nya hidup bikin file cookie (SQLite)
    terkunci / setengah jadi."""
    if os.name != "nt":
        return False
    try:
        keluar = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\""
             " | Select-Object -ExpandProperty CommandLine"],
            capture_output=True, text=True, timeout=60).stdout or ""
    except Exception:
        return False
    return profil.rstrip("\\/").lower() in keluar.lower()


def salin_profil(sumber, tujuan, profil_dir=None, bersih=False, log=print,
                 profil_dir_tujuan=None):
    """Salin sesi login dari profil Chrome lain ke profil milik aplikasi.

    Yang disalin: folder profilnya sendiri (cookie, Login Data, Preferences)
    plus 'Local State' di akar -- file itu menyimpan kunci enkripsi cookie,
    tanpa dia cookie-nya tersalin tapi tidak bisa dibaca.

    profil_dir_tujuan dipakai kalau nama foldernya berbeda di tujuan, mis.
    "Yarra Store" di Chrome kerjaan -> "Default" di profil aplikasi.
    """
    profil_dir = profil_dir or "Default"
    profil_dir_tujuan = profil_dir_tujuan or profil_dir
    asal = os.path.join(sumber, profil_dir)
    if not os.path.isdir(asal):
        raise RuntimeError(
            f"Folder profil tidak ada: {asal}\n"
            f"Cek 'profil_sumber' dan 'profil_dir' di konfigurasi.py. "
            f"Isi {sumber}: {', '.join(sorted(os.listdir(sumber))[:20])}")

    if bersih and os.path.isdir(tujuan):
        log(f"[i] Menghapus profil bot lama: {tujuan}")
        shutil.rmtree(tujuan, ignore_errors=True)
    os.makedirs(tujuan, exist_ok=True)

    ls = os.path.join(sumber, "Local State")
    if os.path.exists(ls):
        shutil.copy2(ls, os.path.join(tujuan, "Local State"))
        log("[i] Local State (kunci enkripsi cookie) disalin")

    tuju = os.path.join(tujuan, profil_dir_tujuan)
    log(f"[i] Menyalin {asal} -> {tuju} (cache dilewati)")
    shutil.copytree(asal, tuju, dirs_exist_ok=True, ignore=_ABAIKAN)

    # tandai supaya Chrome tidak menampilkan layar setup awal
    with open(os.path.join(tujuan, "First Run"), "a"):
        pass
    return tuju


def _siapkan_preferences(profil, profil_dir="Default"):
    """Patch Preferences sebelum Chrome jalan:
    - balon 'Restore pages?' dimatikan
    - kalau OFFSCREEN=False, posisi jendela tersimpan ditarik balik ke layar.
      Chrome menyimpan window_placement terakhir; bekas run offscreen
      (-32000,-32000) bikin jendela tak kelihatan walau flag sudah benar.
    """
    pref = os.path.join(profil, profil_dir or "Default", "Preferences")
    if not os.path.exists(pref):
        return
    try:
        with open(pref, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("profile", {})["exit_type"] = "Normal"
        data["profile"]["exited_cleanly"] = True
        if not K.OFFSCREEN:
            x, y = K.JENDELA_POSISI
            w, h = K.JENDELA_UKURAN
            tempat = data.setdefault("browser", {}).setdefault("window_placement", {})
            tempat.update({"left": x, "top": y, "right": x + w, "bottom": y + h,
                           "maximized": False})
        with open(pref, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


class Mesin:
    def __init__(self, profil_chrome, port=None, log=print, profil_dir=None):
        self.profil = profil_chrome
        self.profil_dir = profil_dir
        self.port = port or K.PORT_CDP
        self.log = log
        self.proc = None
        self.ws = None
        self._id = 0
        self._hasil = {}
        self._kunci = threading.Lock()
        self._jalan = False
        self.target_id = None
        # body response di-cache: menunggu data datang berarti memanen
        # berulang kali, dan Network.getResponseBody itu mahal + isinya
        # kedaluwarsa setelah pindah halaman.
        self._cache_body = {}
        # True kalau menumpang Chrome milik orang -- jangan dimatikan waktu tutup()
        self.dilampirkan = False
        self.tab_dibuat = None
        # request_id -> {url, mime}
        self.respon_masuk = []

    # ---------- siklus hidup ----------
    def buka(self):
        if self._sambung_ke_yang_jalan():
            return self
        return self._jalankan_chrome()

    def _sambung_ke_yang_jalan(self):
        """Chrome toko biasanya sudah dijalankan duluan dengan
        --remote-debugging-port. Kalau port itu hidup, tumpangi saja: sudah
        login, tidak perlu salin profil, tidak ada risiko kena /errorpage."""
        try:
            requests.get(f"http://127.0.0.1:{self.port}/json/version", timeout=2).json()
        except Exception:
            return False
        self.log(f"[cdp] Chrome sudah jalan di port {self.port}, menumpang ke situ")
        r = self._browser_rpc([("Target.createTarget", {"url": "about:blank"})])
        tid = (r[0] if r else {}).get("targetId")
        if not tid:
            self.log("[cdp] gagal membuka tab baru, jalankan Chrome sendiri saja")
            return False
        target = self._tunggu_target(lambda t: t.get("id") == tid)
        if not target:
            self.log("[cdp] tab baru tidak terbaca, jalankan Chrome sendiri saja")
            return False
        self.dilampirkan = True
        self.tab_dibuat = tid
        self._pasang_ws(target)
        # jendela orang tidak digeser-geser, cukup tab kita dimunculkan
        try:
            self.kirim("Page.bringToFront")
        except Exception:
            pass
        self.log("[cdp] Chrome siap (tab baru di jendela yang sudah login)")
        return True

    def _tunggu_target(self, cocok, detik=15):
        batas = time.time() + detik
        while time.time() < batas:
            try:
                lst = requests.get(f"http://127.0.0.1:{self.port}/json", timeout=2).json()
                t = next((t for t in lst if t.get("type") == "page" and cocok(t)), None)
                if t and t.get("webSocketDebuggerUrl"):
                    return t
            except Exception:
                pass
            time.sleep(0.5)
        return None

    def _pasang_ws(self, target):
        self.ws = websocket.create_connection(
            target["webSocketDebuggerUrl"], suppress_origin=True, timeout=60)
        self._jalan = True
        threading.Thread(target=self._pendengar, daemon=True).start()
        self.target_id = target["id"]
        self.kirim("Page.enable")
        self.kirim("Runtime.enable")
        self.kirim("Network.enable")

    def _jalankan_chrome(self):
        # JANGAN menolak kalau folder profilnya belum ada. Chrome membuatnya
        # sendiri saat dijalankan, dan tombol "Login Toko" memang dipakai
        # justru waktu profilnya belum ada -- kalau ditolak di sini, login
        # pertama jadi mustahil (ayam dan telur).
        os.makedirs(self.profil, exist_ok=True)
        _siapkan_preferences(self.profil, self.profil_dir)
        args = [
            _cari_chrome(),
            f"--remote-debugging-port={self.port}",
            f"--user-data-dir={self.profil}",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-session-crashed-bubble",
            "--restore-last-session=false",
            "--disable-features=Translate,OptimizationHints",
            "about:blank",
        ]
        if self.profil_dir:
            # login toko sering tidak ada di "Default"
            args.insert(-1, f"--profile-directory={self.profil_dir}")
        if K.OFFSCREEN:
            args.insert(-1, "--window-position=-32000,-32000")
            args.insert(-1, "--window-size=1600,1000")
        else:
            x, y = K.JENDELA_POSISI
            w, h = K.JENDELA_UKURAN
            args.insert(-1, f"--window-position={x},{y}")
            args.insert(-1, f"--window-size={w},{h}")
        self.proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        target = self._tunggu_target(lambda t: True, detik=30)
        if not target:
            raise RuntimeError(
                "Gagal sambung ke Chrome DevTools. Kemungkinan sudah ada Chrome "
                f"lain memakai profil {self.profil} -- tutup dulu, atau jalankan "
                f"Chrome itu dengan --remote-debugging-port={self.port}")

        self._pasang_ws(target)
        if not K.OFFSCREEN:
            self.tampilkan_jendela()
        self.log("[cdp] Chrome siap")
        return self

    def _browser_rpc(self, panggilan):
        """Kirim perintah ke endpoint browser lewat koneksi pendek sendiri.
        Domain Browser.* dan Target.* tidak tersedia dari websocket halaman."""
        hasil = []
        try:
            info = requests.get(f"http://127.0.0.1:{self.port}/json/version",
                                timeout=5).json()
            bws = websocket.create_connection(info["webSocketDebuggerUrl"],
                                              suppress_origin=True, timeout=15)
        except Exception as e:
            self.log(f"[cdp] tidak bisa sambung ke endpoint browser: {e}")
            return hasil
        try:
            for pid, (metode, params) in enumerate(panggilan, start=1):
                bws.send(json.dumps({"id": pid, "method": metode, "params": params}))
                batas = time.time() + 15
                jawab = {}
                while time.time() < batas:
                    pesan = json.loads(bws.recv())
                    if pesan.get("id") == pid:
                        jawab = pesan
                        break
                hasil.append(jawab.get("result", {}))
        except Exception as e:
            self.log(f"[cdp] perintah browser gagal: {e}")
        finally:
            try:
                bws.close()
            except Exception:
                pass
        return hasil

    def tampilkan_jendela(self):
        """Tarik jendela ke dalam layar dan munculkan ke depan.
        Flag --window-position kadang kalah dari posisi tersimpan di profil."""
        if not self.target_id:
            return
        x, y = K.JENDELA_POSISI
        w, h = K.JENDELA_UKURAN
        r = self._browser_rpc([("Browser.getWindowForTarget",
                                {"targetId": self.target_id})])
        wid = (r[0] if r else {}).get("windowId")
        if wid is None:
            self.log("[cdp] windowId tidak ketemu, jendela dibiarkan apa adanya")
            return
        # normal dulu -- posisi tidak bisa diset selagi minimized/maximized
        self._browser_rpc([
            ("Browser.setWindowBounds",
             {"windowId": wid, "bounds": {"windowState": "normal"}}),
            ("Browser.setWindowBounds",
             {"windowId": wid,
              "bounds": {"left": x, "top": y, "width": w, "height": h}}),
        ])
        self.log(f"[cdp] jendela ditaruh di {x},{y} ukuran {w}x{h}")
        try:
            self.kirim("Page.bringToFront")
        except Exception:
            pass

    def tutup(self):
        self._jalan = False
        try:
            self.ws.close()
        except Exception:
            pass
        if self.dilampirkan:
            # Chrome ini punya orang -- jangan dimatikan, cukup tutup tab kita
            if self.tab_dibuat:
                self._browser_rpc([("Target.closeTarget",
                                    {"targetId": self.tab_dibuat})])
            return
        try:
            self.proc.terminate()
        except Exception:
            pass

    # ---------- lapisan protokol ----------
    def _pendengar(self):
        while self._jalan:
            try:
                pesan = json.loads(self.ws.recv())
            except Exception:
                break
            if "id" in pesan:
                with self._kunci:
                    self._hasil[pesan["id"]] = pesan
            elif pesan.get("method") == "Network.responseReceived":
                p = pesan["params"]
                if p["type"] in ("XHR", "Fetch"):
                    self.respon_masuk.append({
                        "request_id": p["requestId"],
                        "url": p["response"]["url"],
                        "status": p["response"]["status"],
                    })

    def kirim(self, metode, params=None, timeout=30):
        self._id += 1
        pid = self._id
        self.ws.send(json.dumps({"id": pid, "method": metode, "params": params or {}}))
        batas = time.time() + timeout
        while time.time() < batas:
            with self._kunci:
                if pid in self._hasil:
                    return self._hasil.pop(pid)
            time.sleep(0.02)
        raise TimeoutError(f"CDP timeout: {metode}")

    def js(self, ekspresi, timeout=30):
        r = self.kirim("Runtime.evaluate", {
            "expression": ekspresi,
            "returnByValue": True,
            "awaitPromise": True,
        }, timeout=timeout)
        hasil = r.get("result", {}).get("result", {})
        if r.get("result", {}).get("exceptionDetails"):
            raise RuntimeError(str(r["result"]["exceptionDetails"]))
        return hasil.get("value")

    def buka_url(self, url, tunggu=3.0):
        self.kirim("Page.navigate", {"url": url})
        time.sleep(tunggu)
        for _ in range(40):
            if self.js("document.readyState") == "complete":
                break
            time.sleep(0.5)

    # ---------- interaksi manusiawi ----------
    def klik_asli(self, x, y):
        """Klik pakai event mouse asli. WAJIB untuk kalender/tanggal --
        .click() dari JS kelihatan jalan tapi nilainya tidak pernah commit."""
        for tipe in ("mousePressed", "mouseReleased"):
            self.kirim("Input.dispatchMouseEvent", {
                "type": tipe, "x": x, "y": y, "button": "left",
                "clickCount": 1, "buttons": 1,
            })
            time.sleep(0.05)

    def klik_selektor(self, selektor, indeks=0):
        """Cari posisi tengah elemen lalu klik pakai mouse asli."""
        kotak = self.js(f"""
            (() => {{
              const el = document.querySelectorAll({json.dumps(selektor)})[{indeks}];
              if (!el) return null;
              el.scrollIntoView({{block:'center'}});
              const r = el.getBoundingClientRect();
              return {{x: r.left + r.width/2, y: r.top + r.height/2}};
            }})()
        """)
        if not kotak:
            return False
        self.klik_asli(kotak["x"], kotak["y"])
        return True

    def klik_dari_js(self, ekspresi, gulir=True):
        """Klik elemen hasil ekspresi JS (harus mengembalikan Element).
        Tetap pakai event mouse asli -- .click() dari JS kelihatan jalan tapi
        komponen kora (kalender, paginasi) tidak pernah commit nilainya."""
        kotak = self.js(f"""
            (() => {{
              const el = ({ekspresi});
              if (!el) return null;
              {"el.scrollIntoView({block:'center'});" if gulir else ""}
              const r = el.getBoundingClientRect();
              if (!r.width || !r.height) return null;
              return {{x: r.left + r.width / 2, y: r.top + r.height / 2}};
            }})()
        """)
        if not kotak:
            return False
        self.klik_asli(kotak["x"], kotak["y"])
        return True

    def ketik(self, teks, jeda=0.03):
        """Ketik pakai event keyboard asli."""
        for ch in teks:
            for tipe in ("keyDown", "keyUp"):
                self.kirim("Input.dispatchKeyEvent", {
                    "type": tipe, "key": ch,
                    "text": ch if tipe == "keyDown" else "",
                    "unmodifiedText": ch if tipe == "keyDown" else "",
                })
            time.sleep(jeda)

    _TOMBOL = {"Enter": (13, "\r"), "Tab": (9, "\t"),
               "Escape": (27, ""), "Backspace": (8, "")}

    def tekan(self, nama):
        kode, teks = self._TOMBOL[nama]
        for tipe in ("keyDown", "keyUp"):
            self.kirim("Input.dispatchKeyEvent", {
                "type": tipe, "key": nama, "code": nama,
                "windowsVirtualKeyCode": kode, "nativeVirtualKeyCode": kode,
                "text": teks if tipe == "keyDown" else "",
            })
            time.sleep(0.05)

    def pilih_semua(self):
        """Ctrl+A di elemen yang sedang fokus."""
        for tipe in ("keyDown", "keyUp"):
            self.kirim("Input.dispatchKeyEvent", {
                "type": tipe, "key": "a", "code": "KeyA", "modifiers": 2,
                "windowsVirtualKeyCode": 65, "nativeVirtualKeyCode": 65,
            })
            time.sleep(0.05)

    def klik_teks(self, teks, tag="*"):
        """Klik elemen pertama yang teksnya persis sama."""
        kotak = self.js(f"""
            (() => {{
              const t = {json.dumps(teks)};
              const els = [...document.querySelectorAll({json.dumps(tag)})]
                .filter(e => e.children.length === 0 && e.textContent.trim() === t);
              if (!els.length) return null;
              const el = els[0];
              el.scrollIntoView({{block:'center'}});
              const r = el.getBoundingClientRect();
              return {{x: r.left + r.width/2, y: r.top + r.height/2}};
            }})()
        """)
        if not kotak:
            return False
        self.klik_asli(kotak["x"], kotak["y"])
        return True

    # ---------- jaringan ----------
    def ambil_body(self, request_id):
        if request_id in self._cache_body:
            return self._cache_body[request_id]
        try:
            r = self.kirim("Network.getResponseBody", {"requestId": request_id}, timeout=15)
            body = r.get("result", {}).get("body")
        except Exception:
            body = None
        if body:
            self._cache_body[request_id] = body
        return body

    def bersihkan_respon(self):
        self.respon_masuk.clear()
        self._cache_body.clear()

    # ---------- perekam klik ----------
    _JS_REKAM_KLIK = r"""
    (() => {
      if (window.__jejakPasang) return;
      window.__jejakPasang = true;
      window.__jejak = [];
      const sel = (el) => {
        if (!el || el === document.body) return 'body';
        if (el.id) return '#' + CSS.escape(el.id);
        let s = el.tagName.toLowerCase();
        const cls = (el.className || '').toString().trim().split(/\s+/)
                      .filter(c => c && !/^\d/.test(c)).slice(0, 3);
        if (cls.length) s += '.' + cls.map(c => CSS.escape(c)).join('.');
        const ind = el.parentElement
          ? [...el.parentElement.children].indexOf(el) + 1 : 0;
        return (el.parentElement ? sel(el.parentElement) + ' > ' : '') +
               s + ':nth-child(' + ind + ')';
      };
      document.addEventListener('click', (e) => {
        const t = e.target;
        if (!t || !t.tagName) return;
        window.__jejak.push({
          waktu: Date.now(),
          selektor: sel(t),
          tag: t.tagName.toLowerCase(),
          teks: (t.innerText || t.value || '').trim().slice(0, 80),
          aria: t.getAttribute('aria-label') || '',
          peran: t.getAttribute('role') || '',
          testid: t.getAttribute('data-testid') || t.getAttribute('data-tid') || '',
          url: location.href.slice(0, 200),
        });
      }, true);
    })()
    """

    def rekam_klik(self):
        """Pasang perekam klik. Dipasang juga untuk setiap dokumen baru supaya
        tetap hidup kalau halamannya reload."""
        try:
            self.kirim("Page.addScriptToEvaluateOnNewDocument",
                       {"source": self._JS_REKAM_KLIK})
        except Exception as e:
            self.log(f"[cdp] perekam klik tidak terpasang permanen: {e}")
        try:
            self.js(self._JS_REKAM_KLIK)
            return True
        except Exception as e:
            self.log(f"[cdp] perekam klik gagal: {e}")
            return False

    def ambil_klik(self):
        try:
            return json.loads(self.js("JSON.stringify(window.__jejak || [])") or "[]")
        except Exception:
            return []

    def panen_respon(self, pola=None, sejak_indeks=0, saring_host=True):
        """Ambil response XHR yang URL-nya cocok pola, buang yang jelas bukan
        data (i18n, captcha, telemetry) supaya heuristik tidak salah tebak."""
        pola = pola or K.POLA_API
        keluar = []
        for r in self.respon_masuk[sejak_indeks:]:
            url = r["url"].lower()
            if not any(p.lower() in url for p in pola):
                continue
            if saring_host:
                if not any(h.lower() in url for h in K.HOST_API):
                    continue
                if any(a.lower() in url for a in K.POLA_ABAIKAN):
                    continue
            body = self.ambil_body(r["request_id"])
            if body:
                keluar.append({"url": r["url"], "body": body})
        return keluar

    def tangkap_layar(self, nama):
        try:
            r = self.kirim("Page.captureScreenshot", {"format": "png"})
            import base64
            jalur = os.path.join(K.DIR_SS, f"{nama}.png")
            with open(jalur, "wb") as f:
                f.write(base64.b64decode(r["result"]["data"]))
            return jalur
        except Exception:
            return None
