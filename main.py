# VELMARA — The Lantern Harbour
# A travel poster for a place that does not exist.
# Drawn entirely in code with Pillow: no fetched images, no randomness,
# no network. Every coordinate is fixed, so two runs write identical bytes.
#
# Place: Velmara, a harbour town on a floating islet where paper lanterns
# are launched onto the tide every dusk. One landmark: the lighthouse on
# the islet rock, whose beam sweeps the lantern sea.
# Palette: dusk indigo -> teal -> amber horizon; warm gold lantern light.
# Layout (768 x 1024 portrait): name top, moon upper right, lighthouse
# centre-right, lantern sea below, pier silhouette bottom-left, tagline
# at the foot. The eye travels name -> lighthouse -> horizon.

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 768, 1024
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUT_PATH = os.path.join(OUT_DIR, "entry.png")

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, x0, y0, x1, y1, stops):
    """Vertical gradient between (x0,y0)-(x1,y1) through colour stops."""
    n = y1 - y0
    for y in range(n):
        t = y / max(1, n - 1)
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
                draw.line([(x0, y0 + y), (x1, y0 + y)], fill=lerp(c0, c1, f))
                break


def tracked_size(font, text, tracking):
    w = 0
    for ch in text:
        w += font.getbbox(ch)[2] + tracking
    return w - tracking


def draw_tracked(draw, cx, y, text, font, fill, tracking):
    """Draw text centred on cx, with letter tracking, returning its bbox."""
    total = tracked_size(font, text, tracking)
    x = cx - total // 2
    top = None
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        bbox = font.getbbox(ch)
        if top is None:
            top = y + bbox[1]
        x += bbox[2] + tracking
    return (cx - total // 2, top, cx + total // 2, y + font.size)


def soft_disc(layer, cx, cy, r, colour, blur):
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour)
    return layer.filter(ImageFilter.GaussianBlur(blur))


# ---------------------------------------------------------------- sky
img = Image.new("RGB", (W, H), (20, 31, 56))
d = ImageDraw.Draw(img)
SKY_STOPS = [
    (0.00, (16, 26, 50)),
    (0.35, (26, 52, 78)),
    (0.62, (43, 88, 102)),
    (0.85, (146, 110, 74)),
    (1.00, (214, 138, 75)),
]
vgrad(d, 0, 0, W, 560, SKY_STOPS)

# stars: fixed positions, upper sky only
STARS = [
    (52, 40, 2), (120, 90, 1), (180, 46, 2), (250, 110, 1), (320, 60, 2),
    (390, 34, 1), (455, 96, 2), (520, 52, 1), (640, 66, 2), (700, 120, 1),
    (80, 160, 1), (150, 210, 2), (230, 170, 1), (300, 220, 1), (370, 150, 2),
    (660, 200, 2), (720, 60, 1), (40, 260, 1), (680, 260, 1), (500, 140, 1),
    (100, 300, 1), (620, 300, 1), (280, 280, 1), (420, 250, 1),
]
for (sx, sy, sr) in STARS:
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(235, 230, 210))

# moon: pale disc + glow, upper right
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
glow = soft_disc(glow, 630, 262, 66, (255, 214, 150, 90), 26)
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
d = ImageDraw.Draw(img)
d.ellipse([630 - 46, 262 - 46, 630 + 46, 262 + 46], fill=(250, 232, 196))
d.ellipse([616 - 12, 248 - 12, 616 + 12, 248 + 12], fill=(238, 214, 172))
d.ellipse([644 - 8, 278 - 8, 644 + 8, 278 + 8], fill=(238, 214, 172))
d.ellipse([638 - 5, 244 - 5, 638 + 5, 244 + 5], fill=(240, 218, 178))

# distant headlands on the horizon (dark silhouettes)
d.polygon([(0, 560), (0, 500), (90, 516), (170, 492), (250, 528), (300, 560)],
          fill=(24, 42, 60))
d.polygon([(768, 560), (768, 512), (690, 520), (640, 498), (590, 532), (560, 560)],
          fill=(22, 40, 58))

# ---------------------------------------------------------------- sea
SEA_STOPS = [
    (0.00, (34, 74, 88)),
    (0.45, (22, 54, 70)),
    (1.00, (10, 28, 44)),
]
vgrad(d, 0, 560, W, H, SEA_STOPS)

# warm light streaks on the water under the horizon
STREAKS = [
    (120, 596, 260, 3, 60), (330, 620, 180, 2, 48), (520, 600, 210, 3, 56),
    (60, 660, 150, 2, 40), (430, 668, 240, 2, 44), (180, 716, 200, 2, 36),
    (560, 730, 160, 2, 40), (300, 780, 260, 2, 32), (80, 830, 170, 2, 30),
]
for (sx, sy, sl, sh, sa) in STREAKS:
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.rounded_rectangle([sx, sy, sx + sl, sy + sh], radius=sh,
                         fill=(255, 176, 92, sa))
    ov = ov.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(img)

# ---------------------------------------------------------------- islet + lighthouse (the ONE landmark)
# islet rock
d.polygon([(452, 668), (470, 620), (540, 606), (606, 622), (628, 668)],
          fill=(13, 24, 36))
d.polygon([(470, 620), (500, 632), (540, 606), (560, 628)],
          fill=(20, 34, 48))
