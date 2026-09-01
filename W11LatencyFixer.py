import os
import sys
import ctypes
import json
import subprocess
import winreg
import webbrowser

# 1. Запрос прав Администратора (UAC Elevation)
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# 2. Автоустановка необходимых библиотек
for module_name, pip_name in [("customtkinter", "customtkinter"), ("psutil", "psutil")]:
    try:
        __import__(module_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

import customtkinter as ctk
import psutil

# 3. Словарь локализации (RU / EN)
TEXTS = {
    "ru": {
        "title": "W11LatencyFixer — Менеджер прерываний и задержек",
        "header_title": "⚡ W11LATENCYFIXER",
        "cpu_info": "{name}  |  Физических ядер: {cores}  |  Логических потоков: {threads}",
        "btn_preset": "🚀 Автопресет ({threads}T)",
        "btn_restore": "🔄 Сброс на дефолт Windows",
        "sec_gpu": "🎮 ВИДЕОКАРТЫ (GPU)",
        "sec_usb": "🔌 USB-ХОСТ КОНТРОЛЛЕРЫ",
        "sec_net": "🌐 СЕТЕВЫЕ АДАПТЕРЫ (ETHERNET / WI-FI)",
        "sec_proc": "⚙️ ПРОЦЕССЫ И ПРИЛОЖЕНИЯ",
        "msi_mode": "Режим MSI",
        "priority": "Приоритет:",
        "mask_default": "0x0000 [Авто Windows]",
        "mask_custom": "0x{mask:04X} [{count}T]",
        "btn_apply": "⚡ Применить настройки сейчас",
        "btn_task": "💾 Создать автозапуск (навсегда)",
        "btn_del_task": "❌ Удалить автозапуск",
        "btn_add_proc": "➕ Добавить процесс",
        "active_proc_lbl": "Активный процесс:",
        
        # Модальное окно при выходе
        "modal_title": "Поддержка проекта",
        "modal_header": "💖 W11LatencyFixer — Бесплатный проект",
        "modal_desc": "Программа полностью бесплатна. Если она помогла оптимизировать вашу систему, снизить задержки и сделать игры плавнее, вы можете поддержать автора на сайте:",
        "modal_btn_site": "🌐 Перейти на сайт (1va1ne.github.io)",
        "modal_btn_exit": "Выход",
        "modal_btn_cancel": "Отмена",
        
        # Логи
        "log_scan": "Считывание конфигурации оборудования и реестра...",
        "log_found_gpu": "Найдена видеокарта: {name}",
        "log_found_usb": "Найден USB контроллер: {name}",
        "log_found_net": "Найден сетевой адаптер: {name}",
        "log_scan_err": "Ошибка сканирования оборудования: {err}",
        "log_preset_ok": "Применен адаптивный пресет для {threads}T: GPU=0x{gpu:04X}, NET=0x{net:04X}, USB=0x{usb:04X}.",
        "log_restoring": "--- ВОССТАНОВЛЕНИЕ ЗАВОДСКИХ НАСТРОЕК WINDOWS ---",
        "log_dev_restored": "[{name}] Сброшен к стандартной маршрутизации.",
        "log_restored": "Все оверрайды удалены. Восстановлена стандартная маршрутизация Windows.",
        "log_applying": "--- ПРИМЕНЕНИЕ НАСТРОЕК В РЕЕСТР И ПРОЦЕССЫ ---",
        "log_dev_saved": "[{name}] Сохранено: MSI={msi}, Prio={prio}, Mask=0x{mask:04X}",
        "log_dev_err": "[{name}] Ошибка записи реестра: {err}",
        "log_proc_ok": "Процесс '{name}' (PID: {pid}) -> Ядра: {cores}, Приоритет: {prio}",
        "log_proc_not_running": "Процесс '{name}' сейчас не запущен (параметры сохранены для автозапуска).",
        "log_applied": "Все настройки успешно сохранены и применены (RSS синхронизирован)!",
        "log_task_ok": "✅ Служба автоприменения успешно зарегистрирована в Планировщике задач!",
        "log_task_del": "❌ Служба автоприменения удалена из системы.",
        "log_lang_switch": "Язык интерфейса изменен на Русский."
    },
    "en": {
        "title": "W11LatencyFixer — Interrupt & Latency Tuner",
        "header_title": "⚡ W11LATENCYFIXER",
        "cpu_info": "{name}  |  Cores: {cores}  |  Threads: {threads}",
        "btn_preset": "🚀 Auto Preset ({threads}T)",
        "btn_restore": "🔄 Restore Windows Defaults",
        "sec_gpu": "🎮 GRAPHICS CARDS (GPU)",
        "sec_usb": "🔌 USB HOST CONTROLLERS",
        "sec_net": "🌐 NETWORK ADAPTERS (ETHERNET / WI-FI)",
        "sec_proc": "⚙️ APPLICATIONS & PROCESSES",
        "msi_mode": "MSI Mode",
        "priority": "Priority:",
        "mask_default": "0x0000 [Windows Default]",
        "mask_custom": "0x{mask:04X} [{count}T]",
        "btn_apply": "⚡ Apply Settings Now",
        "btn_task": "💾 Install Auto-Apply Service",
        "btn_del_task": "❌ Delete Service",
        "btn_add_proc": "➕ Add Process",
        "active_proc_lbl": "Running Process:",
        
        # Exit Modal
        "modal_title": "Support the Project",
        "modal_header": "💖 W11LatencyFixer is Free Software",
        "modal_desc": "This tool is completely free and open. If it helped optimize your system latency and frame pacing, you can support the developer at:",
        "modal_btn_site": "🌐 Visit Website (1va1ne.github.io)",
        "modal_btn_exit": "Exit",
        "modal_btn_cancel": "Cancel",
        
        # Logs
        "log_scan": "Scanning hardware and reading registry configuration...",
        "log_found_gpu": "GPU detected: {name}",
        "log_found_usb": "USB controller detected: {name}",
        "log_found_net": "Network adapter detected: {name}",
        "log_scan_err": "Hardware scan error: {err}",
        "log_preset_ok": "Applied adaptive preset for {threads}T: GPU=0x{gpu:04X}, NET=0x{net:04X}, USB=0x{usb:04X}.",
        "log_restoring": "--- RESTORING WINDOWS DEFAULT SETTINGS ---",
        "log_dev_restored": "[{name}] Restored to Windows default routing.",
        "log_restored": "All overrides removed. Windows default routing restored.",
        "log_applying": "--- APPLYING SETTINGS TO REGISTRY & PROCESSES ---",
        "log_dev_saved": "[{name}] Saved: MSI={msi}, Priority={prio}, Mask=0x{mask:04X}",
        "log_dev_err": "[{name}] Registry write error: {err}",
        "log_proc_ok": "Process '{name}' (PID: {pid}) -> Cores: {cores}, Priority: {prio}",
        "log_proc_not_running": "Process '{name}' is not running (saved for auto-start).",
        "log_applied": "All settings written safely (RSS synchronized)!",
        "log_task_ok": "✅ Persistent service registered in Task Scheduler!",
        "log_task_del": "❌ Persistent service removed.",
        "log_lang_switch": "Interface language switched to English."
    }
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CoreUnitCapsule(ctk.CTkFrame):
    """Индивидуальная капсула физического ядра с динамической изумрудной каймой"""
    def __init__(self, parent, core_idx, t1, t2, cpu_count, on_change_callback):
        super().__init__(
            parent, 
            fg_color="#090E17", 
            corner_radius=6, 
            border_width=1, 
            border_color="#1E293B"
        )
        self.core_idx = core_idx
        self.t1 = t1
        self.t2 = t2
        self.cpu_count = cpu_count
        self.on_change = on_change_callback

        # Заголовок капсулы (CORE 0, CORE 1...)
        self.lbl_header = ctk.CTkLabel(
            self, 
            text=f"CORE {core_idx}", 
            font=ctk.CTkFont(size=9, weight="bold"), 
            text_color="#64748B"
        )
        self.lbl_header.pack(fill="x", padx=4, pady=(3, 1))

        # Контейнер для чекбоксов потоков
        box_row = ctk.CTkFrame(self, fg_color="transparent")
        box_row.pack(fill="x", padx=4, pady=(0, 4))

        self.cb1 = None
        self.cb2 = None

        if self.t1 < self.cpu_count:
            self.cb1 = ctk.CTkCheckBox(
                box_row,
                text=f"{self.t1}(P)",
                width=0,
                text_color="#F8FAFC",
                font=ctk.CTkFont(size=10, weight="bold"),
                checkbox_width=16,
                checkbox_height=16,
                corner_radius=4,
                border_width=2,
                border_color="#475569",
                fg_color="#10B981",
                hover_color="#059669",
                command=self._handle_click
            )
            self.cb1.pack(side="left", padx=(1, 3))

        if self.t2 < self.cpu_count:
            self.cb2 = ctk.CTkCheckBox(
                box_row,
                text=f"{self.t2}(H)",
                width=0,
                text_color="#94A3B8",
                font=ctk.CTkFont(size=10),
                checkbox_width=16,
                checkbox_height=16,
                corner_radius=4,
                border_width=2,
                border_color="#475569",
                fg_color="#10B981",
                hover_color="#059669",
                command=self._handle_click
            )
            self.cb2.pack(side="left", padx=(1, 2))

    def _handle_click(self):
        self.update_visual_state()
        if self.on_change:
            self.on_change()

    def update_visual_state(self):
        c1 = self.cb1.get() == 1 if self.cb1 else False
        c2 = self.cb2.get() == 1 if self.cb2 else False

        if c1 and c2:
            # Оба потока выбраны: яркая изумрудная кайма и легкий изумрудный фон
            self.configure(border_color="#10B981", fg_color="#062419")
            self.lbl_header.configure(text_color="#34D399")
        elif c1 or c2:
            # Выбран один поток: изумрудная кайма
            self.configure(border_color="#059669", fg_color="#09141F")
            self.lbl_header.configure(text_color="#38BDF8")
        else:
            # Не выбрано: спокойный нейтральный темный вид
            self.configure(border_color="#1E293B", fg_color="#090E17")
            self.lbl_header.configure(text_color="#64748B")

    def get_state(self):
        return (
            self.cb1.get() == 1 if self.cb1 else False,
            self.cb2.get() == 1 if self.cb2 else False
        )

    def set_state(self, p_state, ht_state):
        if self.cb1:
            self.cb1.select() if p_state else self.cb1.deselect()
        if self.cb2:
            self.cb2.select() if ht_state else self.cb2.deselect()
        self.update_visual_state()


class CoreCapsuleGrid(ctk.CTkFrame):
    """Сетка ядер с адаптивной группировкой"""
    def __init__(self, parent, cpu_count, on_change_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.cpu_count = cpu_count
        self.on_change = on_change_callback
        self.capsules = []

        num_cores = (cpu_count + 1) // 2

        for core_idx in range(num_cores):
            t1 = core_idx * 2
            t2 = t1 + 1
            cap = CoreUnitCapsule(self, core_idx, t1, t2, self.cpu_count, self._capsule_changed)
            cap.pack(side="left", padx=2, pady=1)
            self.capsules.append(cap)

    def _capsule_changed(self):
        if self.on_change:
            self.on_change(self.get_mask())

    def get_mask(self):
        mask = 0
        for cap in self.capsules:
            p_on, ht_on = cap.get_state()
            if p_on and cap.t1 < self.cpu_count:
                mask |= (1 << cap.t1)
            if ht_on and cap.t2 < self.cpu_count:
                mask |= (1 << cap.t2)
        return mask

    def set_mask(self, mask):
        for cap in self.capsules:
            p_on = bool(mask & (1 << cap.t1)) if cap.t1 < self.cpu_count else False
            ht_on = bool(mask & (1 << cap.t2)) if cap.t2 < self.cpu_count else False
            cap.set_state(p_on, ht_on)
        if self.on_change:
            self.on_change(self.get_mask())


class DeviceCard(ctk.CTkFrame):
    """3-ярусная карточка устройства с защитой MSI-X"""
    def __init__(self, parent, dev_info, dev_category, cpu_count, app):
        super().__init__(parent, corner_radius=8, fg_color="#131C2E", border_width=1, border_color="#24334C")
        self.app = app
        self.dev_info = dev_info
        self.dev_category = dev_category
        self.cpu_count = cpu_count
        self.original_limit = None
        self.pack(fill="x", pady=4, padx=2)

        # 1-й ЭТАЖ: Заголовок + Бейдж статуса
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=10, pady=(8, 2))

        self.lbl_title = ctk.CTkLabel(hdr, text=dev_info['FriendlyName'], font=ctk.CTkFont(weight="bold", size=13), text_color="#F8FAFC", anchor="w")
        self.lbl_title.pack(side="left")

        self.lbl_id = ctk.CTkLabel(hdr, text=f"[{dev_info['InstanceId']}]", font=ctk.CTkFont(size=10), text_color="#64748B", anchor="w")
        self.lbl_id.pack(side="left", padx=(6, 0))

        self.badge_mask = ctk.CTkLabel(
            hdr, text="", font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#064E3B", text_color="#34D399", corner_radius=5, padx=8, pady=2
        )
        self.badge_mask.pack(side="right")

        # 2-й ЭТАЖ: Панель настроек (MSI + Priority)
        ctrl_bar = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_bar.pack(fill="x", padx=10, pady=(2, 4))

        self.chk_msi = ctk.CTkCheckBox(
            ctrl_bar, text=self.app.t("msi_mode"), font=ctk.CTkFont(size=11), width=0, 
            checkbox_width=15, checkbox_height=15, fg_color="#10B981", hover_color="#059669"
        )
        self.chk_msi.pack(side="left", padx=(0, 16))

        self.lbl_prio = ctk.CTkLabel(ctrl_bar, text=self.app.t("priority"), font=ctk.CTkFont(size=11))
        self.lbl_prio.pack(side="left", padx=(0, 4))
        
        self.cmb_prio = ctk.CTkComboBox(ctrl_bar, width=110, height=22, font=ctk.CTkFont(size=11), values=["Undefined", "Low", "Normal", "High"])
        self.cmb_prio.pack(side="left")

        # 3-й ЭТАЖ: Сетка ядер
        core_box = ctk.CTkFrame(self, fg_color="transparent")
        core_box.pack(fill="x", padx=10, pady=(2, 8))

        self.grid = CoreCapsuleGrid(core_box, self.cpu_count, self._on_mask_update)
        self.grid.pack(anchor="w")

        self.read_real_state()

    def update_texts(self):
        self.chk_msi.configure(text=self.app.t("msi_mode"))
        self.lbl_prio.configure(text=self.app.t("priority"))
        self._on_mask_update(self.grid.get_mask())

    def _on_mask_update(self, mask):
        if mask == 0:
            self.badge_mask.configure(text=self.app.t("mask_default"), fg_color="#1E293B", text_color="#94A3B8")
        else:
            cnt = bin(mask).count("1")
            self.badge_mask.configure(text=self.app.t("mask_custom", mask=mask, count=cnt), fg_color="#064E3B", text_color="#34D399")

    def read_real_state(self):
        path = r"SYSTEM\CurrentControlSet\Enum\\" + self.dev_info["InstanceId"] + r"\Device Parameters\Interrupt Management"
        
        msi_on = False
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path + r"\MessageSignaledInterruptProperties")
            val, _ = winreg.QueryValueEx(k, "MSISupported")
            msi_on = (val == 1)
            try:
                self.original_limit, _ = winreg.QueryValueEx(k, "MessageNumberLimit")
            except: pass
            winreg.CloseKey(k)
        except: pass
        self.chk_msi.select() if msi_on else self.chk_msi.deselect()

        prio_str = "Undefined"
        mask_val = 0
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path + r"\Affinity Policy")
            try:
                p_val, _ = winreg.QueryValueEx(k, "DevicePriority")
                p_map = {0: "Undefined", 1: "Low", 2: "Normal", 3: "High"}
                prio_str = p_map.get(p_val, "Undefined")
            except: pass
            try:
                pol, _ = winreg.QueryValueEx(k, "DevicePolicy")
                if pol == 4:
                    b_val, _ = winreg.QueryValueEx(k, "AssignmentSetOverride")
                    mask_val = int.from_bytes(b_val, byteorder="little")
            except: pass
            winreg.CloseKey(k)
        except: pass

        self.cmb_prio.set(prio_str)
        self.grid.set_mask(mask_val)


