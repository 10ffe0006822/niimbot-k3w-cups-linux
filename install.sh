#!/bin/sh
# Install the NIIMBOT K3_W CUPS driver and add the printer queue. Run with sudo.
# Label sizes and shifts come from labels.conf.
set -e
cd "$(dirname "$0")"

QUEUE=NIIMBOT_K3W

PPD_TMP=$(mktemp)
trap 'rm -f "$PPD_TMP"' EXIT
python3 -I gen_ppd.py labels.conf > "$PPD_TMP"
DEFAULT_SIZE=$(python3 -I gen_ppd.py labels.conf --default-name)

install -o root -g root -m 755 rastertoniimbot /usr/lib/cups/filter/rastertoniimbot
install -o root -g root -m 644 -D "$PPD_TMP" /usr/share/cups/model/niimbot/niimbot-k3w.ppd

URI=$(lpinfo --include-schemes usb -v | awk '/NIIMBOT/ {print $2; exit}')
if [ -z "$URI" ]; then
    echo "Принтер NIIMBOT не найден по USB. Проверьте кабель и питание." >&2
    exit 1
fi
echo "Принтер: $URI"

# Extra shifts reset to 0: per-label shifts now live in labels.conf
lpadmin -p "$QUEUE" -E -v "$URI" -P /usr/share/cups/model/niimbot/niimbot-k3w.ppd \
    -D "NIIMBOT K3_W" -o PageSize="$DEFAULT_SIZE" -o print-scaling=fit \
    -o ShiftRight=0 -o ShiftUp=0
cupsenable "$QUEUE"
cupsaccept "$QUEUE"
echo "Готово: принтер $QUEUE добавлен, этикетка по умолчанию $DEFAULT_SIZE."
