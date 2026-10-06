# assemble-frontend-gif.py
# Stitch the captured frontend-frames/*.png (from make-frontend-gif.mjs)
# into a looping GIF with one shared 256-colour palette (no flicker).
#
# Env overrides: GIF_W (output width; 0 keeps capture size), GIF_FPS (20).
import glob
import os

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
FRAMES = sorted(glob.glob(os.path.join(ROOT, "frontend-frames", "f*.png")))
OUT = os.path.join(ROOT, "solar-flow-frontend.gif")
OUT_W = int(os.environ.get("GIF_W", "0"))
FPS = int(os.environ.get("GIF_FPS", "20"))

if not FRAMES:
    raise SystemExit("no frames found - run make-frontend-gif.mjs first")

imgs = [Image.open(f).convert("RGB") for f in FRAMES]
w, h = imgs[0].size
if any(im.size != (w, h) for im in imgs):
    raise SystemExit("frame sizes differ")
if OUT_W and OUT_W != w:
    nh = round(h * OUT_W / w)
    imgs = [im.resize((OUT_W, nh), Image.LANCZOS) for im in imgs]

# Palette from a settled frame -> consistent colours across all frames.
pal = imgs[60].quantize(colors=256)
qframes = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in imgs]

qframes[0].save(OUT, save_all=True, append_images=qframes[1:],
                duration=round(1000 / FPS), loop=0, optimize=True)
print(f"{OUT}")
print(f"  {qframes[0].size[0]}x{qframes[0].size[1]}, {len(qframes)} frames "
      f"@ {round(1000 / FPS)} ms, {os.path.getsize(OUT) / 1024:.0f} KB")
