#!/usr/bin/env python3
"""Build upload packages into dist/ (gitignored). Writes nothing outside dist/.

dist/claude-ai/<skill>.zip   one zip per skill for claude.ai > Customize > Skills > Upload.
                             Description swapped to the <=200 char version (claude.ai limit),
                             utm_source switched to claude-ai.
dist/openai-skills-only.zip  whole plugin for platform.openai.com/plugins > Skills only.
                             utm_source switched from plugin to chatgpt-plugin. No README from the repo
                             (neutral generated one), no .claude-plugin folder; fails if logo/icon are missing.
"""
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SKILLS = ROOT / "skills"
SHORT = json.loads((ROOT / "scripts/short_descriptions.json").read_text())
CLAUDE_AI_DESC_MAX = 200
SKIP = {"__pycache__", ".DS_Store", ".pytest_cache"}
FIXED_TIME = (2026, 10, 1, 0, 0, 0)


def add(zf: zipfile.ZipFile, arc: str, data: bytes) -> None:
    """Write one entry with a fixed timestamp and permissions (no local times or owners leak)."""
    info = zipfile.ZipInfo(arc, FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    info.create_system = 3
    zf.writestr(info, data)


def files_under(folder: Path) -> list[Path]:
    return sorted(p for p in folder.rglob("*") if p.is_file() and not p.is_symlink() and not SKIP & set(p.parts))


def with_short_description(text: str, short: str) -> str:
    if len(short) > CLAUDE_AI_DESC_MAX:
        raise ValueError(f"short description over {CLAUDE_AI_DESC_MAX} chars: {short[:40]}...")
    return re.sub(r"^description: .*$", lambda _: f"description: {short}", text, count=1, flags=re.M)


def build_claude_ai() -> list[Path]:
    out_dir = DIST / "claude-ai"
    out_dir.mkdir(parents=True, exist_ok=True)
    built = []
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        target = out_dir / f"{skill.name}.zip"
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files_under(skill):
                arc = Path(skill.name) / f.relative_to(skill)
                if f.name == "SKILL.md":
                    text = with_short_description(f.read_text(), SHORT[skill.name])
                    add(zf, arc.as_posix(), text.replace("utm_source=plugin", "utm_source=claude-ai").encode())
                else:
                    add(zf, arc.as_posix(), f.read_bytes())
        built.append(target)
    return built


NEUTRAL_README = """# Ripe Leads Cold Email Writer

Five skills for B2B cold email: writer, audit, ICP builder, deliverability check
(SPF, DKIM, DMARC) and reply handler.

Each skill lives in skills/<name>/SKILL.md. Licensed under MIT.
More: https://ripeleads.eu/?utm_source=chatgpt-plugin&utm_medium=readme&utm_campaign=cold-email-writer
"""
REQUIRED_ASSETS = [ROOT / "assets/logo.png", ROOT / "assets/icon.png"]


def build_openai() -> Path:
    missing = [str(p.relative_to(ROOT)) for p in REQUIRED_ASSETS if not p.is_file()]
    if missing:
        raise SystemExit(f"ERROR: OpenAI zip needs these files, missing: {', '.join(missing)}")
    target = DIST / "openai-skills-only.zip"
    members = sorted([ROOT / "plugin.json", ROOT / "LICENSE", *REQUIRED_ASSETS, *files_under(SKILLS)])
    entries = {}
    for f in members:
        arc = f.relative_to(ROOT).as_posix()
        if f.suffix in {".md", ".json"}:
            entries[arc] = f.read_text().replace("utm_source=plugin", "utm_source=chatgpt-plugin").encode()
        else:
            entries[arc] = f.read_bytes()
    entries["README.md"] = NEUTRAL_README.encode()
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for arc in sorted(entries):
            add(zf, arc, entries[arc])
    return target


def main() -> int:
    if DIST.exists():
        shutil.rmtree(DIST)
    for path in [*build_claude_ai(), build_openai()]:
        print(f"built {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
