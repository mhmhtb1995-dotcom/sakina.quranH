"""مهمة واحدة: تنتج الفيديو التالي وتنشره وتحفظ التقدم. تُشغَّل من GitHub Actions.
--dry-run : تنتج 3 فيديوهات للمراجعة فقط، دون نشر ودون تغيير التقدم."""
import json, os, pathlib, sys
from playwright.sync_api import sync_playwright
from config import *
import publish, render

ROOT = pathlib.Path(__file__).parent
STATE, SKIPPED = ROOT / "state.json", ROOT / "skipped_long.txt"


def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {"next": 0, "cycle": 1}


def advance(st, plan):
    st["next"] += 1
    if st["next"] % len(plan) == 0:
        st["cycle"] += 1; print("ختمة جديدة: العودة إلى الفاتحة")
    STATE.write_text(json.dumps(st))


def main(dry):
    plan = json.loads((ROOT / "plan.json").read_text(encoding="utf-8"))
    st = load_state()
    if dry:
        with sync_playwright() as p:
            br = p.chromium.launch(); page = br.new_page(viewport={"width": 1080, "height": 1920})
            for v in plan[st["next"]: st["next"] + 3]:
                print("تم:", render.render_video(page, v).name)
            br.close()
        return
    while True:
        v = plan[st["next"] % len(plan)]
        if v["long"] and not ALLOW_LONG:
            with SKIPPED.open("a", encoding="utf-8") as f:
                f.write(f"سورة {v['surah_name']} الآية {v['from']} ({v['duration']}ث) - دورة {st['cycle']}\n")
            print("تخطي آية طويلة:", v["surah_name"], v["from"]); advance(st, plan); continue
        break
    with sync_playwright() as p:
        br = p.chromium.launch(); page = br.new_page(viewport={"width": 1080, "height": 1920})
        path = render.render_video(page, v); br.close()
    mid = publish.post_reel(path, v["caption"], os.environ["IG_USER_ID"], os.environ["IG_ACCESS_TOKEN"])
    advance(st, plan)                       # يُحفظ التقدم فور نجاح النشر
    print("نُشر", v["file"], "->", mid)


if __name__ == "__main__":
    main("--dry-run" in sys.argv)
