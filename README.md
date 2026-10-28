# NIIMBOT K3_W — CUPS driver for Linux

[Русский](#русский) · [English](#english)

---

## Русский

Драйвер CUPS для термопринтера этикеток **NIIMBOT K3_W** (USB `3513:0002`).
Официального драйвера под Linux нет — с этим драйвером принтер появляется в системе
как обычный и печатает из любой программы: PDF, браузер, LibreOffice и т.д.

### Возможности
- 26 популярных размеров этикеток (от 30×20 до 80×120 мм), список легко менять
- Отдельные отступы для каждого размера этикетки
- Поворот на 180° (включён по умолчанию)
- Разовая подстройка сдвига в окне печати
- Чёткие штрих-коды, QR-коды и текст, при этом фото и градиенты передаются полутонами: драйвер сам различает эти участки на этикетке
- Без зависимостей — только Python 3 и CUPS

### Установка
```sh
git clone <адрес репозитория>
cd <папка репозитория>
sudo ./install.sh
```
Принтер должен быть подключён по USB. Появится очередь печати `NIIMBOT_K3W`.

Проверка:
```sh
lp -d NIIMBOT_K3W test-43x25.pdf
```

Для настройки сдвигов и зазора есть `test-frame-50x30.pdf` и `test-frame-43x25.pdf`:
три этикетки с рамкой в 1 мм от края и номерами. Рамка должна лечь ровно по каждой этикетке:
```sh
lp -d NIIMBOT_K3W -o PageSize=w142h85 test-frame-50x30.pdf
```

### Размеры и отступы
Все этикетки описаны в `labels.conf`:
```
# ширина  высота  вправо  вверх
43        25      1       1
50        30      0       0
```
- **ширина** — поперёк ленты (максимум 80 мм), **высота** — вдоль ленты;
- **вправо / вверх** — сдвиг печати в мм так, как он виден на готовой этикетке
  (минус — влево / вниз);
- первая строка — размер по умолчанию.

После изменений снова выполните `sudo ./install.sh`.

### Несколько этикеток подряд
Внутри одного задания принтер печатает страницы сплошной лентой и не замечает зазоры
между этикетками. Поэтому настройка «Gap between labels» в окне печати предлагает два режима:
- **Pause after each label** (по умолчанию) — пауза 2 с после каждой этикетки, принтер сам
  находит начало следующей. Работает с любым рулоном, но печатает по одной этикетке;
- **зазор в мм** (1–5 мм) — драйвер сам пропускает зазор, и всё задание печатается одним
  проходом. Зазор должен точно совпадать с рулоном, иначе сдвиг накапливается с каждой этикеткой.

Чтобы зазор стоял по умолчанию: `lpadmin -p NIIMBOT_K3W -o LabelGap=3`.
При повороте на 180° страницы печатаются с последней, чтобы лента читалась сверху вниз.

### Ограничения
- **Открытая крышка** — принтер сам ставит печать на паузу и продолжает, когда крышку закрыть.
- **Кончилась лента** — принтер паузу не ставит: задания, отправленные без ленты,
  считаются напечатанными и теряются. Меняйте рулон заранее и перепечатайте пропавшие этикетки.
- Драйвер не получает от принтера обратной связи о состоянии
- Проверено только на K3_W; другие модели NIIMBOT могут использовать иной протокол

### Как это работает
Принтер сообщает `CMD:ESC` и принимает подмножество ESC/POS через USB-интерфейс
класса Printer (`/dev/usb/lp*`):

| Байты | Назначение |
|---|---|
| `1B 40` | `ESC @` — инициализация |
| `1D 76 30 00 xL xH yL yH …` | `GS v 0` — растр, всегда 80 байт (640 точек) в ширину, бит 1 = чёрный |
| `0C 1B 40` | конец этикетки; завершающий `ESC @` запускает печать |

Текстовые команды ESC/POS принтер игнорирует, «сырой» растр без `GS v 0` — тоже.
Головка 80 мм, 203 dpi; этикетки уже 80 мм стоят по центру головки.

### Файлы
| Файл | Назначение |
|---|---|
| `rastertoniimbot` | CUPS-фильтр: растр CUPS → команды принтера |
| `gen_ppd.py` | генерирует PPD из `labels.conf` |
| `labels.conf` | размеры этикеток и отступы |
| `install.sh` | установка фильтра, PPD и очереди печати |

---

## English

A CUPS driver for the **NIIMBOT K3_W** thermal label printer (USB `3513:0002`).
There is no official Linux driver; with this one the printer shows up as a regular
system printer and prints from any application.

### Features
- 26 common label sizes (30×20 to 80×120 mm), easy to edit
- Per-label-size print offsets
- 180° rotation (on by default)
- Per-job offset tweaks in the print dialog
- Crisp barcodes, QR codes and text while photos and gradients keep their halftones: the driver tells these areas apart on each label
- No dependencies beyond Python 3 and CUPS

### Install
```sh
git clone <repository URL>
cd <repository folder>
sudo ./install.sh
```
The printer must be connected via USB. A `NIIMBOT_K3W` queue is created.

Test:
```sh
lp -d NIIMBOT_K3W test-43x25.pdf
```

To tune shifts and the gap, `test-frame-50x30.pdf` and `test-frame-43x25.pdf` hold three
numbered labels with a frame 1 mm inside the edge; it should sit evenly on every label:
```sh
lp -d NIIMBOT_K3W -o PageSize=w142h85 test-frame-50x30.pdf
```

### Sizes and offsets
All labels are listed in `labels.conf`: width (across the tape, max 80 mm),
height (along the tape), shift right and shift up in mm as seen on the printed label.
The first line is the default size. Run `sudo ./install.sh` again after editing.

### Several labels in a row
Within one job the printer prints pages back to back and ignores the gaps between labels.
The "Gap between labels" print option offers two modes:
- **Pause after each label** (default) — a 2 s pause after each label lets the printer find
  the next one itself. Works with any roll, but prints one label at a time;
- **gap in mm** (1–5 mm) — the driver skips the gap itself and the whole job prints in one go.
  The gap must match the roll exactly, or the offset grows with every label.

To make a gap the default: `lpadmin -p NIIMBOT_K3W -o LabelGap=3`.
With 180° rotation pages print last-first, so the tape reads top to bottom.

### Limitations
- **Cover open** — the printer pauses by itself and resumes once the cover is closed.
- **Out of labels** — the printer does not pause: jobs sent without labels are reported
  as printed and are lost. Replace the roll in time and reprint any missing labels.
- The driver gets no status feedback from the printer
- Tested on the K3_W only; other NIIMBOT models may use a different protocol

### Protocol
The printer reports `CMD:ESC` and accepts a subset of ESC/POS on its USB printer-class
interface (`/dev/usb/lp*`):

| Bytes | Meaning |
|---|---|
| `1B 40` | `ESC @` — init |
| `1D 76 30 00 xL xH yL yH …` | `GS v 0` raster, always 80 bytes (640 dots) wide, bit 1 = black |
| `0C 1B 40` | end of label; the trailing `ESC @` triggers printing |

ESC/POS text commands and raw raster without `GS v 0` are ignored.
80 mm head, 203 dpi; narrower labels sit centred on the head.

---

## Лицензия / License

[MIT](LICENSE)