# tower: tapered, cream with two deep-red bands
d.polygon([(492, 620), (588, 620), (578, 452), (502, 452)], fill=(242, 227, 198))
d.polygon([(490, 580), (590, 580), (586, 548), (494, 548)], fill=(150, 58, 48))
d.polygon([(488, 506), (592, 506), (588, 478), (492, 478)], fill=(150, 58, 48))
d.polygon([(492, 620), (500, 620), (502, 452), (506, 452)], fill=(214, 196, 164))
# gallery + lamp room
d.rectangle([496, 440, 584, 452], fill=(38, 52, 66))
d.rectangle([508, 410, 572, 440], fill=(58, 74, 90))
d.rectangle([516, 418, 564, 436], fill=(255, 214, 130))
d.polygon([(504, 410), (576, 410), (566, 396), (514, 396)], fill=(38, 52, 66))
d.rectangle([538, 388, 542, 396], fill=(38, 52, 66))
# lamp glow
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
glow = soft_disc(glow, 540, 427, 34, (255, 206, 110, 150), 14)
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
d = ImageDraw.Draw(img)
# beams sweeping left and right
for pts, alpha in [([(540, 427), (64, 392), (64, 440)], 30),
                   ([(540, 427), (748, 400), (748, 454)], 26)]:
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).polygon(pts, fill=(255, 214, 130, alpha))
    ov = ov.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(img)

# ---------------------------------------------------------------- lanterns on the water
# (x, y, size) — warm paper lanterns floating on the tide
LANTERNS = [
    (150, 700, 15), (250, 742, 12), (330, 700, 10), (420, 756, 13),
    (640, 700, 12), (700, 756, 15), (96, 800, 11), (210, 830, 14),
    (380, 830, 11), (470, 872, 13), (600, 830, 12), (690, 880, 11),
    (300, 862, 12), (585, 868, 14), (105, 868, 10),
]
for (lx, ly, lr) in LANTERNS:
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse([lx - lr - 6, ly - lr - 6, lx + lr + 6, ly + lr + 6],
               fill=(255, 180, 90, 70))
    ov = ov.filter(ImageFilter.GaussianBlur(5))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(img)
    d.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], fill=(255, 196, 110))
    d.ellipse([lx - lr // 2, ly - lr // 2, lx + lr // 2, ly + lr // 2],
              fill=(255, 226, 160))
    d.line([(lx, ly + lr), (lx, ly + lr + 26)], fill=(255, 176, 92), width=2)
    d.line([(lx - 1, ly + lr + 4), (lx - 1, ly + lr + 22)],
           fill=(255, 200, 120), width=1)

# rising lanterns in the sky
SKY_LANTERNS = [(120, 330, 9), (210, 290, 7), (700, 330, 8), (430, 300, 6),
                (90, 420, 7), (330, 330, 6)]
for (lx, ly, lr) in SKY_LANTERNS:
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse([lx - lr - 5, ly - lr - 5, lx + lr + 5, ly + lr + 5],
               fill=(255, 180, 90, 80))
    ov = ov.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(img)
    d.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], fill=(255, 200, 120))
    d.ellipse([lx - lr // 2, ly - lr // 2, lx + lr // 2, ly + lr // 2],
              fill=(255, 228, 165))

# small rowboat with a lantern, lower left of the lighthouse
d.polygon([(196, 782), (268, 782), (252, 796), (210, 796)], fill=(12, 22, 34))
d.line([(232, 782), (232, 762)], fill=(12, 22, 34), width=3)
d.ellipse([226, 752, 238, 764], fill=(255, 200, 120))
d.ellipse([229, 755, 235, 761], fill=(255, 228, 165))
d.line([(232, 764), (232, 800)], fill=(255, 176, 92), width=1)

# ---------------------------------------------------------------- foreground pier, bottom-left
d.polygon([(0, 1024), (0, 946), (150, 928), (210, 936), (210, 1024)],
          fill=(8, 18, 28))
d.rectangle([26, 900, 34, 946], fill=(8, 18, 28))
d.rectangle([120, 894, 128, 940], fill=(8, 18, 28))
for px, py in [(30, 892), (124, 886)]:
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse([px - 12, py - 12, px + 12, py + 12], fill=(255, 180, 90, 90))
    ov = ov.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(img)
    d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=(255, 200, 120))
    d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 228, 165))

# ---------------------------------------------------------------- type
NAME_FONT = ImageFont.truetype(FONT_BOLD, 92)
SUB_FONT = ImageFont.truetype(FONT_BOLD, 27)
TAG_FONT = ImageFont.truetype(FONT_SERIF_IT, 27)
FOOT_FONT = ImageFont.truetype(FONT_REG, 15)

# soft shadow then cream name, letterspaced
draw_tracked(d, W // 2 + 3, 63, "VELMARA", NAME_FONT, (10, 18, 32), 14)
draw_tracked(d, W // 2, 60, "VELMARA", NAME_FONT, (255, 242, 216), 14)
# gold rules flanking the subtitle
sub_w = tracked_size(SUB_FONT, "THE LANTERN HARBOUR", 8)
rule_y = 196
d.line([(W // 2 - sub_w // 2 - 66, rule_y), (W // 2 - sub_w // 2 - 16, rule_y)],
       fill=(232, 176, 96), width=2)
d.line([(W // 2 + sub_w // 2 + 16, rule_y), (W // 2 + sub_w // 2 + 66, rule_y)],
       fill=(232, 176, 96), width=2)
draw_tracked(d, W // 2, 182, "THE LANTERN HARBOUR", SUB_FONT,
             (240, 196, 120), 8)
# tagline at the foot
draw_tracked(d, W // 2, 936, "Where the tide carries the light home.",
             TAG_FONT, (255, 240, 210), 1)
# small footer, bottom centre
draw_tracked(d, W // 2, 978, "AN ISLAND THAT ISN'T ON ANY MAP",
             FOOT_FONT, (200, 190, 168), 4)

os.makedirs(OUT_DIR, exist_ok=True)
img.save(OUT_PATH, format="PNG")
print("wrote", OUT_PATH, img.size, os.path.getsize(OUT_PATH), "bytes")
