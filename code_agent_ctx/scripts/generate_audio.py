#!/usr/bin/env python3

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from generate import PLAN, ROOT, apply_pronunciations, extract_slides, get_setting


STATE = ROOT / "audio" / "tts-state.json"


def main() -> None:
    if not shutil.which("uvx"):
        raise RuntimeError("找不到 uvx，无法运行 edge-tts")

    source = PLAN.read_text(encoding="utf-8")
    slides = extract_slides(source)
    version = get_setting(source, "tts_version")
    voice = get_setting(source, "tts_voice")
    rate = get_setting(source, "tts_rate")
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    next_state = {}

    for slide in slides:
        narration = slide["narration"]
        if not narration:
            continue
        text = apply_pronunciations(source, narration)
        output = ROOT / "audio" / f"{slide['id']}.mp3"
        cache_key = hashlib.sha256(
            json.dumps([version, voice, rate, text], ensure_ascii=False).encode()
        ).hexdigest()
        if output.exists() and state.get(slide["id"]) == cache_key:
            print(f"cached {output.relative_to(ROOT)}")
        else:
            subprocess.run([
                "uvx", "--from", f"edge-tts=={version}", "edge-tts",
                "--voice", voice,
                f"--rate={rate}",
                "--text", text,
                "--write-media", str(output),
            ], check=True)
            print(f"generated {output.relative_to(ROOT)}")
        next_state[slide["id"]] = cache_key

    STATE.write_text(json.dumps(next_state, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
