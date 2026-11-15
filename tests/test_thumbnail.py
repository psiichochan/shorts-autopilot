"""Per-video cover/thumbnail (owner rule 15 Nov 2026) and the research title gate."""
import shutil
import subprocess

import pytest

from pipeline import thumbnail, virality


def test_cover_text_uses_hook_and_never_truncates_a_claim():
    s = {"youtube": {"hook_text": "2,400 degrees Fahrenheit", "title": "x"}}
    assert thumbnail.cover_text(s) == "2,400 DEGREES FAHRENHEIT"
    long = {"youtube": {"hook_text": "one two three four five six seven eight", "title": "A b c d e f g h i #Shorts"}}
    assert thumbnail.cover_text(long) == ""
    fallback = {"youtube": {"hook_text": "", "title": "Mars Is Pulling Its Moon Apart #Shorts"}}
    assert thumbnail.cover_text(fallback) == "MARS IS PULLING ITS MOON APART"


def test_key_word_prefers_numbers():
    assert thumbnail._key_word(["THE", "2,400", "DEGREES"]) == 1
    assert thumbnail._key_word(["THE", "GALVESTON", "STORM"]) == 1


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="needs ffmpeg")
def test_make_writes_cover_and_thumb(tmp_path):
    v = tmp_path / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=1080x1920:rate=10",
                    "-t", "6", "-pix_fmt", "yuv420p", str(v)], check=True)
    out = thumbnail.make(v, {"youtube": {"hook_text": "Saturn would float"}}, {})
    from PIL import Image
    assert Image.open(out["cover"]).size == (1080, 1920)
    assert Image.open(out["thumb"]).size == (1280, 720)
    assert thumbnail.make(v, {}, {"thumbnail": {"enabled": False}}) == {}


def _script(title):
    return {"youtube": {"title": title, "description": "x\n#Shorts #space #nasa"},
            "scenes": [{"text": "Why does Saturn float?"}, {"text": "Saturn would float in water."}]}


def test_research_title_gate():
    assert virality.score(_script("Facts About Saturn 7 #Shorts"), 40)["points"]["title"] == 0
    assert virality.score(_script("Saturn Would Float in 1 Bathtub 🪐🤯 #Shorts"), 40)["points"]["title"] == 0
    assert virality.score(_script("Saturn Would Float in 1 Bathtub 🪐 #Shorts"), 40)["points"]["title"] == 2
