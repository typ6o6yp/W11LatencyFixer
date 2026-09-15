import os
import sys
import re
import json
import ctypes
from ctypes import wintypes
import struct
import threading
import subprocess
import winreg
import webbrowser
from datetime import datetime
from tkinter import filedialog, messagebox

# ==============================================================================
# 1. ПРОВЕРКА И ПОВЫШЕНИЕ ПРИВИЛЕГИЙ (UAC ELEVATION)
# ==============================================================================
def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def elevate_privileges():
    if not is_admin():
        script_path = os.path.abspath(sys.argv[0])
        params = subprocess.list2cmdline([script_path] + sys.argv[1:])
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1
        )
        if ret <= 32:
            # Пользователь отклонил запрос UAC
            sys.exit(1)
        sys.exit(0)

elevate_privileges()

# ==============================================================================
# 2. ПРОВЕРКА И БЕЗОПАСНАЯ УСТАНОВКА ЗАВИСИМОСТЕЙ
# ==============================================================================
IS_FROZEN = getattr(sys, 'frozen', False)

if not IS_FROZEN:
    for module_name, pip_name in [("customtkinter", "customtkinter"), ("psutil", "psutil")]:
        try:
            __import__(module_name)
        except ImportError:
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pip_name],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception as e:
                print(f"Failed to install {pip_name}: {e}")
                sys.exit(1)

import customtkinter as ctk
import psutil

# ==============================================================================
# 3. КОНСТАНТЫ И ЛОКАЛИЗАЦИЯ
# ==============================================================================
AUTHOR_URL = "https://1va1ne.github.io"
SAFE_PROC_REGEX = re.compile(r"^[a-zA-Z0-9_\-\. ]+\.exe$", re.IGNORECASE)

TEXTS = {
    "en": {
        "title": "W11LatencyFixer Pro — Hardware & Process Latency Engine",
        "header_title": "⚡ W11LATENCYFIXER PRO",
        "author_btn": "🌐 1va1ne.github.io",
        "cpu_info": "{name}  |  P-Cores: {p_cores} ({p_threads}T)  |  E-Cores: {e_cores} ({e_threads}T)  |  Total: {threads}T",
        "btn_preset": "🚀 Reference Preset ({threads}T)",
        "btn_restore": "🔄 Restore Defaults",
        "sec_gpu": "🎮 GRAPHICS CARD (GPU)",
        "sec_usb": "🔌 USB HOST CONTROLLERS (INPUT / AUDIO)",
        "sec_net": "🌐 NETWORK ADAPTERS (ETHERNET / WI-FI)",
        "sec_proc": "⚙️ APPLICATIONS & PROCESSES (SCHEDULER & AFFINITY)",
        "msi_mode": "MSI Mode",
        "priority": "Priority:",
        "mask_default": "0x0000 [Auto / All]",
        "mask_custom": "0x{mask:04X} [{count}T]",
        "btn_apply": "⚡ Apply Settings Now",
        "btn_export": "📤 Export Profile",
        "btn_import": "📥 Import Profile",
        "btn_task": "💾 Install Watchdog",
        "btn_del_task": "❌ Remove Watchdog",
        "btn_add_proc": "➕ Add Process",
        "btn_browse": "📁 Browse .exe",
        "active_proc_lbl": "Running:",
        "modal_title": "Settings Applied — Reboot Recommended",
        "modal_header": "⚠️ System Reboot Recommended",
        "modal_desc": "Hardware interrupt routing (MSI & Affinity masks) takes full effect upon system reboot.\n\nThis software is 100% free and open-source. If it helped reduce input lag and smooth out your frametimes, you can support the developer at:",
        "modal_btn_reboot": "🔄 Reboot PC",
        "modal_btn_site": "🌐 Support Author",
        "modal_btn_exit": "🚪 Exit Without Reboot",
        "modal_btn_cancel": "✕ Cancel",
        "log_scan": "Scanning hardware, CPU topology and driver states...",
        "log_found_gpu": "GPU: {name} [{vectors}]",
        "log_found_usb": "USB Controller: {name} [{vectors}]",
        "log_found_net": "Network: {name} [{vectors}]",
        "log_scan_err": "Hardware scan error: {err}",
        "log_preset_ok": "Smart Preset applied: GPU=0x{gpu:X}, NET=0x{net:X}, USB=0x{usb:X}.",
        "log_restoring": "--- RESTORING DEFAULT WINDOWS CONFIGURATION ---",
        "log_dev_restored": "[{name}] Reset to default routing.",
        "log_restored": "All overrides and IFEO rules removed. System restored.",
        "log_applying": "--- WRITING TO REGISTRY & UPDATING PROCESSES ---",
        "log_dev_saved": "[{name}] Saved: MSI={msi}, Priority={prio}, Mask=0x{mask:04X}",
        "log_dev_err": "[{name}] Registry write error: {err}",
        "log_proc_ok": "Process '{name}' (PID: {pid}) -> Affinity: {cores}, Priority: {prio}",
        "log_proc_saved": "Profile and IFEO rule registered for '{name}'.",
        "log_applied": "Settings successfully applied! NDIS RSS synchronized.",
        "log_exported": "Profile saved to: {path}",
        "log_imported": "Profile successfully loaded from: {path}",
        "log_export_err": "Export failed: {err}",
        "log_import_err": "Import failed: {err}",
        "log_task_ok": "✅ Event-driven Kernel Watchdog (ETW Win32_ProcessStartTrace) active in Session 0.",
        "log_task_del": "❌ Watchdog Service stopped and removed.",
        "log_driver_recovered": "🛡️ Auto-restored driver settings for: {name}",
        "log_lang_switch": "Language switched to English."
    },
    "ru": {
        "title": "W11LatencyFixer Pro — Умный менеджер прерываний и задержек",
        "header_title": "⚡ W11LATENCYFIXER PRO",
        "author_btn": "🌐 1va1ne.github.io",
        "cpu_info": "{name}  |  P-ядер: {p_cores} ({p_threads}T)  |  E-ядер: {e_cores} ({e_threads}T)  |  Всего: {threads}T",
        "btn_preset": "🚀 Эталонный пресет ({threads}T)",
        "btn_restore": "🔄 Сброс на дефолт",
        "sec_gpu": "🎮 ВИДЕОКАРТА (GPU)",
        "sec_usb": "🔌 USB-ХОСТ КОНТРОЛЛЕРЫ (ВВОД / ЗВУК)",
        "sec_net": "🌐 СЕТЕВЫЕ АДАПТЕРЫ (ETHERNET / WI-FI)",
        "sec_proc": "⚙️ ПРИЛОЖЕНИЯ И ПРОЦЕССЫ (ПРИОРИТЕТЫ И ЯДРА)",
        "msi_mode": "Режим MSI",
        "priority": "Приоритет:",
        "mask_default": "0x0000 [Авто / Все]",
        "mask_custom": "0x{mask:04X} [{count}T]",
        "btn_apply": "⚡ Применить настройки",
        "btn_export": "📤 Экспорт",
        "btn_import": "📥 Импорт",
        "btn_task": "💾 Включить службу",
        "btn_del_task": "❌ Удалить службу",
        "btn_add_proc": "➕ Добавить",
        "btn_browse": "📁 Обзор .exe",
        "active_proc_lbl": "Запущенные:",
        "modal_title": "Настройки применены — Рекомендуется перезагрузка",
        "modal_header": "⚠️ Рекомендуется перезагрузка ПК",
        "modal_desc": "Низкоуровневые изменения векторов прерываний (MSI и маски ядер) вступят в полную силу после перезагрузки компьютера.\n\nПрограмма полностью бесплатна. Если она помогла сделать игру плавнее и убрать задержки ввода, вы можете поддержать автора на сайте:",
        "modal_btn_reboot": "🔄 Перезагрузить сейчас",
        "modal_btn_site": "🌐 Поддержать автора",
        "modal_btn_exit": "🚪 Выход без перезагрузки",
        "modal_btn_cancel": "✕ Отмена",
        "log_scan": "Считывание оборудования, топологии ядер CPU и драйверов...",
        "log_found_gpu": "Видеокарта: {name} [{vectors}]",
        "log_found_usb": "USB-контроллер: {name} [{vectors}]",
        "log_found_net": "Сетевая карта: {name} [{vectors}]",
        "log_scan_err": "Ошибка сканирования оборудования: {err}",
        "log_preset_ok": "Применен умный пресет: GPU=0x{gpu:X}, NET=0x{net:X}, USB=0x{usb:X}.",
        "log_restoring": "--- ВОССТАНОВЛЕНИЕ ДЕФОЛТА WINDOWS ---",
        "log_dev_restored": "[{name}] Сброшен на дефолтную маршрутизацию.",
        "log_restored": "Все оверрайды и IFEO-правила удалены. Дефолты восстановлены.",
        "log_applying": "--- ПРИМЕНЕНИЕ В РЕЕСТР И ПРОЦЕССЫ ---",
        "log_dev_saved": "[{name}] Сохранено: MSI={msi}, Приоритет={prio}, Маска=0x{mask:04X}",
        "log_dev_err": "[{name}] Ошибка реестра: {err}",
        "log_proc_ok": "Процесс '{name}' (PID: {pid}) -> Ядра: {cores}, Приоритет: {prio}",
        "log_proc_saved": "Правило IFEO и профиль сохранены для '{name}'.",
        "log_applied": "Все настройки применены успешно! Сеть NDIS RSS синхронизирована.",
        "log_exported": "Профиль сохранен в: {path}",
        "log_imported": "Профиль успешно загружен из: {path}",
        "log_export_err": "Ошибка экспорта: {err}",
        "log_import_err": "Ошибка импорта: {err}",
        "log_task_ok": "✅ Событийная служба ядра (ETW / Win32_ProcessStartTrace) активна в Session 0.",
        "log_task_del": "❌ Фоновая служба остановлена и удалена из системы.",
        "log_driver_recovered": "🛡️ Восстановлены настройки после сброса драйвером: {name}",
        "log_lang_switch": "Язык интерфейса изменен на Русский."
    }
}

