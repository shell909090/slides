#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path

from generate import PLAN, ROOT, get_setting


OUTPUT = ROOT / "assets" / "llms-qr.svg"


def main() -> None:
    if not shutil.which("uvx"):
        raise RuntimeError("找不到 uvx，无法生成二维码")
    source = PLAN.read_text(encoding="utf-8")
    url = get_setting(source, "llms_url")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "uvx", "--from", "segno==1.6.6", "segno", url,
        "--error", "H", "--scale", "12", "--border", "4",
        "--dark", "#17221f", "--light", "#fffdf7",
        "--title", "PyCon 2026 llms.txt",
        "--desc", url,
        "--output", str(OUTPUT),
    ], check=True)
    print(f"generated {OUTPUT.relative_to(ROOT)} -> {url}")


if __name__ == "__main__":
    main()
