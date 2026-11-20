#!/usr/bin/env python3
import os, re
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "screenshots")
os.makedirs(OUT, exist_ok=True)

def load_font(size, bold=False):
    cands = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Menlo.ttc",
    ]
    for c in cands:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()

def load_xml(path):
    import xml.etree.ElementTree as ET
    return ET.parse(path).getroot()

def a(sh):
    return {x.get("name"): x.text for x in sh.findall("attribute")}

COL = {
    "lane": (255, 60, 60),
    "road_curb": (255, 153, 0),
    "crosswalk": (0, 200, 90),
    "drivable": (40, 130, 255),
    "traffic_light": (255, 210, 0),
    "traffic_sign": (205, 70, 255),
}

def draw_tag(draw, xy, text, fg, font):
    bb = draw.textbbox((0, 0), text, font=font)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    x, y = xy
    draw.rectangle([x, y, x + w + 6, y + h + 6], fill=(0, 0, 0, 180))
    draw.text((x + 3, y + 2), text, fill=fg, font=font)

def annotate(img_path, xml_root, img_name, out_path, title, zoom=None):
    base = Image.open(img_path).convert("RGBA")
    W, H = base.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    ft = load_font(20, bold=True)
    fs = load_font(17)
    # find image
    node = None
    for im in xml_root.findall(".//image"):
        if im.get("name") == img_name:
            node = im; break
    if node is None:
        raise SystemExit("image not found " + img_name)
    for sh in node:
        lab = sh.get("label")
        if lab == "tag":
            continue
        col = COL.get(lab, (255, 255, 255))
        if sh.tag == "polyline":
            pts = [tuple(map(float, p.split(","))) for p in sh.get("points").split(";")]
            d.line(pts, fill=col + (255,), width=4, joint="curve")
            at = a(sh)
            lbl = f"{lab}:{at.get('position','')}"
            draw_tag(d, (pts[0][0] + 4, pts[0][1] - 24), lbl, col + (255,), fs)
        elif sh.tag == "polygon":
            pts = [tuple(map(float, p.split(","))) for p in sh.get("points").split(";")]
            d.polygon(pts, outline=col + (255,), width=4)
            at = a(sh)
            lbl = f"{lab}:{at.get('area_type','')}" if at else lab
            draw_tag(d, (pts[0][0] + 4, pts[0][1] + 4), lbl, col + (255,), fs)
        elif sh.tag == "box":
            x0, y0 = float(sh.get("xtl")), float(sh.get("ytl"))
            x1, y1 = float(sh.get("xbr")), float(sh.get("ybr"))
            d.rectangle([x0, y0, x1, y1], outline=col + (255,), width=3)
            at = a(sh)
            if lab == "traffic_light":
                lbl = f"light:{at.get('color','')}/{at.get('facing','')}"
            else:
                lbl = f"sign:{at.get('group','')}"
            draw_tag(d, (x0, max(0, y0 - 22)), lbl, col + (255,), load_font(15))
    comp = Image.alpha_composite(base, overlay).convert("RGB")
    draw = ImageDraw.Draw(comp)
    # header bar
    bar = 46
    draw.rectangle([0, 0, W, bar], fill=(28, 28, 30))
    draw.text((16, 12), title, fill=(240, 240, 240), font=load_font(22, bold=True))
    draw.text((W - 250, 16), "Road v1.0 · CVAT for images 1.1", fill=(170, 170, 170), font=load_font(16))
    if zoom:
        zx0, zy0, zx1, zy1, scale = zoom
        crop = comp.crop((zx0, zy0, zx1, zy1))
        crop = crop.resize((int(crop.width * scale), int(crop.height * scale)), Image.LANCZOS)
        # place bottom-right
        px = W - crop.width - 20
        py = H - crop.height - 20
        draw.rectangle([zx0, zy0, zx1, zy1], outline=(255, 255, 0), width=3)
        comp.paste(crop, (px, py))
        draw.rectangle([px - 3, py - 3, px + crop.width + 3, py + crop.height + 3], outline=(255, 255, 0), width=3)
        draw.text((px + 8, py + 6), "zoom ×%g" % scale, fill=(255, 255, 0), font=load_font(18, bold=True))
    comp.save(out_path)
    print("wrote", out_path, comp.size)

def labels_table(out_path):
    W, H = 1100, 980
    im = Image.new("RGB", (W, H), (30, 30, 33))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 54], fill=(45, 62, 120))
    d.text((20, 14), "Project · Labels (Road v1.0)", fill=(255, 255, 255), font=load_font(24, bold=True))
    rows = [
        ("lane", "polyline", "position L1/R1/L2/R2/other · style solid/dashed · color white/yellow/other · kind single/double"),
        ("road_curb", "polyline", "(không thuộc tính)"),
        ("crosswalk", "polygon", "(không thuộc tính)"),
        ("drivable", "polygon", "area_type direct / alternative"),
        ("traffic_light", "rectangle", "color red/yellow/green/off/unknown · type vehicle/pedestrian/beacon · facing front/side/back · edge_zone ☐"),
        ("traffic_sign", "rectangle", "group prohibitory/mandatory/warning/information/supplementary/other · facing front/side/back · edge_zone ☐"),
        ("camera", "tag", "value front / fisheye_front / fisheye_rear / fisheye_left / fisheye_right"),
        ("timeofday", "tag", "value day / dusk / night"),
        ("weather", "tag", "value clear / overcast / rain / fog / other"),
        ("source", "tag", "value real / simulated"),
    ]
    y = 84
    d.text((24, y), "Label", fill=(180, 190, 210), font=load_font(18, bold=True))
    d.text((300, y), "Kiểu", fill=(180, 190, 210), font=load_font(18, bold=True))
    d.text((470, y), "Thuộc tính / giá trị", fill=(180, 190, 210), font=load_font(18, bold=True))
    y += 34
    d.line([20, y, W - 20, y], fill=(80, 80, 90), width=2); y += 16
    for name, typ, at in rows:
        col = COL.get(name, (120, 200, 255))
        d.ellipse([24, y + 6, 44, y + 26], fill=col)
        d.text((58, y), name, fill=(240, 240, 240), font=load_font(20, bold=True))
        tcol = (150, 220, 150) if typ == "tag" else (255, 210, 130)
        d.text((300, y), typ, fill=tcol, font=load_font(19))
        # wrap attr text
        words = at.split(" ")
        line = ""
        yy = y
        for w in words:
            test = (line + " " + w).strip()
            if d.textlength(test, font=load_font(17)) > W - 500:
                d.text((470, yy), line, fill=(205, 205, 205), font=load_font(17)); yy += 22; line = w
            else:
                line = test
        d.text((470, yy), line, fill=(205, 205, 205), font=load_font(17))
        y = max(yy + 30, y + 42)
        d.line([20, y - 8, W - 20, y - 8], fill=(55, 55, 65), width=1)
        y += 6
    im.save(out_path); print("wrote", out_path)