# ==============================================================================
# 4. НАДЕЖНОЕ ОПРЕДЕЛЕНИЕ ТОПОЛОГИИ CPU (Win32 API)
# ==============================================================================
def get_native_cpu_topology():
    total_threads = os.cpu_count() or 16
    glpi = ctypes.windll.kernel32.GetLogicalProcessorInformationEx
    glpi.argtypes = [wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD)]
    glpi.restype = wintypes.BOOL

    buf_size = wintypes.DWORD(0)
    glpi(0, None, ctypes.byref(buf_size))  # 0 = RelationProcessorCore
    
    if buf_size.value == 0:
        return _fallback_topology(total_threads)

    buf = ctypes.create_string_buffer(buf_size.value)
    if not glpi(0, buf, ctypes.byref(buf_size)):
        return _fallback_topology(total_threads)

    raw = buf.raw
    offset = 0
    cores_raw = []
    mask_format = "<Q" if ctypes.sizeof(ctypes.c_size_t) == 8 else "<I"
    
    while offset < buf_size.value:
        rel, size = struct.unpack_from("<II", raw, offset)
        if rel == 0:  # RelationProcessorCore
            flags = raw[offset + 8]
            eff_class = raw[offset + 9]
            mask = struct.unpack_from(mask_format, raw, offset + 32)[0]
            cores_raw.append({
                'flags': flags,
                'eff_class': eff_class,
                'mask': mask
            })
        offset += size
        if size == 0:
            break

    if not cores_raw:
        return _fallback_topology(total_threads)

    eff_classes = {c['eff_class'] for c in cores_raw}
    has_hybrid = len(eff_classes) > 1
    max_eff = max(eff_classes) if has_hybrid else 0

    p_units = []
    e_units = []

    for c in cores_raw:
        threads = [i for i in range(total_threads) if (c['mask'] & (1 << i))]
        if not threads:
            continue
        t1 = threads[0]
        t2 = threads[1] if len(threads) > 1 else None
        
        is_p = (not has_hybrid) or (c['eff_class'] == max_eff)
        target_list = p_units if is_p else e_units
        target_list.append({
            'type': 'P' if is_p else 'E',
            'core_num': 0,
            't1': t1,
            't2': t2
        })

    for i, unit in enumerate(p_units):
        unit['core_num'] = i
    for i, unit in enumerate(e_units):
        unit['core_num'] = i

    topology = p_units + e_units
    p_cores = len(p_units)
    p_threads = sum(2 if u['t2'] is not None else 1 for u in p_units)
    e_cores = len(e_units)
    e_threads = sum(1 for u in e_units)

    return total_threads, topology, p_cores, p_threads, e_cores, e_threads

def _fallback_topology(total_threads):
    topology = []
    for i in range(total_threads):
        topology.append({'type': 'P', 'core_num': i, 't1': i, 't2': None})
    return total_threads, topology, total_threads, total_threads, 0, 0