class ProcessCard(ctk.CTkFrame):
    """Карточка процесса"""
    def __init__(self, parent, proc_name, default_prio, default_mask, cpu_count, app, on_delete):
        super().__init__(parent, corner_radius=6, fg_color="#0E1626", border_width=1, border_color="#1E2B40")
        self.app = app
        self.cpu_count = cpu_count
        self.pack(fill="x", pady=3, padx=2)

        # 1-й ЭТАЖ: Имя + Приоритет + Бейдж + Кнопка удаления
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=8, pady=(6, 2))

        self.ent_name = ctk.CTkEntry(top, width=130, height=22, font=ctk.CTkFont(size=11, weight="bold"))
        self.ent_name.insert(0, proc_name)
        self.ent_name.pack(side="left", padx=(0, 8))

        self.lbl_prio = ctk.CTkLabel(top, text=self.app.t("priority"), font=ctk.CTkFont(size=11))
        self.lbl_prio.pack(side="left", padx=(0, 4))

        self.cmb_prio = ctk.CTkComboBox(top, width=110, height=22, font=ctk.CTkFont(size=11), values=["Normal", "AboveNormal", "High"])
        self.cmb_prio.set(default_prio)
        self.cmb_prio.pack(side="left", padx=(0, 10))

        self.badge_mask = ctk.CTkLabel(
            top, text="", font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#064E3B", text_color="#34D399", corner_radius=5, padx=8, pady=2
        )
        self.badge_mask.pack(side="left")

        btn_del = ctk.CTkButton(top, text="✕", width=22, height=22, fg_color="#EF4444", hover_color="#DC2626", font=ctk.CTkFont(size=11, weight="bold"), command=lambda: on_delete(self))
        btn_del.pack(side="right")

        # 2-й ЭТАЖ: Сетка ядер
        core_box = ctk.CTkFrame(self, fg_color="transparent")
        core_box.pack(fill="x", padx=8, pady=(2, 6))

        self.grid = CoreCapsuleGrid(core_box, self.cpu_count, self._on_mask_update)
        self.grid.pack(anchor="w")

        self.grid.set_mask(default_mask)
        self.read_real_process_state(proc_name)

    def update_texts(self):
        self.lbl_prio.configure(text=self.app.t("priority"))
        self._on_mask_update(self.grid.get_mask())

    def _on_mask_update(self, mask):
        if mask == 0 or mask == (1 << self.cpu_count) - 1:
            self.badge_mask.configure(text=self.app.t("mask_default"), fg_color="#1E293B", text_color="#94A3B8")
        else:
            cnt = bin(mask).count("1")
            self.badge_mask.configure(text=self.app.t("mask_custom", mask=mask, count=cnt), fg_color="#064E3B", text_color="#34D399")

    def read_real_process_state(self, proc_name):
        clean = proc_name.lower()
        for p in psutil.process_iter(['name', 'pid']):
            try:
                if p.info['name'] and clean in p.info['name'].lower():
                    aff = p.cpu_affinity()
                    mask = sum((1 << c) for c in aff)
                    self.grid.set_mask(mask)
                    nice = p.nice()
                    if nice == psutil.HIGH_PRIORITY_CLASS: self.cmb_prio.set("High")
                    elif nice == psutil.ABOVE_NORMAL_PRIORITY_CLASS: self.cmb_prio.set("AboveNormal")
                    elif nice == psutil.NORMAL_PRIORITY_CLASS: self.cmb_prio.set("Normal")
                    break
            except: pass


