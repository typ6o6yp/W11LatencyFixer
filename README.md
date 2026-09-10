<img width="1374" height="1139" alt="Снимок экрана 2026-09-01 161854" src="https://github.com/user-attachments/assets/ca6777f6-1627-40b8-9088-ec2743f769c4" />

What is this program?

W11LatencyFixer Pro is an advanced, low-level Windows 11/10 latency engine
designed for competitive gamers and power users. Its primary purpose is to
eliminate micro-stutters, minimize input lag, and flatten frametime variance by
reorganizing how the operating system handles CPU cores and hardware interrupts.

The Problem It Solves

By default, Windows does not isolate critical game threads from system hardware:

1.  Interrupt Storms & DPC Latency: Whenever your high-polling gaming mouse
    moves (1000–8000 Hz), your network card receives packets, or your GPU
    completes a frame, they generate hardware interrupts (IRQs). Windows often
    dumps these interrupts onto CPU Core 0 or distributes them chaotically. If
    an interrupt hits a core currently rendering your game, the game thread
    pauses for a split second. You experience this as a micro-stutter, frame
    drop, or "floaty" mouse feel.
2.  Core Contention: Anti-cheats (BattlEye, Easy Anti-Cheat), Discord, streaming
    software (OBS), and background apps constantly fight with the game engine
    for cache and execution time on the exact same CPU cores.

What the Software Actually Does

The program establishes strict core isolation and traffic separation:

1.  Hardware Interrupt (IRQ) Affinity Routing:
      - USB Controllers (Mouse/Keyboard): Pinned to dedicated CPU cores (e.g.,
        Core P6) to guarantee near-instantaneous, queue-free input polling.
      - Graphics Card (GPU): Routed to specific high-end cores (e.g., Core P7),
        isolating the display driver from game logic.
      - Network Adapters (Ethernet / Wi-Fi): Assigned dedicated cores (e.g.,
        Cores P0–P1) synchronized with NDIS RSS (Receive Side Scaling) queues
        for consistent packet delivery.
2.  Enables Low-Latency MSI / MSI-X Mode:
      - Forces hardware controllers into Message Signaled Interrupts (MSI) mode,
        completely bypassing legacy line-based IRQs, resolving IRQ sharing
        conflicts, and reducing DPC/ISR execution time.
3.  Smart Process & Thread Dispatcher:
      - Games are isolated onto dedicated high-performance physical cores with
        elevated priority.
      - Background apps & Anti-Cheats (OBS, browser pages, Discord, VPNs,
        BattlEye) are relegated to separate infrastructure cores, preventing
        them from stealing cache or CPU cycles from the game.
4.  Auto-Recovery Watchdog (Driver-Reset Protection):
      - Installing or updating GPU (NVIDIA/AMD) or NIC (Intel) drivers wipes
        custom registry affinity rules. The built-in ultra-lightweight Watchdog
        service monitors device states and automatically restores your tuned
        masks and MSI modes on the fly.

The End Result:

Crisp and immediate mouse responsiveness, smoother frametimes, higher 1%
and 0.1% Low FPS, and an end to random stuttering during fast-paced in-game
action.

===============================

Universal Rules & Setup Guide for Any Game

3 Golden Rules of Core Allocation:

1.  Hardware (Interrupts / IRQs) — Outer Cores:

      - Network (NIC): Cores P0–P1 (shared with Windows base system timers).
      - USB (Mouse/Keyboard): Second-to-last P-core (e.g., P6). Priority: High.
      - Graphics Card (GPU): Very last P-core (e.g., P7). Priority: Undefined.
      - Always ensure "MSI Mode" is checked.

2.  The Game — Clean Center P-Cores:

      - Assign the game dedicated middle cores (e.g., P1–P5 or P2–P5).
      - Crucial: Never let the game share physical cores with GPU or USB mouse
        interrupts.
      - Priority: AboveNormal (optimal responsiveness; avoid High as it can
        starve audio and input threads).

3.  Background Apps & Anti-Cheats — Isolation Zone:

      - Route Discord, OBS, VPNs, and anti-cheat engines (BEService.exe,
        EasyAntiCheat.exe, vgc.exe) to Cores P0–P1 or to E-cores (on hybrid
        Intel CPUs).
      - Priority: strictly Normal.

Step-by-Step 1-Minute Setup:

1.  Click "🚀 Reference Preset" — the engine will automatically route GPU, USB,
    Network, and base infrastructure to optimal cores.
2.  Click "📁 Browse .exe" and select your game's main executable (or pick it
    from the running processes list).
3.  Click "➕ Add Process".
4.  On your game's card, tick the middle P-cores (uncheck P0, as well as the GPU
    and USB cores) and set the priority to AboveNormal.
5.  Click "⚡ Apply Settings" \to "💾 Install Watchdog" \to Reboot your PC.



<img width="1375" height="603" alt="image" src="https://github.com/user-attachments/assets/1d1d6887-2531-477d-8f5a-993d96303e86" />