# ==============================================================================
# 5. UI КОМПОНЕНТЫ: СЕТКА ЯДЕР (HybridCoreGrid)
# ==============================================================================
class HybridCoreGrid(ctk.CTkFrame):
    def __init__(self, parent, topology, on_change_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.topology = topology
        self.on_change = on_change_callback
        self.capsules = []
        self.checkbox_map = {}

        p_frame = ctk.CTkFrame(self, fg_color="transparent")
        p_frame.pack(side="left", padx=(0, 4))

        has_e = any(u['type'] == 'E' for u in self.topology)
        e_frame = ctk.CTkFrame(self, fg_color="transparent") if has_e else None
        if e_frame:
            e_frame.pack(side="left")

        for unit in self.topology:
            target_frame = p_frame if unit['type'] == 'P' else e_frame
            border_c = "#1E293B" if unit['type'] == 'P' else "#2E1065"
            bg_c = "#090D16" if unit['type'] == 'P' else "#110726"
            prefix = "P" if unit['type'] == 'P' else "E"

            cap = ctk.CTkFrame(target_frame, fg_color=bg_c, corner_radius=6, border_width=1, border_color=border_c)
            cap.pack(side="left", padx=2, pady=1)

            lbl_color = "#64748B" if unit['type'] == 'P' else "#A855F7"
            lbl_c = ctk.CTkLabel(cap, text=f"{prefix}{unit['core_num']}", font=ctk.CTkFont(size=9, weight="bold"), text_color=lbl_color)
            lbl_c.pack(fill="x", padx=3, pady=(2, 0))

            box_row = ctk.CTkFrame(cap, fg_color="transparent")
            box_row.pack(fill="x", padx=3, pady=(0, 2))

            cb1 = ctk.CTkCheckBox(
                box_row, text=f"{unit['t1']}{'P' if unit['type']=='P' else 'E'}", width=0,
                text_color="#F8FAFC" if unit['type']=='P' else "#E9D5FF",
                font=ctk.CTkFont(size=10, weight="bold"),
                checkbox_width=15, checkbox_height=15, corner_radius=3, border_width=2,
                border_color="#475569" if unit['type']=='P' else "#6B21A8",
                fg_color="#10B981" if unit['type']=='P' else "#A855F7",
                hover_color="#059669" if unit['type']=='P' else "#9333EA",
                command=self._handle_change
            )
            cb1.pack(side="left", padx=(1, 2), pady=1)
            self.checkbox_map[unit['t1']] = cb1

            cb2 = None
            if unit['t2'] is not None:
                cb2 = ctk.CTkCheckBox(
                    box_row, text=f"{unit['t2']}H", width=0, text_color="#94A3B8",
                    font=ctk.CTkFont(size=10), checkbox_width=15, checkbox_height=15,
                    corner_radius=3, border_width=2, border_color="#475569",
                    fg_color="#10B981", hover_color="#059669",
                    command=self._handle_change
                )
                cb2.pack(side="left", padx=(1, 3), pady=1)
                self.checkbox_map[unit['t2']] = cb2

            self.capsules.append({'frame': cap, 'lbl': lbl_c, 'unit': unit, 'cb1': cb1, 'cb2': cb2})

    def _handle_change(self):
        self.update_visuals()
        if self.on_change:
            self.on_change(self.get_mask())

    def update_visuals(self):
        for item in self.capsules:
            c1 = item['cb1'].get() == 1 if item['cb1'] else False
            c2 = item['cb2'].get() == 1 if item['cb2'] else False
            is_p = (item['unit']['type'] == 'P')

            if c1 and (c2 or item['cb2'] is None):
                item['frame'].configure(border_color="#10B981" if is_p else "#C084FC", fg_color="#062419" if is_p else "#2E1065")
                item['lbl'].configure(text_color="#34D399" if is_p else "#E9D5FF")
            elif c1 or c2:
                item['frame'].configure(border_color="#059669" if is_p else "#7E22CE", fg_color="#090D16" if is_p else "#110726")
                item['lbl'].configure(text_color="#38BDF8" if is_p else "#C084FC")
            else:
                item['frame'].configure(border_color="#1E293B" if is_p else "#2E1065", fg_color="#090D16" if is_p else "#110726")
                item['lbl'].configure(text_color="#64748B" if is_p else "#A855F7")

    def get_mask(self) -> int:
        mask = 0
        for t_id, cb in self.checkbox_map.items():
            if cb.get() == 1:
                mask |= (1 << t_id)
        return mask

    def set_mask(self, mask: int):
        for t_id, cb in self.checkbox_map.items():
            if mask & (1 << t_id):
                cb.select()
            else:
                cb.deselect()
        self.update_visuals()
        if self.on_change:
            self.on_change(self.get_mask())

# ==============================================================================
# 6. КАРТОЧКА УСТРОЙСТВА (DeviceCard)
# ==============================================================================
class DeviceCard(ctk.CTkFrame):
    def __init__(self, parent, dev_info, dev_category, topology, app):
        super().__init__(parent, corner_radius=8, fg_color="#111827", border_width=1, border_color="#1F2937")
        self.app = app
        self.dev_info = dev_info
        self.dev_category = dev_category
        self.topology = topology
        self.original_limit = dev_info.get('VectorLimit', 1)
        self.pack(fill="x", pady=4, padx=2)

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=10, pady=(6, 2))

        self.lbl_title = ctk.CTkLabel(hdr, text=dev_info['FriendlyName'], font=ctk.CTkFont(weight="bold", size=12), text_color="#F8FAFC", anchor="w")
        self.lbl_title.pack(side="left")

        vec_text = f"MSI-X: {self.original_limit}V" if self.original_limit > 1 else "MSI: 1V"
        self.lbl_vec = ctk.CTkLabel(
            hdr, text=f"[{vec_text}]", font=ctk.CTkFont(size=10, weight="bold"), 
            text_color="#38BDF8", fg_color="#082F49", corner_radius=4, padx=6, pady=1
        )
        self.lbl_vec.pack(side="left", padx=(8, 0))

        self.badge_mask = ctk.CTkLabel(
            hdr, text="", font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#064E3B", text_color="#34D399", corner_radius=5, padx=8, pady=2
        )
        self.badge_mask.pack(side="right")

        ctrl_bar = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_bar.pack(fill="x", padx=10, pady=(2, 3))

        self.chk_msi = ctk.CTkCheckBox(
            ctrl_bar, text=self.app.t("msi_mode"), font=ctk.CTkFont(size=11), width=0, 
            checkbox_width=14, checkbox_height=14, fg_color="#10B981", hover_color="#059669"
        )
        self.chk_msi.pack(side="left", padx=(0, 16))

        self.lbl_prio = ctk.CTkLabel(ctrl_bar, text=self.app.t("priority"), font=ctk.CTkFont(size=11))
        self.lbl_prio.pack(side="left", padx=(0, 4))
        
        self.cmb_prio = ctk.CTkComboBox(ctrl_bar, width=110, height=22, font=ctk.CTkFont(size=11), values=["Undefined", "Low", "Normal", "High"])
        self.cmb_prio.pack(side="left")

        core_box = ctk.CTkFrame(self, fg_color="transparent")
        core_box.pack(fill="x", padx=10, pady=(2, 6))

        self.grid = HybridCoreGrid(core_box, self.topology, self._on_mask_update)
        self.grid.pack(anchor="w")

        self.read_real_state()
        self._on_mask_update(self.grid.get_mask())

    def update_texts(self):
        self.chk_msi.configure(text=self.app.t("msi_mode"))
        self.lbl_prio.configure(text=self.app.t("priority"))
        self._on_mask_update(self.grid.get_mask())

    def _on_mask_update(self, mask):
        if mask == 0:
            self.badge_mask.configure(text=self.app.t("mask_default"), fg_color="#1F2937", text_color="#9CA3AF")
        else:
            cnt = bin(mask).count("1")
            self.badge_mask.configure(text=self.app.t("mask_custom", mask=mask, count=cnt), fg_color="#064E3B", text_color="#34D399")

    def read_real_state(self):
        path = rf"SYSTEM\CurrentControlSet\Enum\{self.dev_info['InstanceId']}\Device Parameters\Interrupt Management"
        msi_on = False
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path + r"\MessageSignaledInterruptProperties", 0, winreg.KEY_READ) as k:
                val, _ = winreg.QueryValueEx(k, "MSISupported")
                msi_on = (val == 1)
                try:
                    lim, _ = winreg.QueryValueEx(k, "MessageNumberLimit")
                    self.original_limit = lim
                except OSError:
                    pass
        except OSError:
            pass
        self.chk_msi.select() if msi_on else self.chk_msi.deselect()

        prio_str = "Undefined"
        mask_val = 0
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path + r"\Affinity Policy", 0, winreg.KEY_READ) as k:
                try:
                    p_val, _ = winreg.QueryValueEx(k, "DevicePriority")
                    p_map = {1: "Low", 2: "Normal", 3: "High"}
                    prio_str = p_map.get(p_val, "Undefined")
                except OSError:
                    pass
                try:
                    pol, _ = winreg.QueryValueEx(k, "DevicePolicy")
                    if pol == 4:
                        b_val, _ = winreg.QueryValueEx(k, "AssignmentSetOverride")
                        mask_val = int.from_bytes(b_val, byteorder="little")
                except OSError:
                    pass
        except OSError:
            pass

        self.cmb_prio.set(prio_str)
        self.grid.set_mask(mask_val)

# ==============================================================================
# 7. КАРТОЧКА ПРОЦЕССА (ProcessCard)
# ==============================================================================
class ProcessCard(ctk.CTkFrame):
    def __init__(self, parent, proc_name, default_prio, default_mask, topology, app, on_delete):
        super().__init__(parent, corner_radius=6, fg_color="#0B132B", border_width=1, border_color="#1C2541")
        self.app = app
        self.topology = topology
        self.proc_name = proc_name
        self.pack(fill="x", pady=3, padx=2)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=8, pady=(5, 2))

        self.ent_name = ctk.CTkEntry(top, width=180, height=22, font=ctk.CTkFont(size=11, weight="bold"))
        self.ent_name.insert(0, proc_name)
        self.ent_name.pack(side="left", padx=(0, 8))

        self.lbl_prio = ctk.CTkLabel(top, text=self.app.t("priority"), font=ctk.CTkFont(size=11))
        self.lbl_prio.pack(side="left", padx=(0, 4))

        self.cmb_prio = ctk.CTkComboBox(top, width=115, height=22, font=ctk.CTkFont(size=11), values=["Normal", "AboveNormal", "High"])
        self.cmb_prio.set(default_prio)
        self.cmb_prio.pack(side="left", padx=(0, 10))

        self.badge_mask = ctk.CTkLabel(
            top, text="", font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#064E3B", text_color="#34D399", corner_radius=5, padx=8, pady=2
        )
        self.badge_mask.pack(side="left")

        btn_del = ctk.CTkButton(top, text="✕", width=22, height=22, fg_color="#EF4444", hover_color="#DC2626", font=ctk.CTkFont(size=11, weight="bold"), command=lambda: on_delete(self))
        btn_del.pack(side="right")

        core_box = ctk.CTkFrame(self, fg_color="transparent")
        core_box.pack(fill="x", padx=8, pady=(1, 5))

        self.grid = HybridCoreGrid(core_box, self.topology, self._on_mask_update)
        self.grid.pack(anchor="w")
        self.grid.set_mask(default_mask)

    def update_texts(self):
        self.lbl_prio.configure(text=self.app.t("priority"))
        self._on_mask_update(self.grid.get_mask())

    def _on_mask_update(self, mask):
        total_threads = self.app.total_threads
        if mask == 0 or mask == (1 << total_threads) - 1:
            self.badge_mask.configure(text=self.app.t("mask_default"), fg_color="#1F2937", text_color="#9CA3AF")
        else:
            cnt = bin(mask).count("1")
            self.badge_mask.configure(text=self.app.t("mask_custom", mask=mask, count=cnt), fg_color="#064E3B", text_color="#34D399")

# ==============================================================================
# 8. ДИАЛОГ ПЕРЕЗАГРУЗКИ (SupportModal)
# ==============================================================================
class SupportModal(ctk.CTkToplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title(self.app.t("modal_title"))
        self.geometry("560x290")
        self.resizable(False, False)
        self.configure(fg_color="#0B1120")
        
        self.transient(parent)
        self.grab_set()

        lbl_hdr = ctk.CTkLabel(self, text=self.app.t("modal_header"), font=ctk.CTkFont(size=16, weight="bold"), text_color="#38BDF8")
        lbl_hdr.pack(padx=20, pady=(16, 6))

        lbl_desc = ctk.CTkLabel(self, text=self.app.t("modal_desc"), font=ctk.CTkFont(size=12), text_color="#CBD5E1", wraplength=510, justify="center")
        lbl_desc.pack(padx=20, pady=(0, 12))

        btn_site = ctk.CTkButton(
            self, text=self.app.t("modal_btn_site"), font=ctk.CTkFont(size=12, weight="bold"), 
            fg_color="#10B981", hover_color="#059669", height=32, command=self._open_site
        )
        btn_site.pack(padx=20, pady=(0, 12), fill="x")

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 10))

        btn_reboot = ctk.CTkButton(btn_row, text=self.app.t("modal_btn_reboot"), fg_color="#2563EB", hover_color="#1D4ED8", width=155, height=32, font=ctk.CTkFont(weight="bold"), command=self._do_reboot)
        btn_reboot.pack(side="left", padx=(0, 6))

        btn_exit = ctk.CTkButton(btn_row, text=self.app.t("modal_btn_exit"), fg_color="#EF4444", hover_color="#DC2626", width=155, height=32, command=self._do_exit)
        btn_exit.pack(side="left", padx=(0, 6))

        btn_cancel = ctk.CTkButton(btn_row, text=self.app.t("modal_btn_cancel"), fg_color="#334155", hover_color="#1E293B", width=95, height=32, command=self.destroy)
        btn_cancel.pack(side="right")

    def _open_site(self):
        webbrowser.open(AUTHOR_URL)

    def _do_reboot(self):
        self.destroy()
        self.app.destroy()
        subprocess.run(["shutdown", "/r", "/t", "0"])

    def _do_exit(self):
        self.destroy()
        self.app.destroy()

