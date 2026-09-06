# NJIAFIX MOBILE
# On-device self-diagnostics for Android: Battery, Storage, RAM, Network.
#
# Same core rule as desktop NJIAFIX: NO REAL DATA -> NO FAULT.
# Every reading either comes from a real source on the device, or the field
# shows "HAIPATIKANI" (UNAVAILABLE) -- it is never guessed or faked.

import os
import shutil
import socket
import threading
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp

UNAVAILABLE = "HAIPATIKANI"


def read_battery():
    """Returns dict with percent/charging, or None if not readable."""
    try:
        from plyer import battery
        status = battery.status  # {'isCharging': bool, 'percentage': float}
        if not status:
            return None
        pct = status.get("percentage")
        charging = status.get("isCharging")
        if pct is None:
            return None
        return {
            "percent": round(pct, 1),
            "charging": bool(charging) if charging is not None else None,
        }
    except Exception:
        return None


def read_storage():
    """Returns dict with total/used/free GB for the main storage volume."""
    candidates = []
    try:
        from android.storage import primary_external_storage_path
        candidates.append(primary_external_storage_path())
    except Exception:
        pass
    candidates.append(os.path.expanduser("~"))
    candidates.append("/")

    for path in candidates:
        try:
            usage = shutil.disk_usage(path)
            gb = 1024 ** 3
            return {
                "total_gb": round(usage.total / gb, 2),
                "used_gb": round((usage.total - usage.free) / gb, 2),
                "free_gb": round(usage.free / gb, 2),
                "percent_used": round((usage.total - usage.free) / usage.total * 100, 1),
            }
        except Exception:
            continue
    return None


def read_ram():
    """Reads /proc/meminfo directly -- works on Android since its kernel is Linux."""
    try:
        info = {}
        with open("/proc/meminfo", "r") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) != 2:
                    continue
                key = parts[0].strip()
                value = parts[1].strip().split()[0]  # value in kB
                info[key] = int(value)

        total_kb = info.get("MemTotal")
        avail_kb = info.get("MemAvailable")
        if total_kb is None or avail_kb is None:
            return None

        used_kb = total_kb - avail_kb
        return {
            "total_mb": round(total_kb / 1024, 1),
            "used_mb": round(used_kb / 1024, 1),
            "available_mb": round(avail_kb / 1024, 1),
            "percent_used": round(used_kb / total_kb * 100, 1),
        }
    except Exception:
        return None


def read_network():
    """Real reachability check: opens a TCP connection, does not assume anything."""
    test_hosts = [("8.8.8.8", 53), ("1.1.1.1", 53)]
    for host, port in test_hosts:
        try:
            socket.setdefaulttimeout(3)
            s = socket.create_connection((host, port))
            s.close()
            return {"connected": True, "checked_via": f"{host}:{port}"}
        except Exception:
            continue
    return {"connected": False, "checked_via": None}


class DiagnosticRow(BoxLayout):
    def __init__(self, label_text, value_text, severity="info", **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(40), **kwargs)
        colors = {
            "info": (0.38, 0.89, 0.58, 1),
            "warning": (1, 0.82, 0.4, 1),
            "critical": (1, 0.42, 0.48, 1),
            "unavailable": (0.6, 0.6, 0.6, 1),
        }
        self.add_widget(Label(text=label_text, size_hint_x=0.5, halign="left", valign="middle"))
        val = Label(text=value_text, size_hint_x=0.5, halign="right", valign="middle",
                    color=colors.get(severity, colors["info"]))
        self.add_widget(val)


class NjiafixMobileRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(16), spacing=dp(10), **kwargs)

        title = Label(text="NJIAFIX MOBILE", font_size="22sp", size_hint_y=None, height=dp(40), bold=True)
        subtitle = Label(text="Kagua Simu Yako - Live Diagnostics", font_size="13sp",
                          size_hint_y=None, height=dp(24), color=(0.7, 0.7, 0.7, 1))
        self.add_widget(title)
        self.add_widget(subtitle)

        scroll = ScrollView(size_hint=(1, 1))
        self.results_box = GridLayout(cols=1, size_hint_y=None, spacing=dp(4))
        self.results_box.bind(minimum_height=self.results_box.setter("height"))
        scroll.add_widget(self.results_box)
        self.add_widget(scroll)

        self.status_label = Label(text="Bonyeza 'Anza Uchunguzi' kuanza.", size_hint_y=None, height=dp(30))
        self.add_widget(self.status_label)

        btn_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        scan_btn = Button(text="Anza Uchunguzi")
        scan_btn.bind(on_press=self.start_scan)
        save_btn = Button(text="Hifadhi Ripoti")
        save_btn.bind(on_press=self.save_report)
        btn_row.add_widget(scan_btn)
        btn_row.add_widget(save_btn)
        self.add_widget(btn_row)

        self.last_results = {}

    def start_scan(self, *_):
        self.status_label.text = "Inachunguza..."
        self.results_box.clear_widgets()
        threading.Thread(target=self._run_scan, daemon=True).start()

    def _run_scan(self):
        battery = read_battery()
        storage = read_storage()
        ram = read_ram()
        network = read_network()
        Clock.schedule_once(lambda dt: self._render_results(battery, storage, ram, network))

    def _render_results(self, battery, storage, ram, network):
        self.last_results = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "battery": battery,
            "storage": storage,
            "ram": ram,
            "network": network,
        }

        # Battery
        if battery:
            sev = "critical" if battery["percent"] <= 15 and not battery["charging"] else "info"
            charge_txt = "Inachaji" if battery["charging"] else "Haichaji"
            self.results_box.add_widget(
                DiagnosticRow("Betri", f"{battery['percent']}% ({charge_txt})", sev)
            )
        else:
            self.results_box.add_widget(DiagnosticRow("Betri", UNAVAILABLE, "unavailable"))

        # Storage
        if storage:
            sev = "critical" if storage["percent_used"] >= 90 else ("warning" if storage["percent_used"] >= 75 else "info")
            self.results_box.add_widget(
                DiagnosticRow("Hifadhi (Storage)",
                              f"{storage['used_gb']}/{storage['total_gb']} GB ({storage['percent_used']}%)", sev)
            )
        else:
            self.results_box.add_widget(DiagnosticRow("Hifadhi (Storage)", UNAVAILABLE, "unavailable"))

        # RAM
        if ram:
            sev = "critical" if ram["percent_used"] >= 90 else ("warning" if ram["percent_used"] >= 75 else "info")
            self.results_box.add_widget(
                DiagnosticRow("RAM", f"{ram['used_mb']}/{ram['total_mb']} MB ({ram['percent_used']}%)", sev)
            )
        else:
            self.results_box.add_widget(DiagnosticRow("RAM", UNAVAILABLE, "unavailable"))

        # Network
        if network["connected"]:
            self.results_box.add_widget(DiagnosticRow("Mtandao (Internet)", "Imeunganishwa", "info"))
        else:
            self.results_box.add_widget(DiagnosticRow("Mtandao (Internet)", "Hakuna muunganiko", "critical"))

        self.status_label.text = f"Imekamilika - {self.last_results['timestamp']}"

    def save_report(self, *_):
        if not self.last_results:
            self.status_label.text = "Fanya uchunguzi kwanza kabla ya kuhifadhi."
            return
        try:
            target_dir = None
            try:
                from android.storage import primary_external_storage_path
                target_dir = primary_external_storage_path()
            except Exception:
                target_dir = os.path.expanduser("~")

            fname = f"NJIAFIX_Mobile_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            path = os.path.join(target_dir, fname)

            lines = ["NJIAFIX MOBILE - RIPOTI YA UCHUNGUZI", f"Tarehe: {self.last_results['timestamp']}", ""]
            for key in ("battery", "storage", "ram", "network"):
                lines.append(f"{key.upper()}: {self.last_results[key] if self.last_results[key] else UNAVAILABLE}")

            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            self.status_label.text = f"Ripoti imehifadhiwa: {path}"
        except Exception as e:
            self.status_label.text = f"Hitilafu ya kuhifadhi: {e}"


class NjiafixMobileApp(App):
    def build(self):
        self.title = "NJIAFIX MOBILE"
        return NjiafixMobileRoot()


if __name__ == "__main__":
    NjiafixMobileApp().run()
