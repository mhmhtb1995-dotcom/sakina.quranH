"""يحمّل النص والصوت ويبني plan.json (خطة كل الفيديوهات). شغّله مرة واحدة."""
import json, pathlib, subprocess, time, requests
from config import *

API = "https://api.quran.com/api/v4"
AUDIO_URL = "https://everyayah.com/data/{folder}/{s:03d}{a:03d}.mp3"
ROOT = pathlib.Path(__file__).parent
AUDIO_DIR = ROOT / "build" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def get(url):
    for i in range(6):
        try:
            r = requests.get(url, timeout=90); r.raise_for_status(); return r
        except Exception:
            time.sleep(2 * (i + 1))
    raise RuntimeError("فشل التحميل: " + url)


def duration(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "default=nw=1:nk=1", str(path)]))


def audio_for(s, a):
    p = AUDIO_DIR / f"{s:03d}{a:03d}.mp3"
    if not p.exists():
        p.write_bytes(get(AUDIO_URL.format(folder=RECITER_FOLDER, s=s, a=a)).content)
    return p


def pack(groups, max_total=MAX_TOTAL_SECONDS):
    """يجمع آيات كاملة متتالية في فيديو واحد دون تقسيم أي آية."""
    videos, cur, cur_t = [], [], 0.0
    for g in groups:
        gt = sum(u["dur"] + GAP for u in g)
        if gt > max_total:
            if cur:
                videos.append((cur, False)); cur, cur_t = [], 0.0
            videos.append((g, True)); continue
        if cur_t + gt > max_total:
            videos.append((cur, False)); cur, cur_t = [], 0.0
        cur += g; cur_t += gt
    if cur:
        videos.append((cur, False))
    return videos


def main():
    chapters = get(f"{API}/chapters?language=ar").json()["chapters"]
    bism_text = get(f"{API}/quran/verses/uthmani?chapter_number=1").json()["verses"][0]["text_uthmani"]
    plan, vid = [], 0
    for ch in chapters:
        s, name = ch["id"], ch["name_arabic"]
        verses = get(f"{API}/quran/verses/uthmani?chapter_number={s}").json()["verses"]
        assert len(verses) == ch["verses_count"], f"عدد آيات سورة {s} غير مطابق"
        groups = []
        for v in verses:
            a = int(v["verse_key"].split(":")[1])
            p = audio_for(s, a)
            unit = {"surah": s, "ayah": a, "text": v["text_uthmani"], "dur": duration(p)}
            if a == 1 and s not in (1, 9):          # البسملة تُلحق بأول آية دائمًا
                bp = audio_for(1, 1)
                groups.append([{"surah": s, "ayah": 0, "text": bism_text, "dur": duration(bp)}, unit])
            else:
                groups.append([unit])
        for units, is_long in pack(groups):
            t = 0.0
            for u in units:
                u["start"] = round(t, 3); t += u["dur"] + GAP; u["end"] = round(t, 3)
            ayahs = [u["ayah"] for u in units if u["ayah"] > 0]
            a1, a2 = ayahs[0], ayahs[-1]
            rng = f"الآية {a1}" if a1 == a2 else f"الآيات {a1}-{a2}"
            vid += 1
            plan.append({"id": vid, "surah": s, "surah_name": name, "from": a1, "to": a2,
                         "file": f"{vid:05d}_s{s:03d}_{a1:03d}-{a2:03d}.mp4", "duration": round(t, 2),
                         "long": is_long, "items": units,
                         "caption": f"سورة {name} | {rng}\n🎧 {RECITER_NAME_AR}\n\n{HASHTAGS}"})
        print(f"سورة {s} ✓", end="\r")
    (ROOT / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    longs = [p for p in plan if p["long"]]
    print(f"\nعدد الفيديوهات: {len(plan)}  |  آيات أطول من الحد: {len(longs)}")
    for p in longs:
        print(f"  - سورة {p['surah_name']} الآية {p['from']} : {p['duration']} ثانية")


if __name__ == "__main__":
    main()
