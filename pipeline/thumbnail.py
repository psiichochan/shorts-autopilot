"""Thumbnail / cover agent: one designed cover per video, built from the video's own best frame + its hook.

Research (reports/market-research-2026-11-13, owner rule 15 Nov 2026 "every Short and Reel gets its own thumbnail"):
  - Instagram: custom 9:16 cover, subject centred, 3-5 big words; must still read when the grid crops it to 3:4
    and 1:1, so the text sits inside the centre square. Same style across the series.
  - YouTube Shorts: frame 1 is what the feed shows (the boxed hook headline already covers that); a custom
    thumbnail still shows on the channel page, search and suggested. Long-form needs a real 16:9 thumbnail.

Outputs next to video.mp4:
  cover.jpg     1080x1920 (Instagram cover, YouTube Shorts thumbnail)
  thumb.jpg     1280x720  (YouTube long-form thumbnail)
The text is youtube.hook_text (already fact-checked with the title), never a new claim. If it is longer than
cover_max_words, the cover carries no text rather than a truncated claim.
"""
import re
import subprocess
import tempfile
from pathlib import Path

from .util import ASSETS, log, media_duration

YELLOW = (255, 214, 0)
WHITE = (255, 255, 255)


def _font(size):
    from PIL import ImageFont
    return ImageFont.truetype(str(ASSETS / "fonts" / "Poppins-Bold.ttf"), size)


def cover_text(script, max_words=6):
    yt = script.get("youtube", {})
    for cand in (yt.get("hook_text"), re.sub(r"\s*#\w+", "", yt.get("title", ""))):
        words = str(cand or "").replace("\n", " ").split()
        if 2 <= len(words) <= max_words:
            return " ".join(words).upper().rstrip(".")
    return ""


def _key_word(words):
    """The word to colour: a number if there is one, else the longest word (the concrete noun, usually)."""
    nums = [i for i, w in enumerate(words) if re.search(r"\d", w)]
    if nums:
        return nums[0]
    return max(range(len(words)), key=lambda i: len(re.sub(r"\W", "", words[i])))


def _frame_score(img):
    """Sharp, contrasty, not dark: what reads at thumbnail size."""
    from PIL import ImageFilter, ImageStat
    g = img.convert("L").resize((216, 384))
    edges = ImageStat.Stat(g.filter(ImageFilter.FIND_EDGES)).mean[0]
    st = ImageStat.Stat(g)
    bright = st.mean[0]
    return edges * 2 + st.stddev[0] - (40 if bright < 45 else 0) - (40 if bright > 225 else 0)


def best_frame(video, samples=8, skip=3.2):
    """Best of `samples` frames after the hook headline is gone (so the cover's text isn't printed twice)."""
    from PIL import Image
    dur = media_duration(video)
    lo, hi = min(skip, dur * 0.3), max(min(dur - 1.0, 40.0), min(skip, dur * 0.3) + 0.5)
    best, best_s = None, -1e9
    with tempfile.TemporaryDirectory() as td:
        for k in range(samples):
            t = lo + (hi - lo) * (k + 0.5) / samples
            p = Path(td) / f"f{k}.png"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1",
                            str(p)], check=False, timeout=60)
            if not p.exists():
                continue
            img = Image.open(p).convert("RGB")
            s = _frame_score(img)
            if s > best_s:
                best, best_s = img.copy(), s
    return best


def _fit(img, W, H):
    from PIL import ImageOps
    return ImageOps.fit(img, (W, H), method=3, centering=(0.5, 0.45))