Что это за программа?

W11LatencyFixer Pro — это системная утилита для глубокой оптимизации
Windows 11/10, предназначенная для геймеров и киберспортсменов. Её главная цель
— минимизировать задержку ввода (input lag), убрать микрофризы и сделать график
времени кадра (frametime) максимально плавным.

Какую проблему она решает?

В стандартной Windows системные устройства (видеокарта, сетевая карта, USB-порты
мыши) и сторонние программы борются за одни и те же ядра процессора:

1.  Прерывания устройств (IRQ): Когда вы двигаете мышью с высокой частотой
    опроса (1000–8000 Гц) или видеокарта заканчивает рендеринг кадра, они
    отправляют сигнал процессору («аппаратное прерывание»). По умолчанию Windows
    часто сбрасывает эти прерывания на нулевое ядро или размазывает их случайным
    образом, прерывая работу игрового движка. В игре это ощущается как внезапный
    микростаттер или "ватное", неотзывчивое управление.
2.  Конфликт процессов: Античиты (BattlEye, Easy Anti-Cheat), OBS для стриминга,
    Discord и фоновые VPN-сервисы работают на тех же ядрах, что и игра, отбирая
    ресурсы в критические моменты перестрелок.

Что конкретно делает программа?

Программа наводит строгий порядок в распределении ресурсов процессора по
принципу «разделяй и властвуй»:

1.  Изолирует прерывания "железа" на выделенные ядра:
      - Мышь и клавиатура (USB): Направляются на отдельные ядра (например, P6),
        чтобы клики и движения мыши считывались мгновенно без очередей.
      - Видеокарта (GPU): Привязывается к крайним ядрам (например, P7), устраняя
        задержки драйвера дисплея.
      - Сетевая карта (Ethernet/Wi-Fi): Закрепляется за отдельными ядрами
        (например, P0–P1) вместе с настройкой очередей NDIS RSS для стабильного
        пинга.
2.  Переводит устройства в скоростной режим MSI/MSI-X:
      - Включает режим прерываний на основе сообщений (Message Signaled
        Interrupts), полностью исключая задержки устаревших прерываний
        (Line-based IRQ) и конфликты устройств на одной линии.
3.  Разделяет потоки игр и фонового софта:
      - Играм (например, Escape from Tarkov) выделяются чистые физические ядра с
        повышенным приоритетом.
      - Фоновым службам (OBS, браузер, Discord, античит) выделяются служебные
        ядра, чтобы они физически не могли отбирать ресурсы у игрового процесса.
4.  Защищает настройки от сброса драйверами (Watchdog):
      - При каждом обновлении драйверов NVIDIA или Intel Windows стирает
        оптимизации. Встроенная незаметная фоновая служба автоматически
        проверяет реестр и возвращает ваши настройки на место.

Результат для игрока:

Снижение задержки отклика мыши, стабильный 1% и 0.1% Low FPS, устранение
внезапных рывков при резких движениях камеры и стабильная сетевая синхронизация.


==========================


🇷🇺 Универсальные правила и настройка для любой игры

3 Золотых правила распределения ядер:

1.  Железо (Прерывания / IRQ) — по краям:

      - Сетевая карта: Ядра P0–P1 (совместно с системными службами Windows).
      - USB (Мышь/Клавиатура): Предпоследнее P-ядро (например, P6). Приоритет:
        High.
      - Видеокарта (GPU): Последнее P-ядро (например, P7). Приоритет: Undefined.
      - Всегда включайте галочку «Режим MSI».

2.  Сама игра — чистые ядра по центру:

      - Отдайте игре свободные средние ядра (например, P1–P5 или P2–P5).
      - Главное: игра не должна делить ядра с прерываниями USB (мыши) и
        видеокарты.
      - Приоритет: AboveNormal (лучший баланс между отзывчивостью и
        стабильностью; приоритет High ставить не рекомендуется, чтобы игра не
        заглушала аудио- и системные потоки ввода).

3.  Фоновый софт и античиты — в «резервацию»:

      - Discord, OBS, Telegram, VPN, античиты (BEService.exe, EasyAntiCheat.exe,
        vgc.exe) отправляйте на ядра P0–P1 или на E-ядра (если процессор с
        гибридной архитектурой).
      - Приоритет: строго Normal.

Пошаговая настройка за 1 минуту:

1.  Нажмите «🚀 Эталонный пресет» — программа автоматически разнесет видеокарту,
    мышь, сеть и фоновые процессы по правильным ядрам.
2.  В строке добавления процессов нажмите «📁 Обзор .exe» и выберите исполняемый
    файл вашей игры (или выберите его из списка запущенных).
3.  Нажмите «➕ Добавить».
4.  В карточке игры выберите средние P-ядра (снимите галочки с ядер мыши,
    видеокарты и P0), а приоритет переключите на AboveNormal.
5.  Нажмите «⚡ Применить настройки» \to «💾 Включить службу» \to Перезагрузите
    ПК.
