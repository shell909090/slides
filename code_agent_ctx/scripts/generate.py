#!/usr/bin/env python3

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "pycon2026-slide.md"
TALK = ROOT / "talk.qmd"
TTS_MANIFEST = ROOT / "audio" / "tts-manifest.json"

HEADER = """---
pagetitle: "Code Agent 的 Context——从 API、Agent Loop 到缓存与协作"
lang: zh-CN
format:
  revealjs:
    width: 1600
    height: 900
    margin: 0
    center: false
    controls: false
    progress: false
    slide-number: false
    transition: fade
    background-transition: fade
    hash: true
    css: talk.css
    include-in-header: header.html
---
"""


def extract_slides(source: str) -> list[dict[str, str]]:
    starts = list(re.finditer(r"<!-- slide:([a-z0-9-]+) -->", source))
    slides = []
    for index, match in enumerate(starts):
        slide_id = match.group(1)
        end = starts[index + 1].start() if index + 1 < len(starts) else len(source)
        body = source[match.end():end]
        visual = re.search(r"````qmd\n(.*?)\n````", body, re.DOTALL)
        narration = re.search(r"### 演讲词（TTS）\n\n(.*)\Z", body, re.DOTALL)
        if not visual or not narration:
            raise ValueError(f"slide {slide_id} 缺少展示内容或演讲词")
        narration_text = narration.group(1).strip()
        if narration_text == "<!-- no-tts -->":
            narration_text = ""
        slides.append({
            "id": slide_id,
            "visual": visual.group(1).strip(),
            "narration": narration_text,
        })
    if not slides:
        raise ValueError("没有找到 slide 定义")
    return slides


def get_setting(source: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}:\s*[\"']?([^\"'\n]+)[\"']?\s*$", source, re.MULTILINE)
    if not match:
        raise ValueError(f"缺少设置 {name}")
    return match.group(1).strip()


def apply_pronunciations(source: str, text: str) -> str:
    pronunciations = [
        ("JSON", get_setting(source, "tts_pronounce_JSON")),
        ("Qwen3", get_setting(source, "tts_pronounce_Qwen3")),
        ("Qwen", get_setting(source, "tts_pronounce_Qwen")),
        ("run_python", get_setting(source, "tts_pronounce_run_python")),
        ("IDs", get_setting(source, "tts_pronounce_IDs")),
        ("ID", get_setting(source, "tts_pronounce_ID")),
    ]
    for term, replacement in pronunciations:
        text = re.sub(
            rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])",
            replacement,
            text,
        )
    return text


def get_audio_metadata(path: Path) -> tuple[str | None, float | None]:
    if not path.exists():
        return None, None
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if not shutil.which("ffprobe"):
        return digest, None
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], check=True, capture_output=True, text=True)
    return digest, round(float(result.stdout.strip()), 3)


def main() -> None:
    source = PLAN.read_text(encoding="utf-8")
    slides = extract_slides(source)
    provider = get_setting(source, "tts_provider")
    version = get_setting(source, "tts_version")
    voice = get_setting(source, "tts_voice")
    rate = get_setting(source, "tts_rate")
    qmd_parts = [HEADER.rstrip()]
    manifest = []
    for slide in slides:
        audio_path = ROOT / "audio" / f"{slide['id']}.mp3"
        synthesis_text = apply_pronunciations(source, slide["narration"])
        visual = slide["visual"].replace("{{LLMS_URL}}", get_setting(source, "llms_url"))
        has_audio = bool(slide["narration"] and audio_path.exists())
        audio_sha256, duration_seconds = get_audio_metadata(audio_path) if has_audio else (None, None)
        if has_audio:
            visual += f'\n\n<audio class="slide-audio" controls preload="auto" src="audio/{audio_path.name}"></audio>'
        qmd_parts.append(visual)
        if slide["narration"]:
            qmd_parts.append("::: {.notes}\n" + slide["narration"] + "\n:::")
        manifest.append({
            "id": slide["id"],
            "text": slide["narration"],
            "narration_sha256": hashlib.sha256(slide["narration"].encode()).hexdigest(),
            "synthesis_text": synthesis_text,
            "synthesis_sha256": hashlib.sha256(synthesis_text.encode()).hexdigest(),
            "audio": f"audio/{slide['id']}.mp3",
            "audio_exists": has_audio,
            "audio_sha256": audio_sha256,
            "duration_seconds": duration_seconds,
            "provider": provider,
            "version": version,
            "voice": voice,
            "rate": rate,
        })

    TALK.write_text("\n\n".join(qmd_parts) + "\n", encoding="utf-8")
    TTS_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    TTS_MANIFEST.write_text(
        json.dumps({"slides": manifest}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"generated {TALK.relative_to(ROOT)} ({len(slides)} slides)")
    print(f"generated {TTS_MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