def _draw_text(canvas, text, box, max_size, align="center"):
    """Big bold words, wrapped to fit `box` (x0, y0, x1, y1), black stroke, key word in yellow."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(canvas)
    words = text.split()
    if not words:
        return
    key = _key_word(words)
    x0, y0, x1, y1 = box
    for size in range(max_size, 40, -6):
        f = _font(size)
        lines, cur = [], []
        for i, w in enumerate(words):
            trial = " ".join(words[j] for j in cur + [i])
            if cur and d.textlength(trial, font=f) > (x1 - x0):
                lines.append(cur)
                cur = [i]
            else:
                cur.append(i)
        lines.append(cur)
        lh = int(size * 1.08)
        if len(lines) * lh <= (y1 - y0) and all(d.textlength(" ".join(words[j] for j in ln), font=f) <= x1 - x0
                                                for ln in lines):
            break
    stroke = max(4, size // 12)
    y = y0 + ((y1 - y0) - len(lines) * lh) // 2
    space = d.textlength(" ", font=f)
    for ln in lines:
        width = d.textlength(" ".join(words[j] for j in ln), font=f)
        x = x0 + ((x1 - x0) - width) / 2 if align == "center" else x0
        for j in ln:
            d.text((x, y), words[j], font=f, fill=YELLOW if j == key else WHITE,
                   stroke_width=stroke, stroke_fill=(0, 0, 0))
            x += d.textlength(words[j], font=f) + space
        y += lh


def _shade(canvas, y0, y1, strength=150):
    """Darken a horizontal band softly so white text reads on any picture."""
    from PIL import Image, ImageDraw
    W, H = canvas.size
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    pad = (y1 - y0) // 2
    for y in range(max(0, y0 - pad), min(H, y1 + pad)):
        dist = 0 if y0 <= y <= y1 else min(abs(y - y0), abs(y - y1)) / pad
        d.line([(0, y), (W, y)], fill=int(strength * (1 - dist)))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    canvas.paste(black, (0, 0), m)


# In a finished video the word captions sit at about y 1130-1300 and the hook headline at y 260-400 (1080x1920);
# between them is clean picture. Used when the caption-free render (work/base.mp4) is no longer on disk.
CLEAN_BAND = (0, 420, 1080, 1110)


def make(video, script, cfg, out_dir=None, clean_video=None):
    """→ {"cover": path, "thumb": path, "text": str} or {} when no frame could be read.
    clean_video: the render before captions were burned in (orchestrator passes work/base.mp4)."""
    from PIL import Image, ImageFilter
    video = Path(video)
    out_dir = Path(out_dir or video.parent)
    t_cfg = cfg.get("thumbnail", {})
    if not t_cfg.get("enabled", True):
        return {}
    clean = clean_video and Path(clean_video).exists()
    frame = best_frame(Path(clean_video) if clean else video, skip=0.5 if clean else 3.2)
    if frame is None:
        log(f"thumbnail: no frame readable from {video.name}")
        return {}
    if not clean:  # keep only the picture between the headline and the caption band
        sx, sy = frame.width / 1080, frame.height / 1920
        frame = frame.crop((int(CLEAN_BAND[0] * sx), int(CLEAN_BAND[1] * sy),
                            int(CLEAN_BAND[2] * sx), int(CLEAN_BAND[3] * sy)))
    text = cover_text(script, t_cfg.get("cover_max_words", 6))

    # 9:16 cover: text inside the centre square (survives the 3:4 and 1:1 grid crops)
    if clean:
        cover = _fit(frame, 1080, 1920)
        if text:
            _shade(cover, 690, 1060)
            _draw_text(cover, text, (90, 660, 990, 1090), 150)
    else:  # blurred fill, the clean band large in the lower centre, text above it
        cover = _fit(frame, 1080, 1920).filter(ImageFilter.GaussianBlur(30))
        cover = Image.blend(cover, Image.new("RGB", cover.size, (0, 0, 0)), 0.35)
        band = _fit(frame, 1080, int(1080 * frame.height / frame.width))
        top = 1500 - band.height if text else (1920 - band.height) // 2
        cover.paste(band, (0, max(0, top)))
        if text:
            _draw_text(cover, text, (70, 430, 1010, max(500, top - 30)), 140)
    cover_p = out_dir / "cover.jpg"
    cover.convert("RGB").save(cover_p, quality=90, optimize=True)

    # 16:9 thumbnail: the picture on the right, text on a darkened left
    pic = _fit(frame, 1280, 720)
    thumb = pic.copy()
    if text:
        from PIL import ImageDraw
        m = Image.new("L", (1280, 720), 0)
        d = ImageDraw.Draw(m)
        for x in range(0, 760):
            d.line([(x, 0), (x, 720)], fill=int(190 * min(1, (760 - x) / 260)))
        thumb.paste(Image.new("RGB", (1280, 720), (0, 0, 0)), (0, 0), m)
        _draw_text(thumb, text, (40, 90, 680, 630), 130)
    thumb_p = out_dir / "thumb.jpg"
    thumb.convert("RGB").save(thumb_p, quality=90, optimize=True)
    for p in (cover_p, thumb_p):  # YouTube's limit is 2 MB
        q = 85
        while p.stat().st_size > 1_900_000 and q > 50:
            Image.open(p).save(p, quality=q)
            q -= 10
    log(f"thumbnail: cover + thumb for {video.parent.name} ({text or 'no text'}{'' if clean else ', from final video'})")
    return {"cover": str(cover_p), "thumb": str(thumb_p), "text": text}


def upload_youtube(yt, video_id, files, duration_s, cfg):
    """Sets the custom thumbnail (needs a phone-verified channel; 50 quota units). Never fails the upload."""
    if not cfg.get("thumbnail", {}).get("youtube_set", True) or not files:
        return False
    from googleapiclient.http import MediaFileUpload
    path = files.get("thumb") if duration_s and duration_s > 180 else files.get("cover")
    if not path or not Path(path).exists():
        return False
    try:
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(path, mimetype="image/jpeg")).execute()
        log(f"thumbnail set on {video_id}")
        return True
    except Exception as e:  # e.g. 403 when the channel isn't verified for custom thumbnails
        log(f"thumbnail not set on {video_id}: {str(e)[:200]}")
        return False