class SupportModal(ctk.CTkToplevel):
    """Красивое модальное окно поддержки при закрытии программы"""
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title(self.app.t("modal_title"))
        self.geometry("520x260")
        self.resizable(False, False)
        self.configure(fg_color="#0F172A")
        
        # Центрирование поверх родительского окна
        self.transient(parent)
        self.grab_set()

        # Заголовок
        lbl_hdr = ctk.CTkLabel(
            self, 
            text=self.app.t("modal_header"), 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color="#38BDF8"
        )
        lbl_hdr.pack(padx=20, pady=(20, 8))

        # Описание
        lbl_desc = ctk.CTkLabel(
            self, 
            text=self.app.t("modal_desc"), 
            font=ctk.CTkFont(size=12), 
            text_color="#CBD5E1", 
            wraplength=460, 
            justify="center"
        )
        lbl_desc.pack(padx=20, pady=(0, 15))

        # Кнопка перехода на сайт
        btn_site = ctk.CTkButton(
            self, 
            text=self.app.t("modal_btn_site"), 
            font=ctk.CTkFont(size=13, weight="bold"), 
            fg_color="#10B981", 
            hover_color="#059669", 
            height=32, 
            command=self._open_site
        )
        btn_site.pack(padx=20, pady=(0, 15), fill="x")

        # Кнопки действия (Выход / Отмена)
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 10))

        btn_exit = ctk.CTkButton(
            btn_row, 
            text=self.app.t("modal_btn_exit"), 
            fg_color="#EF4444", 
            hover_color="#DC2626", 
            width=120, 
            command=self._do_exit
        )
        btn_exit.pack(side="left")

        btn_cancel = ctk.CTkButton(
            btn_row, 
            text=self.app.t("modal_btn_cancel"), 
            fg_color="#334155", 
            hover_color="#1E293B", 
            width=120, 
            command=self.destroy
        )
        btn_cancel.pack(side="right")

    def _open_site(self):
        webbrowser.open("https://1va1ne.github.io")

    def _do_exit(self):
        self.destroy()
        self.app.destroy()


