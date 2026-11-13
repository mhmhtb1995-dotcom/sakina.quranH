"""إنتاج الفيديو. اختبار يدوي: python render.py 1 3   (ينتج الفيديوهات من 1 إلى 3 في out/videos)"""
import html, json, pathlib, random, subprocess, sys
from config import *
from prepare import audio_for

ROOT = pathlib.Path(__file__).parent
BUILD = ROOT / "build"; PNG_DIR = BUILD / "png"; TMP = BUILD / "tmp"
OUT_DIR = ROOT / "out" / "videos"
for d in (PNG_DIR, TMP, OUT_DIR):
    d.mkdir(parents=True, exist_ok=True)
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}

BASE_CSS = """@font-face{font-family:V;src:url('file://@@fv@@')}
@font-face{font-family:T;src:url('file://@@ft@@')}
html,body{margin:0;width:1080px;height:1920px;background:transparent;direction:rtl;color:@@txt@@}"""

STATIC_PAGE = """<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>
""" + BASE_CSS + """
#scrim{position:absolute;inset:0;background:
 radial-gradient(ellipse 85% 48% at 50% 50%,rgba(0,0,0,.30),rgba(0,0,0,0) 100%),
 linear-gradient(to bottom,rgba(0,0,0,.62) 0%,rgba(0,0,0,.46) 24%,rgba(0,0,0,.50) 50%,rgba(0,0,0,.46) 76%,rgba(0,0,0,.66) 100%)}
#top{position:absolute;top:150px;width:100%;text-align:center}
#surah{font-family:T;font-size:104px;line-height:1.2;color:@@acc@@;text-shadow:0 3px 6px rgba(0,0,0,.9),0 0 26px rgba(0,0,0,.8)}
.orn{display:flex;align-items:center;justify-content:center;gap:22px;margin-top:10px;color:@@acc@@;font-size:46px;font-family:V}
.orn i{display:block;width:230px;height:3px;background:linear-gradient(to left,@@acc@@,rgba(242,210,122,0))}
.orn i:last-child{background:linear-gradient(to right,@@acc@@,rgba(242,210,122,0))}
#foot{position:absolute;bottom:140px;width:100%;text-align:center;font-family:V;font-size:40px;color:#f2f2f2;
 text-shadow:0 2px 5px rgba(0,0,0,.95),0 0 16px rgba(0,0,0,.8);line-height:1.8}
#foot b{color:@@acc@@;font-weight:normal}
</style></head><body><div id="scrim"></div>
<div id="top"><div id="surah">@@surah@@</div><div class="orn"><i></i>۞<i></i></div></div>
<div id="foot">@@reciter@@<br><b>@@handle@@</b></div></body></html>"""

TEXT_PAGE = """<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>
""" + BASE_CSS + """
#box{position:absolute;top:470px;left:80px;width:920px;height:980px;display:flex;align-items:center;justify-content:center}
#t{font-family:V;text-align:center;line-height:2.0;width:100%;text-wrap:balance;color:@@txt@@;
 text-shadow:0 2px 4px rgba(0,0,0,.95),0 0 18px rgba(0,0,0,.85),0 0 42px rgba(0,0,0,.6)}
#t .n{color:@@acc@@}
</style></head><body><div id="box"><div id="t">@@text@@</div></div>
<script>
const t=document.getElementById('t');let fs=96;t.style.fontSize=fs+'px';
while(t.offsetHeight>980&&fs>26){fs-=2;t.style.fontSize=fs+'px';}
</script></body></html>"""


def fill(tpl, **kw):
    for k, v in kw.items():
        tpl = tpl.replace(f"@@{k}@@", str(v))
    return tpl


def _fmt():
    return dict(fv=(ROOT / "fonts" / FONT_VERSE_FILE).as_posix(), ft=(ROOT / "fonts" / FONT_TITLE_FILE).as_posix(),
                txt=COLOR_TEXT, acc=COLOR_ACCENT)


def _shot(page, html_str, out):
    f = TMP / "frame.html"; f.write_text(html_str, encoding="utf-8")
    page.goto(f.as_uri()); page.evaluate("document.fonts.ready.then(()=>true)")
    page.screenshot(path=str(out), omit_background=True)


def static_png(page, v):
    out = PNG_DIR / f"static_{v['surah']:03d}.png"
    if not out.exists():
        h = fill(STATIC_PAGE, **_fmt(), surah="سورة " + v["surah_name"], reciter=html.escape(RECITER_NAME_AR),
                               handle='<bdi dir="ltr">' + html.escape(CHANNEL_HANDLE) + '</bdi>')
        _shot(page, h, out)
    return out