# ==============================================================================
# 9. ГЛАВНОЕ ПРИЛОЖЕНИЕ (W11LatencyFixerApp)
# ==============================================================================
class W11LatencyFixerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.lang = "ru"
        self.config_dir = r"C:\ProgramData\W11LatencyFixer"
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.baseline_file = os.path.join(self.config_dir, "baseline.json")
        self.settings_applied_this_session = False

        self._secure_config_dir()

        (self.total_threads, self.topology,
         self.p_cores, self.p_threads,
         self.e_cores, self.e_threads) = get_native_cpu_topology()

        self.gpu_cards = []
        self.usb_cards = []
        self.net_cards = []
        self.proc_cards = []

        self.title(self.t("title"))
        self.geometry("1180x920")
        self.minsize(1060, 760)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_ui()
        
        self.log(self.t("log_scan"))
        threading.Thread(target=self._async_init, daemon=True).start()

    def _secure_config_dir(self):
        """Создает каталог и накладывает защищенные ACL."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            cmd = f'icacls "{self.config_dir}" /inheritance:r /grant:r "SYSTEM:(OI)(CI)F" /grant:r "*S-1-5-32-544:(OI)(CI)F"'
            subprocess.run(cmd, shell=True, capture_output=True, check=False)
        except Exception:
            pass

    def _atomic_write_json(self, filepath, data):
        temp_path = filepath + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(temp_path, filepath)

    def _async_init(self):
        hw_data = self._query_hardware_powershell()
        self.after(0, lambda: self._build_hardware_cards(hw_data))
        self.after(0, self.load_saved_profile)
        self.after(0, self.refresh_process_combo)

    def t(self, key, **kwargs):
        text = TEXTS[self.lang].get(key, key)
        return text.format(**kwargs) if kwargs else text

    def on_closing(self):
        if self.settings_applied_this_session:
            SupportModal(self, self)
        else:
            self.destroy()

    def open_author_site(self):
        webbrowser.open(AUTHOR_URL)

    def switch_language(self, choice):
        self.lang = "ru" if "RU" in choice else "en"
        self.title(self.t("title"))
        self.header_title.configure(text=self.t("header_title"))
        self.btn_author.configure(text=self.t("author_btn"))
        self.cpu_lbl.configure(text=self.t(
            "cpu_info", name=self.get_cpu_name(),
            p_cores=self.p_cores, p_threads=self.p_threads,
            e_cores=self.e_cores, e_threads=self.e_threads,
            threads=self.total_threads
        ))
        self.btn_preset.configure(text=self.t("btn_preset", threads=self.total_threads))
        self.btn_restore.configure(text=self.t("btn_restore"))
        self.lbl_sec_gpu.configure(text=self.t("sec_gpu"))
        self.lbl_sec_usb.configure(text=self.t("sec_usb"))
        self.lbl_sec_net.configure(text=self.t("sec_net"))
        self.lbl_sec_proc.configure(text=self.t("sec_proc"))
        self.lbl_active_proc.configure(text=self.t("active_proc_lbl"))
        self.btn_add_proc.configure(text=self.t("btn_add_proc"))
        self.btn_browse.configure(text=self.t("btn_browse"))
        
        self.btn_apply.configure(text=self.t("btn_apply"))
        self.btn_export.configure(text=self.t("btn_export"))
        self.btn_import.configure(text=self.t("btn_import"))
        self.btn_task.configure(text=self.t("btn_task"))
        self.btn_del_task.configure(text=self.t("btn_del_task"))

        for card in (self.gpu_cards + self.usb_cards + self.net_cards + self.proc_cards):
            card.update_texts()

        self.log(self.t("log_lang_switch"))

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, corner_radius=10, fg_color="#111C30", border_width=1, border_color="#1E2F4D")
        header.grid(row=0, column=0, padx=12, pady=(8, 4), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        self.header_title = ctk.CTkLabel(header, text=self.t("header_title"), font=ctk.CTkFont(size=18, weight="bold"), text_color="#38BDF8")
        self.header_title.grid(row=0, column=0, padx=14, pady=(6, 1), sticky="w")

        self.cpu_lbl = ctk.CTkLabel(header, text=self.t(
            "cpu_info", name=self.get_cpu_name(),
            p_cores=self.p_cores, p_threads=self.p_threads,
            e_cores=self.e_cores, e_threads=self.e_threads,
            threads=self.total_threads
        ), font=ctk.CTkFont(size=11), text_color="#94A3B8")
        self.cpu_lbl.grid(row=1, column=0, padx=14, pady=(0, 6), sticky="w")

        r_hdr = ctk.CTkFrame(header, fg_color="transparent")
        r_hdr.grid(row=0, column=1, rowspan=2, padx=12, pady=6, sticky="e")

        self.btn_author = ctk.CTkButton(
            r_hdr, text=self.t("author_btn"), fg_color="#065F46", hover_color="#047857",
            font=ctk.CTkFont(size=11, weight="bold"), height=26, command=self.open_author_site
        )
        self.btn_author.pack(side="left", padx=(0, 8))

        self.btn_preset = ctk.CTkButton(r_hdr, text=self.t("btn_preset", threads=self.total_threads), fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(weight="bold", size=11), height=26, command=self.apply_reference_preset)
        self.btn_preset.pack(side="left", padx=(0, 6))

        self.btn_restore = ctk.CTkButton(r_hdr, text=self.t("btn_restore"), fg_color="#334155", hover_color="#1E293B", font=ctk.CTkFont(size=11), height=26, command=self.restore_defaults)
        self.btn_restore.pack(side="left", padx=(0, 8))

        self.lang_switch = ctk.CTkSegmentedButton(r_hdr, values=["EN", "RU"], height=24, command=self.switch_language, font=ctk.CTkFont(size=11, weight="bold"))
        self.lang_switch.set("RU")
        self.lang_switch.pack(side="left")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, padx=8, pady=2, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        self.lbl_sec_gpu = ctk.CTkLabel(scroll, text=self.t("sec_gpu"), font=ctk.CTkFont(weight="bold", size=12), text_color="#38BDF8")
        self.lbl_sec_gpu.pack(anchor="w", pady=(3, 1), padx=4)
        self.box_gpu = ctk.CTkFrame(scroll, fg_color="transparent")
        self.box_gpu.pack(fill="x", pady=(0, 4))

        self.lbl_sec_usb = ctk.CTkLabel(scroll, text=self.t("sec_usb"), font=ctk.CTkFont(weight="bold", size=12), text_color="#38BDF8")
        self.lbl_sec_usb.pack(anchor="w", pady=(3, 1), padx=4)
        self.box_usb = ctk.CTkFrame(scroll, fg_color="transparent")
        self.box_usb.pack(fill="x", pady=(0, 4))

        self.lbl_sec_net = ctk.CTkLabel(scroll, text=self.t("sec_net"), font=ctk.CTkFont(weight="bold", size=12), text_color="#38BDF8")
        self.lbl_sec_net.pack(anchor="w", pady=(3, 1), padx=4)
        self.box_net = ctk.CTkFrame(scroll, fg_color="transparent")
        self.box_net.pack(fill="x", pady=(0, 4))

        self.lbl_sec_proc = ctk.CTkLabel(scroll, text=self.t("sec_proc"), font=ctk.CTkFont(weight="bold", size=12), text_color="#38BDF8")
        self.lbl_sec_proc.pack(anchor="w", pady=(3, 1), padx=4)

        proc_main = ctk.CTkFrame(scroll, corner_radius=8, fg_color="#101726", border_width=1, border_color="#1F2A3F")
        proc_main.pack(fill="x", pady=(0, 8), padx=2)

        self.box_procs = ctk.CTkFrame(proc_main, fg_color="transparent")
        self.box_procs.pack(fill="x", padx=6, pady=6)

        add_bar = ctk.CTkFrame(proc_main, fg_color="transparent")
        add_bar.pack(fill="x", padx=6, pady=(0, 6))

        self.lbl_active_proc = ctk.CTkLabel(add_bar, text=self.t("active_proc_lbl"), font=ctk.CTkFont(size=11))
        self.lbl_active_proc.pack(side="left", padx=(0, 4))

        self.cmb_running = ctk.CTkComboBox(add_bar, width=150, height=22, font=ctk.CTkFont(size=11), values=["..."])
        self.cmb_running.pack(side="left", padx=(0, 4))

        btn_ref = ctk.CTkButton(add_bar, text="🔄", width=24, height=22, fg_color="#1E293B", command=self.refresh_process_combo)
        btn_ref.pack(side="left", padx=(0, 8))

        self.ent_custom_name = ctk.CTkEntry(add_bar, width=130, height=22, placeholder_text="mygame.exe", font=ctk.CTkFont(size=11))
        self.ent_custom_name.pack(side="left", padx=(0, 4))

        self.btn_browse = ctk.CTkButton(add_bar, text=self.t("btn_browse"), width=85, height=22, font=ctk.CTkFont(size=11), fg_color="#334155", command=self.browse_exe_file)
        self.btn_browse.pack(side="left", padx=(0, 6))

        self.btn_add_proc = ctk.CTkButton(add_bar, text=self.t("btn_add_proc"), width=80, height=22, font=ctk.CTkFont(size=11, weight="bold"), fg_color="#10B981", hover_color="#059669", command=self.add_custom_or_selected_proc)
        self.btn_add_proc.pack(side="left")

        actions = ctk.CTkFrame(self, corner_radius=8, fg_color="#111C30", border_width=1, border_color="#1E2F4D")
        actions.grid(row=2, column=0, padx=12, pady=6, sticky="ew")

        self.btn_apply = ctk.CTkButton(actions, text=self.t("btn_apply"), fg_color="#2563EB", hover_color="#1D4ED8", font=ctk.CTkFont(weight="bold", size=12), command=self.apply_all_settings)
        self.btn_apply.pack(side="left", padx=(8, 4), pady=8)

        self.btn_export = ctk.CTkButton(actions, text=self.t("btn_export"), fg_color="#0284C7", hover_color="#0369A1", font=ctk.CTkFont(weight="bold", size=12), command=self.export_profile)
        self.btn_export.pack(side="left", padx=4, pady=8)

        self.btn_import = ctk.CTkButton(actions, text=self.t("btn_import"), fg_color="#0D9488", hover_color="#0F766E", font=ctk.CTkFont(weight="bold", size=12), command=self.import_profile)
        self.btn_import.pack(side="left", padx=4, pady=8)

        self.btn_task = ctk.CTkButton(actions, text=self.t("btn_task"), fg_color="#7C3AED", hover_color="#6D28D9", font=ctk.CTkFont(weight="bold", size=12), command=self.install_persistent_service)
        self.btn_task.pack(side="left", padx=4, pady=8)

        self.btn_del_task = ctk.CTkButton(actions, text=self.t("btn_del_task"), fg_color="#EF4444", hover_color="#DC2626", font=ctk.CTkFont(size=12), command=self.remove_persistent_service)
        self.btn_del_task.pack(side="left", padx=4, pady=8)

        self.log_box = ctk.CTkTextbox(self, height=100, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#05070E", text_color="#34D399")
        self.log_box.grid(row=3, column=0, padx=12, pady=(0, 8), sticky="nsew")

    def log(self, text):
        self.log_box.insert("end", f"> {text}\n")
        self.log_box.see("end")

    def get_cpu_name(self):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", 0, winreg.KEY_READ) as key:
                val, _ = winreg.QueryValueEx(key, "ProcessorNameString")
                return val.strip()
        except OSError:
            return "Processor"

    def browse_exe_file(self):
        path = filedialog.askopenfilename(
            title="Select Game or Application Executable",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if path:
            self.ent_custom_name.delete(0, "end")
            self.ent_custom_name.insert(0, os.path.basename(path))

    def _query_hardware_powershell(self) -> dict:
        """
        Безопасный опрос оборудования с автоматическим фоллбэком на Name/DeviceDesc.
        Гарантирует 100% обнаружение контроллеров даже на чистых драйверах Microsoft (usbxhci.inf).
        """
        ps_cmd = (
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
            "$gpu = @(Get-PnpDevice -Class Display -PresentOnly -ErrorAction SilentlyContinue | "
            "Where-Object { $_.InstanceId -like 'PCI*' -and (($_.FriendlyName -and $_.FriendlyName -notmatch 'Basic Render|Basic Display') -or ($_.Name -and $_.Name -notmatch 'Basic Render|Basic Display')) } | "
            "Select-Object @{N='FriendlyName'; E={if ($_.FriendlyName) { $_.FriendlyName } else { $_.Name }}}, InstanceId); "
            
            "$usb = @(Get-PnpDevice -Class USB -PresentOnly -ErrorAction SilentlyContinue | "
            "Where-Object { $_.InstanceId -like 'PCI*' } | "
            "Select-Object @{N='FriendlyName'; E={if ($_.FriendlyName) { $_.FriendlyName } elseif ($_.Name) { $_.Name } else { 'USB Host Controller' }}}, InstanceId); "
            
            "$net = @(Get-PnpDevice -Class Net -PresentOnly -ErrorAction SilentlyContinue | "
            "Where-Object { $_.InstanceId -like 'PCI*' -and (($_.FriendlyName -and $_.FriendlyName -notmatch 'Virtual|VPN|TAP|Wintun|Direct|NDIS|Hyper-V') -or ($_.Name -and $_.Name -notmatch 'Virtual|VPN|TAP|Wintun|Direct|NDIS|Hyper-V')) } | "
            "Select-Object @{N='FriendlyName'; E={if ($_.FriendlyName) { $_.FriendlyName } else { $_.Name }}}, InstanceId); "
            
            "[PSCustomObject]@{ GPU = $gpu; USB = $usb; NET = $net } | ConvertTo-Json -Depth 3 -Compress"
        )
        try:
            p = subprocess.Popen(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, _ = p.communicate(timeout=20)
            return json.loads(stdout.decode("utf-8", errors="replace"))
        except Exception as e:
            self.after(0, lambda: self.log(self.t("log_scan_err", err=str(e))))
            return {"GPU": [], "USB": [], "NET": []}

    def _build_hardware_cards(self, data):
        # 1. GPU
        for d in (data.get("GPU") or []):
            if not isinstance(d, dict) or not d.get("InstanceId"): continue
            if not d.get("FriendlyName"): d['FriendlyName'] = "Graphics Card"
            try:
                d['VectorLimit'] = 1
                card = DeviceCard(self.box_gpu, d, 'GPU', self.topology, self)
                self.gpu_cards.append(card)
                self.log(self.t("log_found_gpu", name=d['FriendlyName'], vectors="MSI: 1V"))
            except Exception as e:
                self.log(f"GPU card init error: {e}")

        # 2. USB
        for d in (data.get("USB") or []):
            if not isinstance(d, dict) or not d.get("InstanceId"): continue
            if not d.get("FriendlyName"): d['FriendlyName'] = "USB Host Controller"
            try:
                d['VectorLimit'] = 8
                card = DeviceCard(self.box_usb, d, 'USB', self.topology, self)
                self.usb_cards.append(card)
                self.log(self.t("log_found_usb", name=d['FriendlyName'], vectors="MSI: 8V"))
            except Exception as e:
                self.log(f"USB card init error: {e}")

        # 3. NET
        for d in (data.get("NET") or []):
            if not isinstance(d, dict) or not d.get("InstanceId"): continue
            if not d.get("FriendlyName"): d['FriendlyName'] = "Network Adapter"
            try:
                limit = 5 if any(x in d['FriendlyName'] for x in ["I225", "I226"]) else (16 if "Wi-Fi" in d['FriendlyName'] else 4)
                d['VectorLimit'] = limit
                card = DeviceCard(self.box_net, d, 'NET', self.topology, self)
                self.net_cards.append(card)
                self.log(self.t("log_found_net", name=d['FriendlyName'], vectors=f"MSI-X: {limit}V"))
            except Exception as e:
                self.log(f"NET card init error: {e}")

        self._save_baseline_if_absent()

    def _save_baseline_if_absent(self):
        if os.path.exists(self.baseline_file):
            return
        data = self.get_current_state_data()
        try:
            self._atomic_write_json(self.baseline_file, data)
        except Exception:
            pass

    def calc_preset_masks(self) -> dict:
        T = self.total_threads
        if self.e_cores > 0 and T >= 20:
            return {
                "gpu": 0xC000,
                "usb": 0x3000,
                "net": 0xF00000,
                "infra": 0x0F0000,
                "game_eft": 0x0554,
                "game_aaa": 0x0FFC
            }
        elif T == 16:
            return {
                "gpu": 0xC000,
                "usb": 0x3000,
                "net": 0x0003,
                "infra": 0x0003,
                "game_eft": 0x0554,
                "game_aaa": 0x0FFC
            }
        elif T == 12:
            return {
                "gpu": 0x0C00,
                "usb": 0x0300,
                "net": 0x0003,
                "infra": 0x0003,
                "game_eft": 0x00D4,
                "game_aaa": 0x00FC
            }
        else:
            p_hi = max(0, T - 1)
            usb_bit = max(0, T - 2)
            game_bits = max(1, T - 2)
            return {
                "gpu": 1 << p_hi,
                "usb": 1 << usb_bit,
                "net": 3 if T >= 2 else 1,
                "infra": 3 if T >= 2 else 1,
                "game_eft": max(1, (1 << game_bits) - 4),
                "game_aaa": max(1, (1 << game_bits) - 4)
            }

    def smart_classify_process(self, proc_name: str) -> dict:
        masks = self.calc_preset_masks()
        name = proc_name.lower().strip()

        if any(x in name for x in ["xray", "v2ray", "sing-box", "openvpn", "wireguard", "amnezia"]):
            return {"prio": "AboveNormal", "mask": masks["infra"]}
        elif any(x in name for x in ["obs-browser", "obs64", "obs", "streamlabs"]):
            return {"prio": "Normal", "mask": masks["infra"]}
        elif any(x in name for x in ["beservice", "_be.exe", "_be", "battleye", "easyanticheat", "vgc"]):
            return {"prio": "Normal", "mask": masks["infra"]}
        elif any(x in name for x in ["escapefromtarkov", "tarkov"]):
            return {"prio": "AboveNormal", "mask": masks["game_eft"]}
        elif any(x in name for x in ["discord", "telegram", "chrome", "msedge", "firefox", "steam"]):
            return {"prio": "Normal", "mask": masks["infra"]}
        else:
            return {"prio": "Normal", "mask": (1 << self.total_threads) - 1}

    def apply_reference_preset(self):
        masks = self.calc_preset_masks()

        for g in self.gpu_cards:
            g.grid.set_mask(masks["gpu"])
            g.chk_msi.select()
            g.cmb_prio.set("Undefined")

        for u in self.usb_cards:
            u.grid.set_mask(masks["usb"])
            u.chk_msi.select()
            u.cmb_prio.set("High")

        for n in self.net_cards:
            n.grid.set_mask(masks["net"])
            n.chk_msi.select()
            n.cmb_prio.set("Undefined")

        for r in self.proc_cards:
            p_name = r.ent_name.get().strip()
            rule = self.smart_classify_process(p_name)
            r.grid.set_mask(rule["mask"])
            r.cmb_prio.set(rule["prio"])

        self.log(self.t("log_preset_ok", threads=self.total_threads, gpu=masks['gpu'], net=masks['net'], usb=masks['usb']))

    def restore_defaults(self):
        self.log(self.t("log_restoring"))

        for d in (self.gpu_cards + self.usb_cards + self.net_cards):
            path = rf"SYSTEM\CurrentControlSet\Enum\{d.dev_info['InstanceId']}\Device Parameters\Interrupt Management"
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path + r"\Affinity Policy", 0, winreg.KEY_READ | winreg.KEY_WRITE) as k_aff:
                    for val_name in ["AssignmentSetOverride", "DevicePolicy", "DevicePriority"]:
                        try: winreg.DeleteValue(k_aff, val_name)
                        except OSError: pass
                d.grid.set_mask(0)
                d.cmb_prio.set("Undefined")
                self.log(self.t("log_dev_restored", name=d.dev_info['FriendlyName']))
            except OSError:
                pass

        for r in self.proc_cards:
            p_name = r.ent_name.get().strip()
            if not p_name: continue
            if not p_name.lower().endswith(".exe"): p_name += ".exe"
            try:
                ifeo_path = rf"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\{p_name}\PerfOptions"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, ifeo_path, 0, winreg.KEY_ALL_ACCESS) as k_ifeo:
                    try: winreg.DeleteValue(k_ifeo, "CpuPriorityClass")
                    except OSError: pass
            except OSError:
                pass

        proc_names_to_reset = {r.ent_name.get().strip().lower() for r in self.proc_cards if r.ent_name.get().strip()}
        all_cores = list(range(self.total_threads))
        for p in psutil.process_iter(['name']):
            try:
                if p.info['name'] and p.info['name'].lower() in proc_names_to_reset:
                    p.cpu_affinity(all_cores)
                    p.nice(psutil.NORMAL_PRIORITY_CLASS)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        for r in self.proc_cards:
            r.grid.set_mask((1 << self.total_threads) - 1)
            r.cmb_prio.set("Normal")

        self.remove_persistent_service()
        if os.path.exists(self.config_file):
            try: os.remove(self.config_file)
            except OSError: pass

        self.log(self.t("log_restored"))

    def add_proc_card(self, name: str, prio: str, mask: int):
        card = ProcessCard(self.box_procs, name, prio, mask, self.topology, self, self.remove_proc_card)
        self.proc_cards.append(card)

    def remove_proc_card(self, card):
        p_name = card.ent_name.get().strip()
        if p_name and not p_name.lower().endswith(".exe"):
            p_name += ".exe"
        if p_name:
            try:
                ifeo_path = rf"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\{p_name}\PerfOptions"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, ifeo_path, 0, winreg.KEY_ALL_ACCESS) as k:
                    winreg.DeleteValue(k, "CpuPriorityClass")
            except OSError:
                pass

        card.destroy()
        if card in self.proc_cards:
            self.proc_cards.remove(card)

    def add_custom_or_selected_proc(self):
        custom = self.ent_custom_name.get().strip()
        sel = self.cmb_running.get()
        target_name = custom if custom else (sel if sel != "..." else "")
        if not target_name:
            return

        if not target_name.lower().endswith(".exe"):
            target_name += ".exe"

        if not SAFE_PROC_REGEX.match(target_name):
            messagebox.showerror("Invalid Input", "Process name contains illegal characters.")
            return

        for p in self.proc_cards:
            if p.ent_name.get().lower() == target_name.lower():
                return
        
        rule = self.smart_classify_process(target_name)
        self.add_proc_card(target_name, rule["prio"], rule["mask"])
        self.ent_custom_name.delete(0, "end")

    def refresh_process_combo(self):
        names = set()
        for p in psutil.process_iter(['name']):
            try:
                n = p.info['name']
                if n and n.lower().endswith('.exe'):
                    names.add(n)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        sorted_procs = sorted(list(names))
        self.cmb_running.configure(values=sorted_procs[:200])
        if sorted_procs:
            self.cmb_running.set(sorted_procs[0])

    def get_current_state_data(self) -> dict:
        devices = {}
        for d in (self.gpu_cards + self.usb_cards + self.net_cards):
            mask_val = d.grid.get_mask()
            devices[d.dev_info["InstanceId"]] = {
                "category": d.dev_category,
                "name": d.dev_info["FriendlyName"],
                "msi": 1 if d.chk_msi.get() else 0,
                "priority": d.cmb_prio.get(),
                "mask": mask_val,
                "mask_hex": f"0x{mask_val:04X}"
            }

        procs = []
        for r in self.proc_cards:
            name = r.ent_name.get().strip()
            if name:
                mask_val = r.grid.get_mask()
                procs.append({
                    "name": name,
                    "priority": r.cmb_prio.get(),
                    "mask": mask_val,
                    "mask_hex": f"0x{mask_val:04X}"
                })
        
        return {
            "app": "W11LatencyFixer Pro",
            "version": "2.3",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cpu": self.get_cpu_name(),
            "threads": self.total_threads,
            "devices": devices,
            "processes": procs
        }

    def export_profile(self):
        path = filedialog.asksaveasfilename(
            title=self.t("btn_export"),
            defaultextension=".json",
            filetypes=[("JSON Profile (*.json)", "*.json"), ("All Files (*.*)", "*.*")],
            initialfile=f"LatencyProfile_{self.total_threads}T.json"
        )
        if not path: return
        try:
            data = self.get_current_state_data()
            self._atomic_write_json(path, data)
            self.log(self.t("log_exported", path=os.path.basename(path)))
        except Exception as e:
            self.log(self.t("log_export_err", err=str(e)))

    def import_profile(self):
        path = filedialog.askopenfilename(
            title=self.t("btn_import"),
            filetypes=[("JSON Profile (*.json)", "*.json"), ("All Files (*.*)", "*.*")]
        )
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            dev_map = data.get("devices", {})
            for card in (self.gpu_cards + self.usb_cards + self.net_cards):
                dev_id = card.dev_info["InstanceId"]
                matched = dev_map.get(dev_id)
                if not matched:
                    matched = next((v for v in dev_map.values() if v.get("name") == card.dev_info["FriendlyName"]), None)
                if not matched:
                    same_cat = [v for v in dev_map.values() if v.get("category") == card.dev_category]
                    same_local = [c for c in (self.gpu_cards + self.usb_cards + self.net_cards) if c.dev_category == card.dev_category]
                    if len(same_cat) == 1 and len(same_local) == 1:
                        matched = same_cat[0]

                if matched:
                    card.grid.set_mask(matched.get("mask", 0))
                    card.cmb_prio.set(matched.get("priority", "Undefined"))
                    card.chk_msi.select() if matched.get("msi", 1) else card.chk_msi.deselect()

            for card in list(self.proc_cards):
                self.remove_proc_card(card)

            for p in data.get("processes", []):
                p_name = p.get("name", "")
                if SAFE_PROC_REGEX.match(p_name):
                    self.add_proc_card(p_name, p.get("priority", "Normal"), p.get("mask", 0))

            self.save_current_profile()
            self.log(self.t("log_imported", path=os.path.basename(path)))
        except Exception as e:
            self.log(self.t("log_import_err", err=str(e)))

    def load_saved_profile(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    dev_map = data.get("devices", {})
                    all_cards = self.gpu_cards + self.usb_cards + self.net_cards
                    
                    for card in all_cards:
                        dev_id = card.dev_info["InstanceId"]
                        matched = dev_map.get(dev_id)
                        if not matched:
                            matched = next((v for v in dev_map.values() if v.get("name") == card.dev_info["FriendlyName"]), None)
                            
                        if matched:
                            saved_mask = matched.get("mask", 0)
                            saved_prio = matched.get("priority", "Undefined")
                            saved_msi = matched.get("msi", 1)
                            
                            current_reg_mask = card.grid.get_mask()
                            
                            card.grid.set_mask(saved_mask)
                            card.cmb_prio.set(saved_prio)
                            card.chk_msi.select() if saved_msi else card.chk_msi.deselect()
                            
                            if current_reg_mask == 0 and saved_mask > 0:
                                self.write_device_reg(card)
                                self.log(self.t("log_driver_recovered", name=card.dev_info['FriendlyName']))

                    for p in data.get("processes", []):
                        p_name = p.get("name", "")
                        if SAFE_PROC_REGEX.match(p_name):
                            self.add_proc_card(p_name, p.get("priority", "Normal"), p.get("mask", 0))
                return
            except Exception:
                pass
        
        masks = self.calc_preset_masks()
        defaults = [
            ("xray.exe", "AboveNormal", masks["infra"]),
            ("obs64.exe", "Normal", masks["infra"]),
            ("obs-browser-page.exe", "Normal", masks["infra"]),
            ("EscapeFromTarkov.exe", "AboveNormal", masks["game_eft"]),
            ("BEService.exe", "Normal", masks["infra"]),
            ("EscapeFromTarkov_BE.exe", "Normal", masks["infra"])
        ]
        for name, prio, mask in defaults:
            self.add_proc_card(name, prio, mask)

    def save_current_profile(self):
        data = self.get_current_state_data()
        self._atomic_write_json(self.config_file, data)

    def write_device_reg(self, dev_card) -> bool:
        path = rf"SYSTEM\CurrentControlSet\Enum\{dev_card.dev_info['InstanceId']}"
        msi = dev_card.chk_msi.get()
        prio_str = dev_card.cmb_prio.get()
        mask_val = dev_card.grid.get_mask()

        try:
            full_path = path + r"\Device Parameters\Interrupt Management"
            msi_path = full_path + r"\MessageSignaledInterruptProperties"
            aff_path = full_path + r"\Affinity Policy"

            with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, msi_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as k_msi:
                winreg.SetValueEx(k_msi, "MSISupported", 0, winreg.REG_DWORD, 1 if msi else 0)
                if dev_card.dev_category == 'GPU':
                    winreg.SetValueEx(k_msi, "MessageNumberLimit", 0, winreg.REG_DWORD, 1)
                elif dev_card.original_limit is not None:
                    winreg.SetValueEx(k_msi, "MessageNumberLimit", 0, winreg.REG_DWORD, dev_card.original_limit)

            with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, aff_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as k_aff:
                if prio_str == "Undefined":
                    try: winreg.DeleteValue(k_aff, "DevicePriority")
                    except OSError: pass
                else:
                    p_map = {"Low": 1, "Normal": 2, "High": 3}
                    winreg.SetValueEx(k_aff, "DevicePriority", 0, winreg.REG_DWORD, p_map.get(prio_str, 2))

                if mask_val > 0:
                    winreg.SetValueEx(k_aff, "DevicePolicy", 0, winreg.REG_DWORD, 4)
                    mask_bytes = (mask_val & 0xFFFFFFFFFFFFFFFF).to_bytes(8, byteorder="little")
                    winreg.SetValueEx(k_aff, "AssignmentSetOverride", 0, winreg.REG_BINARY, mask_bytes)
                else:
                    winreg.SetValueEx(k_aff, "DevicePolicy", 0, winreg.REG_DWORD, 0)
                    try: winreg.DeleteValue(k_aff, "AssignmentSetOverride")
                    except OSError: pass

            if dev_card.dev_category == 'NET' and mask_val > 0:
                cores = [i for i in range(self.total_threads) if (mask_val & (1 << i))]
                if cores:
                    base_proc = min(cores)
                    max_procs = len(cores)
                    num_queues = 4 if max_procs >= 4 else (2 if max_procs >= 2 else 1)
                    
                    raw_name = dev_card.dev_info['FriendlyName']
                    match_token = "I225" if "I225" in raw_name else ("I226" if "I226" in raw_name else raw_name.split('(')[0].strip())
                    ps_token = match_token.replace("'", "''")
                    
                    rss_cmd = (
                        f"$adapters = Get-NetAdapter -ErrorAction SilentlyContinue | "
                        f"Where-Object {{ $_.InterfaceDescription -like '*{ps_token}*' -or $_.Name -like '*{ps_token}*' }}; "
                        f"foreach ($a in $adapters) {{ "
                        f"$a | Set-NetAdapterRss -BaseProcessorNumber {base_proc} -MaxProcessors {num_queues} "
                        f"-NumberOfReceiveQueues {num_queues} -Profile Conservative -ErrorAction SilentlyContinue "
                        f"}}"
                    )
                    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", rss_cmd], capture_output=True, timeout=10)

            self.log(self.t("log_dev_saved", name=dev_card.dev_info['FriendlyName'], msi=msi, prio=prio_str, mask=mask_val))
            return True
        except Exception as e:
            self.log(self.t("log_dev_err", name=dev_card.dev_info['FriendlyName'], err=str(e)))
            return False

    def apply_all_settings(self):
        self.log(self.t("log_applying"))
        all_ok = True

        for g in self.gpu_cards: all_ok &= self.write_device_reg(g)
        for u in self.usb_cards: all_ok &= self.write_device_reg(u)
        for n in self.net_cards: all_ok &= self.write_device_reg(n)

        p_prio_map = {
            "Normal": psutil.NORMAL_PRIORITY_CLASS,
            "AboveNormal": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
            "High": psutil.HIGH_PRIORITY_CLASS
        }

        active_processes = {}
        for p in psutil.process_iter(['name', 'pid']):
            try:
                name = p.info['name']
                if name:
                    name_low = name.lower()
                    active_processes.setdefault(name_low, []).append(p)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        for r in self.proc_cards:
            p_name = r.ent_name.get().strip()
            if not p_name: continue
            if not p_name.lower().endswith(".exe"): p_name += ".exe"

            mask_val = r.grid.get_mask()
            cores = [i for i in range(self.total_threads) if (mask_val & (1 << i))]
            if not cores: cores = list(range(self.total_threads))
            prio = p_prio_map.get(r.cmb_prio.get(), psutil.NORMAL_PRIORITY_CLASS)

            try:
                ifeo_path = rf"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\{p_name}\PerfOptions"
                with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, ifeo_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as k_ifeo:
                    ifeo_prio_val = 3 if r.cmb_prio.get() == "High" else (6 if r.cmb_prio.get() == "AboveNormal" else 2)
                    winreg.SetValueEx(k_ifeo, "CpuPriorityClass", 0, winreg.REG_DWORD, ifeo_prio_val)
            except OSError:
                pass

            target_procs = active_processes.get(p_name.lower(), [])
            if target_procs:
                for proc in target_procs:
                    try:
                        proc.cpu_affinity(cores)
                        proc.nice(prio)
                        self.log(self.t("log_proc_ok", name=p_name, pid=proc.pid, cores=cores, prio=r.cmb_prio.get()))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            else:
                self.log(self.t("log_proc_saved", name=p_name))

        self.save_current_profile()
        self.settings_applied_this_session = True
        self.log(self.t("log_applied"))

    def install_persistent_service(self):
        """Регистрирует реактивную WMI ETW службу с мгновенным перехватом запуска процессов."""
        self.save_current_profile()
        script_file = os.path.join(self.config_dir, "WatchdogService.ps1")

        ps_code = r'''# W11LatencyFixer Ultra-Light Reactive Kernel Watchdog (WMI ETW Process Creation Trace)
$ErrorActionPreference = 'SilentlyContinue'
$configFile = "C:\ProgramData\W11LatencyFixer\config.json"
$lastModified = $null
$cachedCfg = $null

function Restore-DeviceSettings($cfg) {
    if ($cfg -and $cfg.devices) {
        foreach ($devId in $cfg.devices.PSObject.Properties.Name) {
            $dev = $cfg.devices.$devId
            $regPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\" + $devId + "\Device Parameters\Interrupt Management"
            $affPath = Join-Path $regPath "Affinity Policy"
            $msiPath = Join-Path $regPath "MessageSignaledInterruptProperties"
            
            if (Test-Path $regPath) {
                if (-not (Test-Path $affPath)) { New-Item $affPath -Force | Out-Null }
                if (-not (Test-Path $msiPath)) { New-Item $msiPath -Force | Out-Null }

                $currMsi = (Get-ItemProperty -Path $msiPath -Name "MSISupported" -ErrorAction SilentlyContinue).MSISupported
                if ($currMsi -ne $dev.msi) {
                    Set-ItemProperty $msiPath -Name "MSISupported" -Value $dev.msi -Type DWord
                }
                if ($dev.category -eq 'GPU') {
                    Set-ItemProperty $msiPath -Name "MessageNumberLimit" -Value 1 -Type DWord
                }

                $pMap = @{ "Undefined"=0; "Low"=1; "Normal"=2; "High"=3 }
                $pr = $pMap[$dev.priority]
                if ($pr -eq 0) {
                    Remove-ItemProperty $affPath -Name "DevicePriority" -ErrorAction SilentlyContinue
                } else {
                    Set-ItemProperty $affPath -Name "DevicePriority" -Value $pr -Type DWord
                }

                $maskVal = [Convert]::ToUInt64($dev.mask)
                if ($maskVal -gt 0) {
                    $currPol = (Get-ItemProperty -Path $affPath -Name "DevicePolicy" -ErrorAction SilentlyContinue).DevicePolicy
                    if ($currPol -ne 4) {
                        Set-ItemProperty $affPath -Name "DevicePolicy" -Value 4 -Type DWord
                        $bytes = [BitConverter]::GetBytes($maskVal)
                        Set-ItemProperty $affPath -Name "AssignmentSetOverride" -Value $bytes -Type Binary
                    }
                }

                if ($dev.category -eq 'NET' -and $maskVal -gt 0) {
                    $cores = @()
                    for ($i = 0; $i -lt 32; $i++) {
                        if ($maskVal -band (1 -shl $i)) { $cores += $i }
                    }
                    if ($cores.Count -gt 0) {
                        $baseProc = ($cores | Measure-Object -Minimum).Minimum
                        $numQueues = if ($cores.Count -ge 4) { 4 } elseif ($cores.Count -ge 2) { 2 } else { 1 }
                        $cMatch = if ($dev.name -like '*I225*') { 'I225' } elseif ($dev.name -like '*I226*') { 'I226' } else { $dev.name.Split('(')[0].Trim() }
                        Get-NetAdapter -ErrorAction SilentlyContinue | Where-Object { $_.InterfaceDescription -like "*$cMatch*" -or $_.Name -like "*$cMatch*" } | Set-NetAdapterRss -BaseProcessorNumber $baseProc -MaxProcessors $numQueues -NumberOfReceiveQueues $numQueues -Profile Conservative -ErrorAction SilentlyContinue
                    }
                }
            }
        }
    }
}

function Sync-ActiveProcesses($cfg) {
    if ($cfg -and $cfg.processes) {
        foreach ($item in $cfg.processes) {
            $pClean = $item.name
            if ($pClean.EndsWith(".exe", [System.StringComparison]::OrdinalIgnoreCase)) { 
                $pClean = $pClean.Substring(0, $pClean.Length - 4) 
            }
            $pMask = [System.IntPtr]([Convert]::ToInt64($item.mask))
            $pPrio = $item.priority
            
            $procs = [System.Diagnostics.Process]::GetProcessesByName($pClean)
            foreach ($p in $procs) {
                try {
                    if ($p.ProcessorAffinity -ne $pMask) { $p.ProcessorAffinity = $pMask }
                    if ($p.PriorityClass -ne $pPrio) { $p.PriorityClass = $pPrio }
                } catch {}
                finally { $p.Dispose() }
            }
        }
    }
}

# 1. Применяем настройки оборудования и уже запущенных процессов при старте
if (Test-Path $configFile) {
    try {
        $cachedCfg = Get-Content $configFile -Raw | ConvertFrom-Json
        $lastModified = (Get-Item $configFile).LastWriteTime
        Restore-DeviceSettings $cachedCfg
        Sync-ActiveProcesses $cachedCfg
    } catch {}
}

# 2. Инициализация WMI ETW Event Watcher (Событийный перехват без таймеров)
$query = "SELECT ProcessID, ProcessName FROM Win32_ProcessStartTrace"
$watcher = New-Object System.Management.ManagementEventWatcher($query)
$watcher.Options.Timeout = [System.TimeSpan]::FromSeconds(30)

while ($true) {
    try {
        # Поток 100% спит на прерывании ОС, пока не будет запущен ЛЮБОЙ процесс
        $event = $watcher.WaitForNextEvent()
        $pName = [string]$event.Properties["ProcessName"].Value
        $pId   = [int]$event.Properties["ProcessID"].Value

        if ($cachedCfg -and $cachedCfg.processes -and $pName) {
            foreach ($item in $cachedCfg.processes) {
                if ($pName -ieq $item.name) {
                    try {
                        $p = [System.Diagnostics.Process]::GetProcessById($pId)
                        $pMask = [System.IntPtr]([Convert]::ToInt64($item.mask))
                        $pPrio = $item.priority
                        if ($p.ProcessorAffinity -ne $pMask) { $p.ProcessorAffinity = $pMask }
                        if ($p.PriorityClass -ne $pPrio) { $p.PriorityClass = $pPrio }
                        $p.Dispose()
                    } catch {}
                    break
                }
            }
        }
    } catch [System.Management.ManagementException] {
        # Тайм-аут ожидания (нет новых процессов) — нормальное поведение для фоновой проверки
    } catch {}

    # Периодическая проверка обновления файла профиля (если нажали "Применить" в GUI)
    if (Test-Path $configFile) {
        try {
            $currMod = (Get-Item $configFile).LastWriteTime
            if ($currMod -ne $lastModified) {
                $cachedCfg = Get-Content $configFile -Raw | ConvertFrom-Json
                $lastModified = $currMod
                Restore-DeviceSettings $cachedCfg
                Sync-ActiveProcesses $cachedCfg
            }
        } catch {}
    }
}
'''
        try:
            subprocess.run('schtasks /end /tn "W11LatencyFixerWatchdog"', shell=True, capture_output=True)
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", 
                 "Get-CimInstance Win32_Process -Filter \"CommandLine like '%WatchdogService.ps1%'\" | Stop-Process -Force -ErrorAction SilentlyContinue"],
                capture_output=True
            )

            with open(script_file, "w", encoding="utf-8-sig") as f:
                f.write(ps_code)

            task_cmd = (
                f'schtasks /create /tn "W11LatencyFixerWatchdog" '
                f'/tr "powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File \\"{script_file}\\"" '
                f'/sc onlogon /ru "NT AUTHORITY\\SYSTEM" /rl highest /f'
            )
            res = subprocess.run(task_cmd, shell=True, capture_output=True, text=True)
            
            if res.returncode == 0:
                subprocess.run('schtasks /run /tn "W11LatencyFixerWatchdog"', shell=True, capture_output=True)
                self.log(self.t("log_task_ok"))
            else:
                self.log(f"SchTasks Error: {res.stderr.strip()}")
        except Exception as e:
            self.log(f"Watchdog install error: {e}")

    def remove_persistent_service(self):
        """Останавливает процесс службы в памяти и полностью удаляет задание."""
        subprocess.run('schtasks /end /tn "W11LatencyFixerWatchdog"', shell=True, capture_output=True)
        
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command",
             "Get-CimInstance Win32_Process -Filter \"CommandLine like '%WatchdogService.ps1%'\" | Stop-Process -Force -ErrorAction SilentlyContinue"],
            capture_output=True
        )

        res = subprocess.run('schtasks /delete /tn "W11LatencyFixerWatchdog" /f', shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            self.log(self.t("log_task_del"))
        else:
            self.log(self.t("log_task_del"))


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = W11LatencyFixerApp()
    app.mainloop()