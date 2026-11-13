"""نشر Reel على إنستغرام عبر Instagram API (تسجيل الدخول عبر Instagram)."""
import os, time, pathlib, requests

GRAPH = os.environ.get("IG_GRAPH", "https://graph.instagram.com/v25.0")
RUPLOAD = os.environ.get("IG_RUPLOAD", "https://rupload.facebook.com/ig-api-upload/v25.0")


def post_reel(path, caption, ig_id, token):
    path = pathlib.Path(path)
    r = requests.post(f"{GRAPH}/{ig_id}/media", timeout=120, data={
        "media_type": "REELS", "upload_type": "resumable", "caption": caption,
        "share_to_feed": "true", "access_token": token})
    r.raise_for_status()
    cid = r.json()["id"]
    with open(path, "rb") as f:
        u = requests.post(f"{RUPLOAD}/{cid}", data=f, timeout=900,
                          headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(path.stat().st_size)})
    u.raise_for_status()
    for _ in range(60):                                   # حتى 30 دقيقة انتظار للمعالجة
        s = requests.get(f"{GRAPH}/{cid}", params={"fields": "status_code", "access_token": token}, timeout=60).json()
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"فشلت معالجة الفيديو: {s}")
        time.sleep(30)
    else:
        raise RuntimeError("انتهت مهلة المعالجة")
    p = requests.post(f"{GRAPH}/{ig_id}/media_publish", data={"creation_id": cid, "access_token": token}, timeout=120)
    p.raise_for_status()
    return p.json()["id"]


def refresh_token(token):
    """تمديد صلاحية الرمز 60 يومًا (يشترط أن يكون عمره أكثر من 24 ساعة)."""
    r = requests.get("https://graph.instagram.com/refresh_access_token", timeout=60,
                     params={"grant_type": "ig_refresh_token", "access_token": token})
    r.raise_for_status()
    return r.json()["access_token"]
