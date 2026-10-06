# make-solar-flow-gif.py
"""
Render the Solar Flow animated hero infographic (the SVG diagram inside
solar-flow-elementor.html) to a looping animated GIF, using Pillow only.

Animation timing mirrors the CSS in solar-flow-elementor.html:
- Entrance: nodes pop in (back/spring ease), connectors + labels rise,
  staggered ~0.2 s apart (same delays/durations as the CSS classes).
- Ambient: sun-glow pulse, ray rotation + twinkle, energy dashes along the
  connectors, inverter waveform pulse, savings-coin bob.

Ambient periods are snapped to divisors of a 3.2 s master cycle
(glow/ray/wave 3.2 s, rotation 12.8 s/rev = 90 deg per cycle, which is
seamless for the 8-fold symmetric rays, dashes 1.6 / 1.28 / 0.8 s,
coin 3.2 s) so the ambient loop repeats without a visible jump.

Usage (from this folder):
    python make-solar-flow-gif.py                    # 1200 px wide, 20 fps
    set GIF_W=900&& python make-solar-flow-gif.py    # smaller file
    set GIF_FPS=15&& python make-solar-flow-gif.py   # fewer frames
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_GIF = os.path.join(ROOT, "solar-flow.gif")
OUT_PNG = os.path.join(ROOT, "solar-flow-preview.png")

VW, VH = 1200.0, 420.0          # SVG viewBox user units
OUT_W = int(os.environ.get("GIF_W", "1200"))
FPS = int(os.environ.get("GIF_FPS", "20"))
SS = 2.0 * OUT_W / VW           # supersample factor (render big, downscale)
W, H = round(VW * SS), round(VH * SS)
OUT_H = round(VH * OUT_W / VW)

T_ENTRANCE = 2.2                # seconds of entrance captured
T_AMBIENT = 3.2                 # seamless ambient cycle length
DUR = 1000 // FPS               # ms per GIF frame

FONTS = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")


def F(name, size):
    return ImageFont.truetype(
        os.path.join(FONTS, name), max(1, int(round(size * SS)))
    )


f_label = F("arialbd.ttf", 15)
f_sub = F("arial.ttf", 12)
f_big = F("arialbd.ttf", 22)
f_badge = F("arialbd.ttf", 11)
f_saved = F("arialbd.ttf", 10)


def hx(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, f):
    return tuple(int(round(a[i] + (b[i] - a[i]) * f)) for i in range(3))


def ease_out_cubic(p):
    p = min(1.0, max(0.0, p))
    return 1 - (1 - p) ** 3


def ease_out_back(p):
    """cubic-bezier(.34,1.56,.64,1) == CSS easeOutBack."""
    p = min(1.0, max(0.0, p))
    c1 = 1.70158
    return 1 + (c1 + 1) * (p - 1) ** 3 + c1 * (p - 1) ** 2


def env(phi):
    """0 -> 1 -> 0 sine envelope (matches ease-in-out 0%/50%/100% keyframes)."""
    return (1 - math.cos(2 * math.pi * (phi % 1.0))) / 2


def prog(t, delay, dur):
    return min(1.0, max(0.0, (t - delay) / dur))


# ---------------------------------------------------------------- background
def build_bg():
    """radial-gradient(1200px 600px at 15% 0%, #10312d, #0a1f1c 55%, #071513)"""
    gw, gh = 240, 84
    img = Image.new("RGB", (gw, gh))
    px = img.load()
    c0, c1, c2 = hx("#10312d"), hx("#0a1f1c"), hx("#071513")
    for j in range(gh):
        y = (j + 0.5) / gh * VH
        for i in range(gw):
            x = (i + 0.5) / gw * VW
            d = math.hypot((x - 180) / 1200.0, y / 600.0)
            if d < 0.55:
                col = mix(c0, c1, d / 0.55)
            else:
                col = mix(c1, c2, min(1.0, (d - 0.55) / 0.45))
            px[i, j] = col
    return img.resize((W, H), Image.BILINEAR)


BG = build_bg()

# ----------------------------------------------------------- gradient patches
def grad_rect(x, y, w, h, c1, c2, rx=0.0, alpha=1.0):
    """Vertical linear-gradient rect with rounded-corner mask -> (patch, pos)."""
    wS, hS = max(1, int(round(w * SS))), max(1, int(round(h * SS)))
    base = Image.new("RGB", (1, 2))
    base.putpixel((0, 0), c1)
    base.putpixel((0, 1), c2)
    g = base.resize((wS, hS), Image.BILINEAR)
    m = Image.new("L", (wS, hS), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        [0, 0, wS - 1, hS - 1], radius=max(0.0, rx * SS), fill=255
    )
    if alpha < 1:
        m = m.point(lambda v: int(v * alpha))
    return (Image.merge("RGBA", (*g.split(), m)),
            (int(round(x * SS)), int(round(y * SS))))


def grad_ellipse(cx, cy, r, c1, c2, alpha=1.0):
    """Horizontal linear-gradient disc -> (patch, pos)."""
    rS = max(2, int(round(r * SS)))
    size = 2 * rS + 2
    base = Image.new("RGB", (2, 1))
    base.putpixel((0, 0), c1)
    base.putpixel((1, 0), c2)
    g = base.resize((size, size), Image.BILINEAR)
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse([0, 0, size - 1, size - 1], fill=255)
    if alpha < 1:
        m = m.point(lambda v: int(v * alpha))
    return (Image.merge("RGBA", (*g.split(), m)),
            (int(round(cx * SS)) - rS - 1, int(round(cy * SS)) - rS - 1))


def sun_glow_patch(cx, cy, r, glow_alpha):
    """radialGradient #ffe0a3@0.9 -> #ffb347@0.35(60%) -> 0(100%)."""
    rS = max(2, int(round(r * SS)))
    size = 2 * rS + 2
    gw = 64
    A = Image.new("L", (gw, gw))
    pa = A.load()
    G = Image.new("RGB", (gw, gw))
    pg = G.load()
    ci, co = hx("#ffe0a3"), hx("#ffb347")
    for jj in range(gw):
        for ii in range(gw):
            dx = (ii + 0.5) / gw * 2 - 1
            dy = (jj + 0.5) / gw * 2 - 1
            d = min(1.0, math.hypot(dx, dy))
            if d < 0.6:
                f = d / 0.6
                col = mix(ci, co, f)
                a = 0.9 - 0.55 * f
            else:
                col = co
                a = 0.35 * (1 - (d - 0.6) / 0.4)
            pa[ii, jj] = int(max(0.0, a) * 255 * glow_alpha)
            pg[ii, jj] = col
    A = A.resize((size, size), Image.BILINEAR)
    G = G.resize((size, size), Image.BILINEAR)
    return (Image.merge("RGBA", (*G.split(), A)),
            (int(round(cx * SS)) - rS - 1, int(round(cy * SS)) - rS - 1))


# ---------------------------------------------------------------- primitives
def dashed_line(dr, p0, p1, color, width, dash=9.0, gap=13.0, shift=0.0):
    """SVG-style stroke-dasharray 9 13 line; `shift` moves dashes p0 -> p1."""
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return
    ux, uy = dx / L, dy / L
    period = dash + gap
    s = shift % period
    w = max(1, int(round(width * SS)))
    k = -1
    while True:
        a = k * period + s
        if a > L:
            break
        b = min(L, a + dash)
        if b > 0:
            a2 = max(0.0, a)
            dr.line([(x0 + ux * a2) * SS, (y0 + uy * a2) * SS,
                     (x0 + ux * b) * SS, (y0 + uy * b) * SS],
                    fill=color, width=w)
        k += 1


def arrow(dr, p_end, direction, color):
    """SVG marker 6x6 refX/refY 3, markerUnits=strokeWidth, stroke 2.5
    -> 15x15 user units; tip pokes 7.5 past the line end."""
    n = math.hypot(direction[0], direction[1])
    ux, uy = direction[0] / n, direction[1] / n
    nx, ny = -uy, ux
    ex, ey = p_end
    b = 7.5
    dr.polygon([((ex + ux * b) * SS, (ey + uy * b) * SS),
                ((ex - ux * b + nx * b) * SS, (ey - uy * b + ny * b) * SS),
                ((ex - ux * b - nx * b) * SS, (ey - uy * b - ny * b) * SS)],
               fill=color)

# --------------------------------------------------------------------- nodes
def draw_sun(dr, cv, t, alpha, scale):
    cx, cy = 105.0, 150.0
    eg = env(t / 3.2)
    patch, pos = sun_glow_patch(cx, cy, 58.0 * (1 + 0.08 * eg) * scale,
                                (0.55 + 0.35 * eg) * alpha)
    cv.paste(patch, pos, patch)
    ra = (0.35 + 0.65 * eg) * alpha
    rot = math.radians(360.0 * t / 12.8)   # 90 deg per 3.2 s cycle
    for k in range(8):
        a = math.radians(45 * k) + rot
        ux, uy = math.sin(a), -math.cos(a)
        dr.line([(cx + ux * 72 * scale) * SS, (cy + uy * 72 * scale) * SS,
                 (cx + ux * 88 * scale) * SS, (cy + uy * 88 * scale) * SS],
                fill=(*hx("#ffb347"), int(255 * ra)),
                width=max(1, int(round(3 * SS * scale))))
    patch, pos = grad_ellipse(cx, cy, 32 * scale,
                              hx("#ffd166"), hx("#ffb347"), alpha=alpha)
    cv.paste(patch, pos, patch)
    rr = 32 * scale * SS
    dr.ellipse([cx * SS - rr, cy * SS - rr, cx * SS + rr, cy * SS + rr],
               outline=(*hx("#ffe0a3"), int(255 * 0.6 * alpha)),
               width=max(1, int(round(1.5 * SS * scale))))


def draw_panel(dr, cv, t, alpha, scale):
    cx, cy = 400.0, 161.0                       # fill-box centre (bbox)
    T = lambda px, py: (cx + (px - cx) * scale, cy + (py - cy) * scale)
    x0, y0 = T(305, 115)
    w, h = 190 * scale, 70 * scale
    patch, pos = grad_rect(x0, y0, w, h, hx("#1d4d89"), hx("#123a6b"),
                           rx=8 * scale)
    cv.paste(patch, pos, patch)
    lw = max(1, int(round(2 * SS * scale)))
    grid = (*hx("#0f2d57"), int(255 * alpha))
    for lx in (325, 365, 405, 445):
        a, b = T(lx, 115), T(lx, 185)
        dr.line([a[0] * SS, a[1] * SS, b[0] * SS, b[1] * SS], fill=grid, width=lw)
    a, b = T(305, 150), T(495, 150)
    dr.line([a[0] * SS, a[1] * SS, b[0] * SS, b[1] * SS], fill=grid, width=lw)
    gx, gy = T(305, 115)
    dr.rounded_rectangle([gx * SS, gy * SS,
                          (gx + 190 * scale) * SS, (gy + 32 * scale) * SS],
                         radius=8 * scale * SS,
                         fill=(255, 255, 255, int(255 * 0.06 * alpha)))
    sx, sy = T(392, 185)
    dr.rectangle([sx * SS, sy * SS,
                  (sx + 16 * scale) * SS, (sy + 22 * scale) * SS],
                 fill=(*hx("#1c353d"), int(255 * alpha)))
    dr.rounded_rectangle([x0 * SS, y0 * SS, (x0 + w) * SS, (y0 + h) * SS],
                         radius=8 * scale * SS,
                         outline=(*hx("#2a6bc7"), int(255 * alpha)),
                         width=max(1, int(round(1.5 * SS * scale))))

def draw_inverter(dr, cv, t, alpha, scale):
    cx, cy = 720.0, 150.0
    T = lambda px, py: (cx + (px - cx) * scale, cy + (py - cy) * scale)
    x0, y0 = T(625, 115)
    w, h = 190 * scale, 70 * scale
    patch, pos = grad_rect(x0, y0, w, h, hx("#2a4a55"), hx("#1c353d"),
                           rx=10 * scale)
    cv.paste(patch, pos, patch)
    wa = alpha * (0.5 + 0.5 * env(t / 1.6))
    pts = []
    x = 645.0
    while x <= 805.0:
        wx, wy = T(x, 150 - 10 * math.sin(2 * math.pi * (x - 645) / 40.0))
        pts.append((wx * SS, wy * SS))
        x += 1.0
    dr.line(pts, fill=(*hx("#3ddc97"), int(255 * wa)),
            width=max(1, int(round(2.2 * SS * scale))), joint="curve")
    for bx, by, txt, col, bgc in (
            (770, 123, "AC", hx("#3ddc97"), (61, 220, 151)),
            (770, 160, "DC", hx("#ffb347"), (255, 179, 71))):
        p = T(bx, by)
        dr.rounded_rectangle([p[0] * SS, p[1] * SS,
                              (p[0] + 36 * scale) * SS, (p[1] + 18 * scale) * SS],
                             radius=4 * scale * SS,
                             fill=(*bgc, int(255 * 0.15 * alpha)))
        c = T(bx + 18, by + 13)
        dr.text((c[0] * SS, c[1] * SS), txt, font=f_badge,
                fill=(*col, int(255 * alpha)), anchor="ms")
    dr.rounded_rectangle([x0 * SS, y0 * SS, (x0 + w) * SS, (y0 + h) * SS],
                         radius=10 * scale * SS,
                         outline=(*hx("#3ddc97"), int(255 * 0.4 * alpha)),
                         width=max(1, int(round(1.5 * SS * scale))))


def draw_home(dr, cv, t, alpha, scale):
    cx, cy = 987.5, 140.0                       # fill-box centre (bbox)
    T = lambda px, py: (cx + (px - cx) * scale, cy + (py - cy) * scale)
    x0, y0 = T(945, 115)
    w, h = 85 * scale, 85 * scale
    patch, pos = grad_rect(x0, y0, w, h, hx("#eef7f3"), hx("#d4e9e0"),
                           rx=8 * scale)
    cv.paste(patch, pos, patch)
    roof = [T(935, 115), T(987, 80), T(1040, 115)]
    dr.polygon([(p[0] * SS, p[1] * SS) for p in roof],
               fill=(*hx("#2bbf80"), int(255 * alpha)))
    dx0, dy0 = T(975, 155)
    dr.rounded_rectangle([dx0 * SS, dy0 * SS,
                          (dx0 + 22 * scale) * SS, (dy0 + 45 * scale) * SS],
                         radius=3 * scale * SS,
                         fill=(*hx("#1c353d"), int(255 * alpha)))
    for wx, wy, a in ((953, 128, 0.85), (1005, 128, 0.5)):
        p = T(wx, wy)
        dr.rounded_rectangle([p[0] * SS, p[1] * SS,
                              (p[0] + 16 * scale) * SS, (p[1] + 16 * scale) * SS],
                             radius=2 * scale * SS,
                             fill=(*hx("#3ddc97"), int(255 * a * alpha)))


def draw_coin(dr, cv, t, alpha, scale):
    dy = -3.0 * env(t / 3.2)
    cx, cy = 1095.0, 315.0 + dy
    patch, pos = grad_ellipse(cx, cy, 42 * scale,
                              hx("#3ddc97"), hx("#2bbf80"), alpha=alpha)
    cv.paste(patch, pos, patch)
    rr = 42 * scale * SS
    dr.ellipse([cx * SS - rr, cy * SS - rr, cx * SS + rr, cy * SS + rr],
               outline=(*hx("#a6f0d2"), int(255 * 0.5 * alpha)),
               width=max(1, int(round(1.5 * SS * scale))))
    dr.text((cx * SS, (310 + dy) * SS), "$", font=f_big,
            fill=(*hx("#0a1f1c"), int(255 * alpha)), anchor="ms")
    txt = "SAVED"
    sp = 1.0 * SS * scale
    widths = [f_saved.getlength(c) for c in txt]
    x = cx * SS - (sum(widths) + sp * (len(txt) - 1)) / 2
    for c, wch in zip(txt, widths):
        dr.text((x, (330 + dy) * SS), c, font=f_saved,
                fill=(*hx("#0a1f1c"), int(255 * alpha)), anchor="ls")
        x += wch + sp

# --------------------------------------------------------------- connectors
CONNS = (
    ((150, 150), (305, 150), "#ffb347", "#ffd166", "#ffb347", 1.6),
    ((495, 150), (625, 150), "#ffd166", "#ffd166", "#ffb347", 1.6),
    ((815, 150), (945, 150), "#3ddc97", "#3ddc97", "#3ddc97", 1.28),
    ((1030, 200), (1090, 285), "#3ddc97", "#3ddc97", "#3ddc97", 0.8),
)


def draw_connectors(dr, t):
    for j, (p0, p1, faint, line, arr, P) in enumerate(CONNS):
        e = ease_out_cubic(prog(t, 0.55 + 0.2 * j, 0.5))
        if e <= 0:
            continue
        dy = 14 * (1 - e)
        a0 = (p0[0], p0[1] + dy)
        a1 = (p1[0], p1[1] + dy)
        dr.line([a0[0] * SS, a0[1] * SS, a1[0] * SS, a1[1] * SS],
                fill=(*hx(faint), int(255 * 0.18 * e)),
                width=max(1, int(round(2 * SS))))
        dashed_line(dr, a0, a1, (*hx(line), int(255 * e)), 2.5,
                    shift=44.0 * t / P)
        arrow(dr, a1, (a1[0] - a0[0], a1[1] - a0[1]), (*hx(arr), int(255 * e)))


LABELS = (
    (105, 232, "Sunlight", "Free & unlimited", "#f1fbf8"),
    (400, 232, "Solar Panels", "Capture DC current", "#f1fbf8"),
    (720, 232, "Inverter", "Converts DC to AC", "#f1fbf8"),
    (987, 232, "Your Home", "Powered by the sun", "#f1fbf8"),
    (1095, 382, "Bill Savings", "Lower monthly costs", "#3ddc97"),
)


def draw_labels(dr, t):
    for i, (x, y1, main, sub, col) in enumerate(LABELS):
        e = ease_out_cubic(prog(t, 0.6 + 0.2 * i, 0.5))
        if e <= 0:
            continue
        dy = 14 * (1 - e)
        dr.text((x * SS, (y1 + dy) * SS), main, font=f_label,
                fill=(*hx(col), int(255 * e)), anchor="ms")
        dr.text((x * SS, (y1 + 20 + dy) * SS), sub, font=f_sub,
                fill=(*hx("#9fb8b2"), int(255 * e)), anchor="ms")


# --------------------------------------------------------------------- frame
NODES = (draw_sun, draw_panel, draw_inverter, draw_home, draw_coin)


def node_anim(t, idx):
    p = prog(t, 0.45 + 0.2 * idx, 0.6)
    if p <= 0:
        return None
    b = ease_out_back(p)
    return min(1.0, max(0.0, b)), 0.6 + 0.4 * b   # (opacity, scale)


def render_frame(t):
    cv = BG.copy()
    dr = ImageDraw.Draw(cv, "RGBA")
    draw_connectors(dr, t)
    for idx, fn in enumerate(NODES):
        na = node_anim(t, idx)
        if na:
            fn(dr, cv, t, na[0], na[1])
    draw_labels(dr, t)
    return cv.convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS)


