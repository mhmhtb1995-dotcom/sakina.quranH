"""تحميل الخطوط تلقائيًا والتحقق من ffmpeg"""
import pathlib, shutil, requests
ROOT = pathlib.Path(__file__).parent
FONTS = {
    "AmiriQuran-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/amiriquran/AmiriQuran-Regular.ttf",
    "ArefRuqaa-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/arefruqaa/ArefRuqaa-Bold.ttf",
}
(ROOT / "fonts").mkdir(exist_ok=True)
for name, url in FONTS.items():
    p = ROOT / "fonts" / name
    if p.exists():
        print("موجود:", name); continue
    try:
        r = requests.get(url, timeout=60); r.raise_for_status(); p.write_bytes(r.content); print("تم تحميل:", name)
    except Exception as e:
        print(f"تعذر تحميل {name}: {e}\n  حمّله يدويًا من fonts.google.com (Amiri Quran / Aref Ruqaa) وضعه في مجلد fonts/")
for tool in ("ffmpeg", "ffprobe"):
    print(tool, "✓" if shutil.which(tool) else "✗ غير مثبت")
