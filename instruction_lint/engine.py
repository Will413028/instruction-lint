"""Run the enabled rules over the full instruction-file set."""
from __future__ import annotations

import datetime
from dataclasses import replace
from pathlib import Path

from . import allowlist, discover
from .config import Config
from .finding import Finding
from .rules import RULES


def analyze(root: Path, config: Config, today: datetime.date, warn_as_error: bool = False) -> list[Finding]:
    paths = discover.instruction_files(root, config.globs)
    findings: list[Finding] = []
    for path in paths:
        try:
            text = (root / path).read_text(encoding="utf-8")  # text mode, like the legacy checker
        except UnicodeDecodeError:
            findings.append(Finding(path, 0, "input", "file is not valid UTF-8"))
            continue
        for rule_id, module in RULES.items():
            params = config.rules[rule_id]
            level = params["level"]
            if level == "off":
                continue
            for f in module.check(path, text, params):
                findings.append(replace(f, level=level))
    findings = allowlist.apply(findings, config.entries, config.allowlist, set(paths), today)
    if warn_as_error:
        findings = [replace(f, level="error") for f in findings]
    return sorted(findings, key=Finding.sort_key)
