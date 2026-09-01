

🇷🇺 Русский вариант (README.md)

⚡ W11LatencyFixer

Низкоуровневый оптимизатор системных задержек, DPC/ISR прерываний и
распределения потоков для Windows 11 / 10.

🎯 Назначение и цель проекта

По умолчанию операционная система Windows сбрасывает практически все аппаратные
прерывания периферийных устройств (видеокарты, сетевой карты, контроллера
USB-мыши) на самое первое ядро процессора — Core 0 (CPU 0). Когда на систему
ложится нагрузка в играх, при стриминге или работе со звуком, планировщик ядра
ОС на Core 0 захлебывается, вызывая микрофризы (stutters), плавающий Input Lag
мыши, скачки 0.1% Low FPS и треск звука (audio dropouts/xruns).

Цель W11LatencyFixer — в автоматическом или ручном режиме безопасно разнести
очереди прерываний ключевых контроллеров по разным физическим ядрам процессора,
перевести шину в режим MSI (Message Signaled Interrupts) и снизить системные
DPC-задержки до рекордных < 150\ \mu\text{s}, освободив первые ядра
исключительно под нужды игрового движка.

⚙️ Как это устроено и работает под капотом

1.  Аппаратное сканирование шины PCIe:
    Утилита сканирует систему и фильтрует весь виртуальный шум (хабы,
    виртуальные коммутаторы), находя только реальные физические контроллеры:
    видеокарту (GPU), USB-хост (xHCI) и сетевые адаптеры (Ethernet / Wi-Fi).
2.  Активация Message Signaled Interrupts (MSI Mode):
    Переводит устройства из устаревшего режима Line-Based IRQ в режим прямого
    доступа MSI/MSI-X, ликвидируя очереди ожидания на шине PCI Express.
3.  Интеллектуальная адаптивная топология (Smart Core Pinning):
    В зависимости от количества ядер вашего процессора (от 4-поточных i3
    до 32-поточных i9/Ryzen 9) программа рассчитывает оптимальную маску
    Affinity:
      - Core 0–3: Остаются стерильно чистыми для главного потока игры и
        планировщика ОС.
      - Core 4: Забирает прерывания USB (мышь 1000–8000 Гц и аудиоинтерфейс).
      - Core 5: Забирает прерывания Сетевого стека.
      - Core 6–7: Забирают прерывания Видеокарты (GPU).
4.  Защита MSI-X и нативный NDIS RSS:
    В отличие от других твикеров, программа не ломает очереди сетевых карт
    (Intel I225-V/I226-V, AX211) принудительным ограничением лимитов, а
    синхронизирует привязку ядер через нативный системный API Set-NetAdapterRss,
    исключая системные сбои (Код 10).
5.  Оптимизация стриминга и процессов (OBS, Xray/VPN):
    Позволяет привязать фоновые программы (OBS Studio, Xray) к тем же ядрам, где
    живет сетевой стек и видеокарта. Это дает выигрыш за счет общего L3-кэша
    процессора и гарантирует, что оверлеи стрима не отберут FPS у игры.
6.  Автономность и самовосстановление (0% фоновой нагрузки):
    Программа не висит в трее и не потребляет оперативную память. Она генерирует
    нативную задачу в Планировщике задач Windows, которая автоматически
    восстанавливает настройки прерываний при перезагрузке и даже после чистой
    переустановки видеодрайверов NVIDIA/AMD.

🛠️ Стек технологий и реализация

  - Язык: Python 3.10+ (компилируется в единый автономный .exe).
  - GUI / Фронтенд: CustomTkinter (современный темный Fluent/Flat интерфейс,
    динамическая адаптивная сетка капсул ядер).
  - Бэкенд: Нативные вызовы winreg, Windows PnP API, NDIS Network API, psutil,
    PowerShell.

============================================


EN English Version (README.md)

⚡ W11LatencyFixer

Low-level hardware interrupt (DPC/ISR), MSI mode, and core affinity tuner for
Windows 11 / 10.

🎯 Purpose & Project Objective

By default, Windows routes almost all hardware interrupts (GPU render fences,
network packets, USB mouse polling) to the very first CPU core — Core 0 (CPU 0).
Under heavy gaming, live-streaming, or digital audio production (DAW) workloads,
Core 0 becomes overwhelmed with interrupt queues, leading to micro-stuttering,
inconsistent mouse input lag, 0.1% low FPS frame drops, and audio buffer
underruns (xruns/clicks).

The goal of W11LatencyFixer is to safely distribute hardware interrupts across
dedicated physical CPU cores, enforce high-priority Message Signaled Interrupts
(MSI/MSI-X), and achieve sub-150\ \mu\text{s} DPC latencies while keeping
primary CPU cores 100% clean for game rendering loops.

⚙️ How It Works (Under the Hood)

1.  Hardware PCIe Scanning:
    Enumerates physical PCIe controllers and filters out virtual root hubs,
    software bridges, and VPN devices, exposing only true actionable
    controllers: GPU, USB xHCI, and Network Adapters (Ethernet / Wi-Fi).
2.  Message Signaled Interrupts (MSI/MSI-X) Activation:
    Transitions devices from legacy Line-Based IRQs to direct DMA MSI mode,
    eliminating PCI bus contention and interrupt sharing penalties.
3.  Adaptive CPU Core Pinning:
    Dynamically calculates mathematical affinity masks tailored to your exact
    CPU thread count (4T up to 32T+):
      - Core 0–3: Kept completely clean for the Game Engine's main render loop
        and OS dispatcher.
      - Core 4: Dedicated to USB interrupts (high-polling mice 1000–8000 Hz and
        USB Audio DACs).
      - Core 5: Dedicated to Network interrupts.
      - Core 6–7: Dedicated to GPU fences, VSync, and NVENC completions.
4.  Safe MSI-X Vectoring & NDIS RSS Synchronization:
    Unlike generic tweakers that crash multi-queue NICs (e.g., Intel
    I225-V/I226-V, Wi-Fi 6E AX211) by forcing invalid message limits,
    W11LatencyFixer preserves native MSI-X hardware limits and synchronizes core
    routing through the official Set-NetAdapterRss API.
5.  Streaming & Process Latency Tuning (OBS / Xray / VPN):
    Enables assigning background processes (e.g., obs64.exe, xray.exe) to
    network/GPU-adjacent cores. This maximizes L3 cache locality while
    preventing streaming overlays from stealing render quantum time from the
    game.
6.  Zero Background Overhead & Driver Update Persistence:
    The application does not run resident background services. It registers a
    lightweight native Windows Scheduled Task that automatically ensures
    interrupt masks and MSI settings remain intact after Windows reboots and GPU
    driver updates.

🛠️ Tech Stack & Architecture

  - Language: Python 3.10+ (bundled into a standalone single-file .exe).
  - GUI: CustomTkinter (Modern Dark Fluent UI with interactive, color-coded Core
    Capsules).
  - System Layer: winreg (Windows Registry API), PnP Device Manager, NDIS 6.x
    RSS Engine, psutil, PowerShell.