def main():
    n_entrance = round(T_ENTRANCE * FPS)
    n_ambient = round(T_AMBIENT * FPS)
    total = n_entrance + n_ambient

    # One consistent 256-colour palette from a settled frame -> no flicker.
    pal = render_frame(T_ENTRANCE + 1.6).quantize(colors=256)

    def q(fr):
        return fr.quantize(palette=pal, dither=Image.Dither.NONE)

    frames = []
    for k in range(total):
        if k < n_entrance:
            t = k / float(FPS)                      # entrance: 0 .. 2.15 s
        else:
            t = T_ENTRANCE + (k - n_entrance) / float(FPS)   # ambient: +3.2 s
        frames.append(q(render_frame(t)))
        if k % 20 == 0:
            print(f"frame {k + 1}/{total} (t={t:.2f}s)", flush=True)

    # Full-resolution previews for a quick visual check.
    render_frame(T_ENTRANCE + 1.6).save(OUT_PNG)
    render_frame(1.0).save(os.path.join(ROOT, "solar-flow-preview-entrance.png"))

    frames[0].save(OUT_GIF, save_all=True, append_images=frames[1:],
                   duration=DUR, loop=0, optimize=True)

    kb = os.path.getsize(OUT_GIF) / 1024
    print(f"\nGIF  : {OUT_GIF}")
    print(f"       {OUT_W}x{OUT_H}, {total} frames @ {DUR} ms, {kb:.0f} KB")


if __name__ == "__main__":
    main()




