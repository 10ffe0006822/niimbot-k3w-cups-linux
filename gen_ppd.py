#!/usr/bin/python3 -I
# Generates niimbot-k3w.ppd from labels.conf (install.sh runs this):
#   python3 gen_ppd.py labels.conf > niimbot-k3w.ppd   # install.sh does this itself
#   python3 gen_ppd.py labels.conf --default-name    # PageSize name of the default label
# Per-label shifts go into "*NiimbotLabel" lines that rastertoniimbot reads at print time.
import sys

HEAD_MM = 80                       # print head width, the widest possible label
PT_PER_MM = 72 / 25.4

HEADER = """*PPD-Adobe: "4.3"
*FormatVersion: "4.3"
*FileVersion: "1.2"
*LanguageVersion: English
*LanguageEncoding: ISOLatin1
*PCFileName: "NIIMBOTK3.PPD"
*Manufacturer: "NIIMBOT"
*Product: "(K3_W)"
*ModelName: "NIIMBOT K3W"
*ShortNickName: "NIIMBOT K3_W"
*NickName: "NIIMBOT K3_W (rastertoniimbot)"
*1284DeviceID: "MFG:NIIMBOT;CMD:ESC;MDL:K3_W;"
*PSVersion: "(3010.000) 0"
*LanguageLevel: "3"
*ColorDevice: False
*DefaultColorSpace: Gray
*FileSystem: False
*Throughput: "1"
*LandscapeOrientation: Plus90
*TTRasterizer: Type42
*cupsVersion: 2.4
*cupsModelNumber: 0
*cupsManualCopies: False
*cupsFilter: "application/vnd.cups-raster 0 rastertoniimbot"

*OpenUI *Resolution/Resolution: PickOne
*OrderDependency: 10 AnySetup *Resolution
*DefaultResolution: 203dpi
*Resolution 203dpi/203 DPI: "<</HWResolution[203 203]/cupsBitsPerColor 1/cupsColorSpace 3/cupsColorOrder 0>>setpagedevice"
*CloseUI: *Resolution

*OpenUI *Rotate180/Rotate 180 degrees: Boolean
*OrderDependency: 30 AnySetup *Rotate180
*DefaultRotate180: True
*Rotate180 True/Yes: ""
*Rotate180 False/No: ""
*CloseUI: *Rotate180
"""

def fmt(x):
    return ("%.3f" % x).rstrip("0").rstrip(".")


def die(msg):
    sys.stderr.write("labels.conf: %s\n" % msg)
    sys.exit(1)


def read_labels(path):
    """[(name, label, w_pt, h_pt, right_mm, up_mm)], default first."""
    labels, seen = [], {}
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.replace(",", ".").split()
            if len(parts) not in (2, 4):
                die("строка %d: нужно 2 или 4 числа: ширина высота [вправо вверх]" % n)
            try:
                w, h, right, up = (list(map(float, parts)) + [0, 0])[:4]
            except ValueError:
                die("строка %d: не число: %s" % (n, line))
            if not (3.5 <= w <= HEAD_MM) or not (3.5 <= h <= 1000):
                die("строка %d: ширина 3.5-%d мм, высота 3.5-1000 мм" % (n, HEAD_MM))
            wp, hp = w * PT_PER_MM, h * PT_PER_MM
            name = "w%dh%d" % (round(wp), round(hp))
            if name in seen:
                die("строка %d: размер %sx%s слишком близок к строке %d" % (n, fmt(w), fmt(h), seen[name]))
            seen[name] = n
            labels.append((name, "%s x %s mm" % (fmt(w), fmt(h)), wp, hp, right, up))
    if not labels:
        die("нет ни одной этикетки")
    return labels


def ppd(labels):
    lines = [HEADER]
    lines += ["*% Per-label shift, mm as seen on the label: width_pt height_pt right up"]
    lines += ['*NiimbotLabel %s: "%.2f %.2f %s %s"' % (name, wp, hp, fmt(r), fmt(u))
              for name, _, wp, hp, r, u in labels]
    lines.append("")
    lines += shift_option("ShiftRight", "Extra shift right (mm)", 31)
    lines += shift_option("ShiftUp", "Extra shift up (mm)", 32)
    setpd = '"<</PageSize[%.2f %.2f]/ImagingBBox null>>setpagedevice"'
    default = labels[0][0]
    for kw, ui, value in (
            ("PageSize", "*OpenUI *PageSize/Label size: PickOne\n*OrderDependency: 20 AnySetup *PageSize", setpd),
            ("PageRegion", "*OpenUI *PageRegion: PickOne\n*OrderDependency: 20 AnySetup *PageRegion", setpd),
            ("ImageableArea", None, '"0 0 %.2f %.2f"'),
            ("PaperDimension", None, '"%.2f %.2f"')):
        if ui:
            lines.append(ui)
        lines.append("*Default%s: %s" % (kw, default))
        for name, label, wp, hp, _, _ in labels:
            lines.append("*%s %s/%s: %s" % (kw, name, label, value % (wp, hp)))
        if ui:
            lines.append("*CloseUI: *%s" % kw)
        lines.append("")
    lines.append("*DefaultFont: Courier")
    lines.append('*Font Courier: Standard "(1.05)" Standard ROM')
    return "\n".join(lines)


def shift_option(keyword, title, order):
    """Per-job extra shift, -3..+3 mm in 0.5 mm steps; choices are named m1.5 / 0 / p1.5."""
    lines = ["*OpenUI *%s/%s: PickOne" % (keyword, title),
             "*OrderDependency: %d AnySetup *%s" % (order, keyword),
             "*Default%s: 0" % keyword]
    for i in range(-6, 7):
        mm = i / 2
        name = "0" if i == 0 else ("p" if i > 0 else "m") + fmt(abs(mm))
        lines.append('*%s %s/%+.1f mm: ""' % (keyword, name, mm))
    lines += ["*CloseUI: *%s" % keyword, ""]
    return lines


def main():
    labels = read_labels(sys.argv[1] if len(sys.argv) > 1 else "labels.conf")
    if "--default-name" in sys.argv:
        print(labels[0][0])
    else:
        print(ppd(labels))


if __name__ == "__main__":
    main()
