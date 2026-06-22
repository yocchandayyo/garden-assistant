"""
プラログ ブランドアセット生成スクリプト
Nano Banana Pro (Gemini 3 Pro Image) で、爽やか＆先鋭的・和モダンの
ロゴ／アプリアイコン／ボトムタブ4種を生成する。
使い方:  python generate_assets.py
（GEMINI_API_KEY は同階層の親フォルダ .env から読み込む）
"""
import os, sys, mimetypes
from google import genai
from google.genai import types

# キー読み込み：生キー入りファイル（germi_api.txt等）→ .env の順で探す
def load_key():
    here = os.path.dirname(__file__)
    raw_files = [
        os.path.join(here, "..", "germi_api.txt"),
        os.path.join(here, "..", "gemini_api.txt"),
        os.path.join(here, "..", "API.txt"),
    ]
    for rf in raw_files:
        if os.path.exists(rf):
            txt = open(rf, encoding="utf-8").read().strip()
            key = txt.split("=", 1)[1].strip() if "=" in txt.splitlines()[0] else txt.strip()
            if key:
                os.environ["GEMINI_API_KEY"] = key
                return
    for cand in [os.path.join(here, "..", "..", ".env"), os.path.join(here, "..", ".env")]:
        if os.path.exists(cand):
            for line in open(cand, encoding="utf-8"):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
            return
load_key()

MODEL = "gemini-3-pro-image-preview"   # Nano Banana Pro
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

OUT = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(OUT, exist_ok=True)

STYLE = (
  "Minimalist flat vector icon, modern and crisp, premium plant-tech brand identity. "
  "Smooth clean geometry, gently rounded forms, confident even line weight. "
  "Strict color palette: moss green #3F7D5B, fresh asagi teal #2F9E8F, deep pine #234A36, soft mint highlights. "
  "Subtle smooth gradients allowed. Centered, comfortable padding. "
  "FULLY TRANSPARENT background (PNG alpha), absolutely no background panel, no drop shadow, no text, no frame. "
  "Fresh, airy, sharp, high-end Japanese wa-modern aesthetic. Square 1:1."
)

JOBS = {
  "logo-mark": (
    "A single elegant plant sprout with two symmetric leaves rising upward, forming a calm iconic emblem "
    "for a plant care app. Smooth teal-to-moss-green gradient on the leaves. Simple, memorable, balanced. " + STYLE
  ),
  "app-icon": (
    "App icon for a plant care app: a refined two-leaf sprout emblem centered on a soft smooth gradient "
    "background going from pale mint to soft paper-white #EEF4EF with a gentle teal glow. Friendly rounded-square "
    "app-icon composition with subtle depth and a faint Japanese seigaiha wave texture, no text. "
    "Modern wa-modern plant-tech. Clean, premium, fresh. Square 1:1. (Background is intentionally filled, not transparent.)"
  ),
  "tab-identify": (
    "Icon: a magnifying glass overlapping a single leaf, representing 'identify / explore a plant'. " + STYLE
  ),
  "tab-diagnose": (
    "Icon: a single leaf with a smooth heartbeat pulse line passing through its center, representing a plant "
    "health check / diagnosis. Gentle and clear. " + STYLE
  ),
  "tab-garden": (
    "Icon: a small potted plant with two rounded leaves in a minimalist modern pot, representing 'my garden'. " + STYLE
  ),
  "tab-calendar": (
    "Icon: a clean minimalist calendar page with a small water drop (teal) on it, representing a care schedule. " + STYLE
  ),
}

def gen(name, prompt):
    print(f"... generating {name}")
    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )
    saved = False
    for cand in resp.candidates or []:
        for part in (cand.content.parts if cand.content else []):
            if getattr(part, "inline_data", None) and part.inline_data.data:
                ext = mimetypes.guess_extension(part.inline_data.mime_type or "image/png") or ".png"
                path = os.path.join(OUT, name + ext)
                with open(path, "wb") as f:
                    f.write(part.inline_data.data)
                print(f"    saved {path} ({len(part.inline_data.data)//1024} KB, {part.inline_data.mime_type})")
                saved = True
            elif getattr(part, "text", None):
                print(f"    [text] {part.text[:120]}")
    if not saved:
        print(f"    !! no image returned for {name}")
    return saved

if __name__ == "__main__":
    only = sys.argv[1:] if len(sys.argv) > 1 else list(JOBS.keys())
    ok = 0
    for name in only:
        if name in JOBS:
            try:
                ok += 1 if gen(name, JOBS[name]) else 0
            except Exception as e:
                print(f"    ERROR {name}: {e}")
    print(f"done: {ok}/{len(only)} images")