def text_png(page, it):
    out = PNG_DIR / f"txt_{it['surah']:03d}_{it['ayah']:03d}.png"
    if not out.exists():
        if it["ayah"] == 0:
            body = html.escape(it["text"])
        else:
            n = str(it["ayah"]).translate(AR)
            body = f"{html.escape(it['text'])} <span class='n'>﴿{n}﴾</span>"
        _shot(page, fill(TEXT_PAGE, **_fmt(), text=body), out)
    return out


def probe(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "default=nw=1:nk=1", str(p)]))


def build_audio(items):
    n = len(items)
    total = sum(it["dur"] for it in items) + GAP * n
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for it in items:
        cmd += ["-i", str(audio_for(1, 1) if it["ayah"] == 0 else audio_for(it["surah"], it["ayah"]))]
    fc = [f"[{i}:a]aresample=44100,aformat=channel_layouts=stereo,apad=pad_dur={GAP}[a{i}]" for i in range(n)]
    fc.append("".join(f"[a{i}]" for i in range(n)) +
              f"concat=n={n}:v=0:a=1,afade=t=in:d=0.15,afade=t=out:st={max(total-0.5,0):.3f}:d=0.45[out]")
    a = TMP / "audio.m4a"
    cmd += ["-filter_complex", ";".join(fc), "-map", "[out]", "-c:a", "aac", "-b:a", "160k", str(a)]
    subprocess.run(cmd, check=True)
    return a


def pick_background(total):
    """يختار فيديو خلفية عشوائيًا ومقطعًا عشوائيًا منه بطول الفيديو."""
    bgs = [p for p in (ROOT / "backgrounds").glob("*") if p.suffix.lower() in VIDEO_EXT]
    if not bgs:
        return ["-f", "lavfi", "-i", "color=c=0x0a2e24:s=1080x1920:r=30"]
    src = random.choice(bgs)
    d = probe(src)
    if d > total + 2:
        start = random.uniform(0, d - total - 1)
        return ["-ss", f"{start:.2f}", "-i", str(src)]
    return ["-stream_loop", "-1", "-i", str(src)]


def render_video(page, v):
    """ينتج الفيديو ويعيد مساره. page = صفحة playwright."""
    out = OUT_DIR / v["file"]
    items = v["items"]
    statp = static_png(page, v)
    pngs = [text_png(page, it) for it in items]
    audio = build_audio(items)
    total = probe(audio)
    n = len(items)
    cmd = ["ffmpeg", "-y", "-v", "error"] + pick_background(total)
    cmd += ["-loop", "1", "-framerate", "30", "-t", f"{total:.3f}", "-i", str(statp)]
    for p in pngs:
        cmd += ["-loop", "1", "-framerate", "30", "-t", f"{total:.3f}", "-i", str(p)]
    cmd += ["-i", str(audio)]
    blur = f"gblur=sigma={BG_BLUR}," if BG_BLUR else ""
    fc = [f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,{blur}"
          f"eq=brightness={BG_BRIGHTNESS}:saturation=0.9,format=yuv420p[b0]",
          "[1:v]format=rgba[st]", "[b0][st]overlay=0:0:format=auto[s0]"]
    for i, it in enumerate(items):
        end = total if i == n - 1 else it["end"] - 0.05
        fc.append(f"[{i+2}:v]format=rgba,fade=t=in:st={it['start']:.3f}:d=0.30:alpha=1,"
                  f"fade=t=out:st={max(end-0.30, it['start']):.3f}:d=0.30:alpha=1[t{i}]")
        fc.append(f"[s{i}][t{i}]overlay=0:0:format=auto[s{i+1}]")
    fc.append(f"[s{n}]fade=t=in:st=0:d=0.5,fade=t=out:st={max(total-0.5,0):.3f}:d=0.45,format=yuv420p[v]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", f"{n+2}:a", "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-r", "30",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    d = probe(out)
    if d > HARD_LIMIT and not v["long"]:
        out.unlink()
        raise RuntimeError(f"الفيديو {v['id']} مدته {d:.2f}ث > {HARD_LIMIT}")
    return out


if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    plan = json.loads((ROOT / "plan.json").read_text(encoding="utf-8"))
    a = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    b = int(sys.argv[2]) if len(sys.argv) > 2 else a
    with sync_playwright() as p:
        br = p.chromium.launch(); page = br.new_page(viewport={"width": 1080, "height": 1920})
        for v in plan[a - 1:b]:
            f = render_video(page, v); print(f"{f.name}  {probe(f):.1f}s")
        br.close()