def xml_snippet(out_path):
    import xml.etree.ElementTree as ET
    root = load_xml(os.path.join(ROOT, "screenshots", "_tmp_front.xml"))
    line = None
    for im in root.findall(".//image"):
        for sh in im.findall("polyline"):
            if sh.get("label") == "lane":
                # rebuild a readable line
                at = a(sh)
                line = ('  <polyline label="lane" source="manual" occluded="0" points="%s" z_order="0">'
                        '<attribute name="position">%s</attribute><attribute name="style">%s</attribute>'
                        '<attribute name="color">%s</attribute><attribute name="kind">%s</attribute></polyline>') % (
                            sh.get("points"), at.get("position"), at.get("style"), at.get("color"), at.get("kind"))
                break
        if line: break
    W, H = 1200, 460
    im = Image.new("RGB", (W, H), (30, 30, 33))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 50], fill=(45, 62, 120))
    d.text((20, 12), "annotations.xml — đoạn <polyline label=\"lane\">", fill=(255, 255, 255), font=load_font(22, bold=True))
    # simple syntax coloring
    fm = load_font(17)
    y = 90
    # split into chunks and color tags
    tokens = re.split(r'(<[a-zA-Z/][^>]*>)', line)
    x = 30
    for tk in tokens:
        if tk.startswith("<"):
            # tag name color
            m = re.match(r'(</?)([a-zA-Z0-9_]+)', tk)
            if m:
                d.text((x, y), m.group(1), fill=(120, 200, 255), font=fm)
                x += d.textlength(m.group(1), font=fm)
                d.text((x, y), m.group(2), fill=(230, 140, 255), font=fm)
                x += d.textlength(m.group(2), font=fm)
                rest = tk[m.end():]
                # attrs
                for am in re.finditer(r'([a-zA-Z_]+)=("[^"]*")', rest):
                    pre = rest[:am.start()]
                    if pre:
                        d.text((x, y), pre, fill=(200, 200, 200), font=fm); x += d.textlength(pre, font=fm)
                    d.text((x, y), am.group(1), fill=(255, 210, 130), font=fm); x += d.textlength(am.group(1), font=fm)
                    d.text((x, y), "=", fill=(200, 200, 200), font=fm); x += d.textlength("=", font=fm)
                    d.text((x, y), am.group(2), fill=(150, 230, 150), font=fm); x += d.textlength(am.group(2), font=fm)
                # wrap if too long
                if x > W - 40:
                    y += 30; x = 40
            else:
                d.text((x, y), tk, fill=(200, 200, 200), font=fm); x += d.textlength(tk, font=fm)
        else:
            d.text((x, y), tk, fill=(210, 210, 210), font=fm); x += d.textlength(tk, font=fm)
    # wrap note: the line is long; draw a second wrapped copy manually
    im.save(out_path); print("wrote", out_path)

if __name__ == "__main__":
    # extract front xml to temp for snippet
    import zipfile
    with zipfile.ZipFile(os.path.join(ROOT, "duong-front.zip")) as z:
        open(os.path.join(OUT, "_tmp_front.xml"), "wb").write(z.read("annotations.xml"))
    with zipfile.ZipFile(os.path.join(ROOT, "duong-fisheye.zip")) as z:
        open(os.path.join(OUT, "_tmp_fisheye.xml"), "wb").write(z.read("annotations.xml"))
    fr = load_xml(os.path.join(OUT, "_tmp_front.xml"))
    fe = load_xml(os.path.join(OUT, "_tmp_fisheye.xml"))

    labels_table(os.path.join(OUT, "muc6-1-labels.png"))
    annotate(os.path.join(ROOT, "data", "A08_c0deebc1-16cfa791.jpg"), fr, "A08_c0deebc1-16cfa791.jpg",
             os.path.join(OUT, "muc6-2-front-A08.png"),
             "front · A08 — làn, vùng lái, đèn & biển")
    annotate(os.path.join(ROOT, "data", "B01_02688_FV.png"), fe, "B01_02688_FV.png",
             os.path.join(OUT, "muc6-3-fisheye-B01.png"),
             "fisheye_front · B01 — polyline theo cung",
             zoom=(300, 380, 620, 560, 2.2))
    xml_snippet(os.path.join(OUT, "muc6-4-xml-snippet.png"))
    for t in ("_tmp_front.xml", "_tmp_fisheye.xml"):
        try: os.remove(os.path.join(OUT, t))
        except OSError: pass
    print("DONE")