class W11LatencyFixerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.lang = "ru"
        self.cpu_count = os.cpu_count() or 16
        self.num_cores = (self.cpu_count + 1) // 2

        self.gpu_cards = []
        self.usb_cards = []
        self.net_cards = []
        self.proc_cards = []

        self.title(self.t("title"))
        self.geometry("1100x880")
        self.minsize(980, 750)

        # Перехват закрытия окна крестиком
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_ui()
        self.scan_hardware()
        self.refresh_process_combo()

    def t(self, key, **kwargs):
        text = TEXTS[self.lang].get(key, key)
        return text.format(**kwargs) if kwargs else text

    def on_closing(self):
        SupportModal(self, self)

    def switch_language(self, choice):
        self.lang = "ru" if "RU" in choice else "en"
        self.title(self.t("title"))
        self.header_title.configure(text=self.t("header_title"))
        self.cpu_lbl.configure(text=self.t("cpu_info", name=self.get_cpu_name(), cores=self.num_cores, threads=self.cpu_count))
        self.btn_preset.configure(text=self.t("btn_preset", threads=self.cpu_count))
        self.btn_restore.configure(text=self.t("btn_restore"))

        self.lbl_sec_gpu.configure(text=self.t("sec_gpu"))
        self.lbl_sec_usb.configure(text=self.t("sec_usb"))
        self.lbl_sec_net.configure(text=self.t("sec_net"))
        self.lbl_sec_proc.configure(text=self.t("sec_proc"))

        self.lbl_active_proc.configure(text=self.t("active_proc_lbl"))
        self.btn_add_proc.configure(text=self.t("btn_add_proc"))

        self.btn_apply.configure(text=self.t("btn_apply"))
        self.btn_task.configure(text=self.t("btn_task"))
        self.btn_del_task.configure(text=self.t("btn_del_task"))

        for card in (self.gpu_cards + self.usb_cards + self.net_cards + self.proc_cards):
            card.update_texts()

        self.log(self.t("log_lang_switch"))

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ХЕДЕР
        header = ctk.CTkFrame(self, corner_radius=8, fg_color="#131C2E", border_width=1, border_color="#24334C")
        header.grid(row=0, column=0, padx=12, pady=6, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        self.header_title = ctk.CTkLabel(header, text=self.t("header_title"), font=ctk.CTkFont(size=18, weight="bold"), text_color="#38BDF8")
        self.header_title.grid(row=0, column=0, padx=12, pady=(6, 1), sticky="w")

        self.cpu_lbl = ctk.CTkLabel(header, text=self.t("cpu_info", name=self.get_cpu_name(), cores=self.num_cores, threads=self.cpu_count), font=ctk.CTkFont(size=11), text_color="#94A3B8")
        self.cpu_lbl.grid(row=1, column=0, padx=12, pady=(0, 6), sticky="w")

        r_hdr = ctk.CTkFrame(header, fg_color="transparent")
        r_hdr.grid(row=0, column=1, rowspan=2, padx=12, pady=6, sticky="e")

        self.btn_preset = ctk.CTkButton(r_hdr, text=self.t("btn_preset", threads=self.cpu_count), fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(weight="bold", size=11), command=self.apply_smart_adaptive_preset)
        self.btn_preset.pack(side="left", padx=(0, 6))

        self.btn_restore = ctk.CTkButton(r_hdr, text=self.t("btn_restore"), fg_color="#475569", hover_color="#334155", font=ctk.CTkFont(size=11), command=self.restore_defaults)
        self.btn_restore.pack(side="left", padx=(0, 8))

        self.lang_switch = ctk.CTkSegmentedButton(r_hdr, values=["RU", "EN"], command=self.switch_language, font=ctk.CTkFont(size=11))
        self.lang_switch.set("RU")
        self.lang_switch.pack(side="left")

        # СКРОЛЛ ОБЛАСТЬ
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, padx=8, pady=2, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # Секции
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

        proc_main = ctk.CTkFrame(scroll, corner_radius=8, fg_color="#131C2E", border_width=1, border_color="#24334C")
        proc_main.pack(fill="x", pady=(0, 8), padx=2)

        self.box_procs = ctk.CTkFrame(proc_main, fg_color="transparent")
        self.box_procs.pack(fill="x", padx=6, pady=6)

        add_bar = ctk.CTkFrame(proc_main, fg_color="transparent")
        add_bar.pack(fill="x", padx=6, pady=(0, 6))

        self.lbl_active_proc = ctk.CTkLabel(add_bar, text=self.t("active_proc_lbl"), font=ctk.CTkFont(size=11))
        self.lbl_active_proc.pack(side="left", padx=(0, 4))

        self.cmb_running = ctk.CTkComboBox(add_bar, width=170, height=22, font=ctk.CTkFont(size=11), values=["..."])
        self.cmb_running.pack(side="left", padx=(0, 6))

        self.btn_add_proc = ctk.CTkButton(add_bar, text=self.t("btn_add_proc"), width=120, height=22, font=ctk.CTkFont(size=11), fg_color="#334155", command=self.add_selected_proc)
        self.btn_add_proc.pack(side="left", padx=(0, 6))

        btn_ref = ctk.CTkButton(add_bar, text="🔄", width=25, height=22, fg_color="#1E293B", command=self.refresh_process_combo)
        btn_ref.pack(side="left")

        # Начальные процессы
        preset_masks = self.calc_preset_masks()
        self.add_proc_card("xray.exe", "AboveNormal", preset_masks["net"])
        self.add_proc_card("obs64.exe", "Normal", preset_masks["net"] | preset_masks["gpu"])

        # ФУТЕР
        actions = ctk.CTkFrame(self, corner_radius=8, fg_color="#131C2E", border_width=1, border_color="#24334C")
        actions.grid(row=2, column=0, padx=12, pady=6, sticky="ew")

        self.btn_apply = ctk.CTkButton(actions, text=self.t("btn_apply"), fg_color="#3B82F6", hover_color="#2563EB", font=ctk.CTkFont(weight="bold", size=12), command=self.apply_all_settings)
        self.btn_apply.pack(side="left", padx=8, pady=8)

        self.btn_task = ctk.CTkButton(actions, text=self.t("btn_task"), fg_color="#8B5CF6", hover_color="#7C3AED", font=ctk.CTkFont(weight="bold", size=12), command=self.install_persistent_service)
        self.btn_task.pack(side="left", padx=8, pady=8)

        self.btn_del_task = ctk.CTkButton(actions, text=self.t("btn_del_task"), fg_color="#EF4444", hover_color="#DC2626", font=ctk.CTkFont(size=12), command=self.remove_persistent_service)
        self.btn_del_task.pack(side="left", padx=8, pady=8)

        self.log_box = ctk.CTkTextbox(self, height=100, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#05070E", text_color="#A7F3D0")
        self.log_box.grid(row=3, column=0, padx=12, pady=(0, 8), sticky="nsew")

    def log(self, text):
        self.log_box.insert("end", f"> {text}\n")
        self.log_box.see("end")

    def get_cpu_name(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            val, _ = winreg.QueryValueEx(key, "ProcessorNameString")
            return val.strip()
        except:
            return "Intel Core Processor"

    def scan_hardware(self):
        self.log(self.t("log_scan"))
        
        ps_cmd = (
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
            "$gpu = Get-PnpDevice -Class Display -PresentOnly | Where-Object { $_.InstanceId -like 'PCI*' } | Select-Object FriendlyName, InstanceId; "
            "$usb = Get-PnpDevice -Class USB -PresentOnly | Where-Object { $_.InstanceId -like 'PCI*' } | Select-Object FriendlyName, InstanceId; "
            "$net = Get-PnpDevice -Class Net -PresentOnly | Where-Object { $_.InstanceId -like 'PCI*' -and $_.FriendlyName -notmatch 'Virtual|VPN|TAP|Wintun|Direct|NDIS' } | Select-Object FriendlyName, InstanceId; "
            "@{ GPU = @($gpu); USB = @($usb); NET = @($net) } | ConvertTo-Json -Depth 3"
        )
        try:
            p = subprocess.Popen(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, _ = p.communicate()
            data = json.loads(stdout.decode("utf-8", errors="replace"))

            for d in data.get("GPU", []):
                self.gpu_cards.append(DeviceCard(self.box_gpu, d, 'GPU', self.cpu_count, self))
                self.log(self.t("log_found_gpu", name=d['FriendlyName']))

            for d in data.get("USB", []):
                self.usb_cards.append(DeviceCard(self.box_usb, d, 'USB', self.cpu_count, self))
                self.log(self.t("log_found_usb", name=d['FriendlyName']))

            for d in data.get("NET", []):
                self.net_cards.append(DeviceCard(self.box_net, d, 'NET', self.cpu_count, self))
                self.log(self.t("log_found_net", name=d['FriendlyName']))

        except Exception as e:
            self.log(self.t("log_scan_err", err=str(e)))

    def calc_preset_masks(self):
        T = self.cpu_count
        if T <= 4: return {"gpu": 1 << 3, "net": 1 << 2, "usb": 1 << 1}
        elif T <= 8: return {"gpu": 0x00C0, "net": 0x0030, "usb": 0x000C}
        elif T <= 12: return {"gpu": 0x0F00, "net": 0x00C0, "usb": 0x0030}
        elif T <= 16: return {"gpu": 0xF000, "net": 0x0C00, "usb": 0x0300}
        else:
            gpu_m = ((1 << 8) - 1) << (T - 8)
            net_m = ((1 << 4) - 1) << (T - 12)
            usb_m = ((1 << 4) - 1) << (T - 16)
            return {"gpu": gpu_m, "net": net_m, "usb": usb_m}

    def apply_smart_adaptive_preset(self):
        masks = self.calc_preset_masks()

        for g in self.gpu_cards:
            g.grid.set_mask(masks["gpu"])
            g.chk_msi.select()
            g.cmb_prio.set("High")

        for u in self.usb_cards:
            u.grid.set_mask(masks["usb"])
            u.chk_msi.select()
            u.cmb_prio.set("High")

        for n in self.net_cards:
            n.grid.set_mask(masks["net"])
            n.chk_msi.select()
            n.cmb_prio.set("High")

        for r in self.proc_cards:
            name = r.ent_name.get().lower()
            if "xray" in name:
                r.grid.set_mask(masks["net"])
                r.cmb_prio.set("AboveNormal")
            elif "obs" in name:
                r.grid.set_mask(masks["net"] | masks["gpu"])
                r.cmb_prio.set("Normal")

        self.log(self.t("log_preset_ok", threads=self.cpu_count, gpu=masks['gpu'], net=masks['net'], usb=masks['usb']))

    def restore_defaults(self):
        self.log(self.t("log_restoring"))
        for d in (self.gpu_cards + self.usb_cards + self.net_cards):
            path = r"SYSTEM\CurrentControlSet\Enum\\" + d.dev_info["InstanceId"] + r"\Device Parameters\Interrupt Management"
            try:
                k_aff = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path + r"\Affinity Policy", 0, winreg.KEY_ALL_ACCESS)
                try: winreg.DeleteValue(k_aff, "AssignmentSetOverride")
                except: pass
                try: winreg.DeleteValue(k_aff, "DevicePolicy")
                except: pass
                try: winreg.DeleteValue(k_aff, "DevicePriority")
                except: pass
                winreg.CloseKey(k_aff)
                d.grid.set_mask(0)
                d.cmb_prio.set("Undefined")
                self.log(self.t("log_dev_restored", name=d.dev_info['FriendlyName']))
            except: pass

        subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-NetAdapterRSS | Set-NetAdapterRss -BaseProcessorNumber 0 -MaxProcessors 4 -NumberOfReceiveQueues 4 -ErrorAction SilentlyContinue"],
            capture_output=True
        )

        all_cores = list(range(self.cpu_count))
        for r in self.proc_cards:
            p_name = r.ent_name.get().strip().lower()
            if not p_name: continue
            for p in psutil.process_iter(['name']):
                try:
                    if p.info['name'] and p_name in p.info['name'].lower():
                        p.cpu_affinity(all_cores)
                        p.nice(psutil.NORMAL_PRIORITY_CLASS)
                except: pass
            r.grid.set_mask(sum(1 << i for i in all_cores))
            r.cmb_prio.set("Normal")

        self.remove_persistent_service()
        self.log(self.t("log_restored"))

    def add_proc_card(self, name, prio, mask):
        card = ProcessCard(self.box_procs, name, prio, mask, self.cpu_count, self, self.remove_proc_card)
        self.proc_cards.append(card)

    def remove_proc_card(self, card):
        card.destroy()
        if card in self.proc_cards:
            self.proc_cards.remove(card)

    def add_selected_proc(self):
        sel = self.cmb_running.get()
        if sel and sel != "...":
            self.add_proc_card(sel, "Normal", (1 << self.cpu_count) - 1)

    def refresh_process_combo(self):
        procs = sorted(list(set(p.info['name'] for p in psutil.process_iter(['name']) if p.info['name'] and p.info['name'].endswith('.exe'))))
        self.cmb_running.configure(values=procs[:150])
        if procs:
            self.cmb_running.set(procs[0])

    def write_device_reg(self, dev_card):
        path = r"SYSTEM\CurrentControlSet\Enum\\" + dev_card.dev_info["InstanceId"]
        msi = dev_card.chk_msi.get()
        prio_str = dev_card.cmb_prio.get()
        mask_val = dev_card.grid.get_mask()

        try:
            full_path = path + r"\Device Parameters\Interrupt Management"
            msi_path = full_path + r"\MessageSignaledInterruptProperties"
            aff_path = full_path + r"\Affinity Policy"

            k_msi = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, msi_path, 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(k_msi, "MSISupported", 0, winreg.REG_DWORD, 1 if msi else 0)
            
            if dev_card.dev_category == 'GPU':
                winreg.SetValueEx(k_msi, "MessageNumberLimit", 0, winreg.REG_DWORD, 1)
            elif dev_card.original_limit is not None:
                winreg.SetValueEx(k_msi, "MessageNumberLimit", 0, winreg.REG_DWORD, dev_card.original_limit)
            winreg.CloseKey(k_msi)

            p_map = {"Undefined": 0, "Low": 1, "Normal": 2, "High": 3}
            mask_bytes = mask_val.to_bytes(8, byteorder="little")

            k_aff = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, aff_path, 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(k_aff, "DevicePriority", 0, winreg.REG_DWORD, p_map.get(prio_str, 0))

            if mask_val > 0:
                winreg.SetValueEx(k_aff, "DevicePolicy", 0, winreg.REG_DWORD, 4)
                winreg.SetValueEx(k_aff, "AssignmentSetOverride", 0, winreg.REG_BINARY, mask_bytes)
            else:
                winreg.SetValueEx(k_aff, "DevicePolicy", 0, winreg.REG_DWORD, 0)
                try: winreg.DeleteValue(k_aff, "AssignmentSetOverride")
                except: pass
            winreg.CloseKey(k_aff)

            if dev_card.dev_category == 'NET' and mask_val > 0:
                cores = [i for i in range(self.cpu_count) if (mask_val & (1 << i))]
                if cores:
                    base_proc = min(cores)
                    max_procs = len(cores)
                    rss_cmd = f"Get-NetAdapter -InterfaceDescription '*{dev_card.dev_info['FriendlyName']}*' -ErrorAction SilentlyContinue | Set-NetAdapterRss -BaseProcessorNumber {base_proc} -MaxProcessors {max_procs} -NumberOfReceiveQueues {max_procs} -Profile Closest -ErrorAction SilentlyContinue"
                    subprocess.run(["powershell", "-NoProfile", "-Command", rss_cmd], capture_output=True)

            self.log(self.t("log_dev_saved", name=dev_card.dev_info['FriendlyName'], msi=msi, prio=prio_str, mask=mask_val))
            return True
        except Exception as e:
            self.log(self.t("log_dev_err", name=dev_card.dev_info['FriendlyName'], err=str(e)))
            return False

    def apply_all_settings(self):
        self.log(self.t("log_applying"))
        for g in self.gpu_cards: self.write_device_reg(g)
        for u in self.usb_cards: self.write_device_reg(u)
        for n in self.net_cards: self.write_device_reg(n)

        p_prio_map = {
            "Normal": psutil.NORMAL_PRIORITY_CLASS,
            "AboveNormal": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
            "High": psutil.HIGH_PRIORITY_CLASS
        }

        for r in self.proc_cards:
            p_name = r.ent_name.get().strip().lower()
            if not p_name: continue
            if not p_name.endswith(".exe"): p_name += ".exe"

            mask_val = r.grid.get_mask()
            cores = [i for i in range(self.cpu_count) if (mask_val & (1 << i))]
            if not cores: cores = list(range(self.cpu_count))
            prio = p_prio_map.get(r.cmb_prio.get(), psutil.NORMAL_PRIORITY_CLASS)

            found = False
            for p in psutil.process_iter(['name', 'pid']):
                try:
                    if p.info['name'] and p.info['name'].lower() == p_name:
                        p.cpu_affinity(cores)
                        p.nice(prio)
                        self.log(self.t("log_proc_ok", name=p_name, pid=p.info['pid'], cores=cores, prio=r.cmb_prio.get()))
                        found = True
                except: pass
            if not found:
                self.log(self.t("log_proc_not_running", name=p_name))

        self.log(self.t("log_applied"))

    def install_persistent_service(self):
        folder = r"C:\ProgramData\W11LatencyFixer"
        os.makedirs(folder, exist_ok=True)
        script_file = os.path.join(folder, "AutoApply.ps1")

        dev_cmds = []
        for d in (self.gpu_cards + self.usb_cards + self.net_cards):
            p = "HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\" + d.dev_info["InstanceId"]
            m = 1 if d.chk_msi.get() else 0
            p_map = {"Undefined": 0, "Low": 1, "Normal": 2, "High": 3}
            pr = p_map.get(d.cmb_prio.get(), 3)
            mask_hex = f"0x{d.grid.get_mask():04X}"
            is_gpu = 1 if d.dev_category == 'GPU' else 0
            dev_cmds.append(f'Set-SafeReg "{p}" {m} {pr} "{mask_hex}" {is_gpu}')

        for n in self.net_cards:
            mask_val = n.grid.get_mask()
            if mask_val > 0:
                cores = [i for i in range(self.cpu_count) if (mask_val & (1 << i))]
                if cores:
                    base_proc = min(cores)
                    max_procs = len(cores)
                    dev_cmds.append(f"Get-NetAdapter -InterfaceDescription '*{n.dev_info['FriendlyName']}*' -ErrorAction SilentlyContinue | Set-NetAdapterRss -BaseProcessorNumber {base_proc} -MaxProcessors {max_procs} -NumberOfReceiveQueues {max_procs} -Profile Closest -ErrorAction SilentlyContinue")

        proc_cmds = []
        for r in self.proc_cards:
            p_name = r.ent_name.get().strip()
            if p_name:
                p_clean = p_name if not p_name.endswith('.exe') else p_name[:-4]
                mask_hex = f"0x{r.grid.get_mask():04X}"
                proc_cmds.append(f"Get-Process -Name '{p_clean}' -ErrorAction SilentlyContinue | ForEach-Object {{ $_.ProcessorAffinity = [IntPtr][Convert]::ToInt64('{mask_hex}', 16); $_.PriorityClass = '{r.cmb_prio.get()}' }}")

        ps_code = f"""
function Set-SafeReg($p, $m, $pr, $hex, $isGpu) {{
    if (Test-Path $p) {{
        $mp = Join-Path $p "Device Parameters\\Interrupt Management\\MessageSignaledInterruptProperties"
        $ap = Join-Path $p "Device Parameters\\Interrupt Management\\Affinity Policy"
        if (-not (Test-Path $mp)) {{ New-Item $mp -Force | Out-Null }}
        if (-not (Test-Path $ap)) {{ New-Item $ap -Force | Out-Null }}
        Set-ItemProperty $mp -Name "MSISupported" -Value $m -Type DWord
        if ($isGpu -eq 1) {{ Set-ItemProperty $mp -Name "MessageNumberLimit" -Value 1 -Type DWord }}
        Set-ItemProperty $ap -Name "DevicePriority" -Value $pr -Type DWord
        $maskVal = [Convert]::ToUInt64($hex, 16)
        if ($maskVal -gt 0) {{
            Set-ItemProperty $ap -Name "DevicePolicy" -Value 4 -Type DWord
            $b = [BitConverter]::GetBytes($maskVal)
            Set-ItemProperty $ap -Name "AssignmentSetOverride" -Value $b -Type Binary
        }} else {{
            Set-ItemProperty $ap -Name "DevicePolicy" -Value 0 -Type DWord
            Remove-ItemProperty $ap -Name "AssignmentSetOverride" -ErrorAction SilentlyContinue
        }}
    }}
}}

{chr(10).join(dev_cmds)}

Start-Sleep -Seconds 15
{chr(10).join(proc_cmds)}
"""
        with open(script_file, "w", encoding="utf-8-sig") as f:
            f.write(ps_code)

        task_cmd = (
            f'schtasks /create /tn "W11LatencyFixerAutoApply" '
            f'/tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File \\"{script_file}\\"" '
            f'/sc onlogon /rl highest /f'
        )
        subprocess.run(task_cmd, shell=True, capture_output=True)
        self.log(self.t("log_task_ok"))

    def remove_persistent_service(self):
        subprocess.run('schtasks /delete /tn "W11LatencyFixerAutoApply" /f', shell=True, capture_output=True)
        self.log(self.t("log_task_del"))

if __name__ == "__main__":
    app = W11LatencyFixerApp()
    app.mainloop()