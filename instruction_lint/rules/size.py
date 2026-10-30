"""R1: size limits. A byte limit per path-depth tier and a character limit per line."""
from __future__ import annotations

import re
from typing import Any

from ..errors import ConfigError, check_keys, expect_int, expect_str
from ..finding import Finding

ID = "R1"
NAME = "size"
DESCRIPTION = "byte limit per path-depth tier and character limit per line"

_TIERS = ("root", "subproject", "nested")


def validate(params: dict[str, Any]) -> dict[str, Any]:
    where = f"rules.{ID}"
    check_keys(params, {"level", "max_line_chars", "max_bytes", "excluded_blocks"}, where)
    for key in ("max_line_chars", "max_bytes", "excluded_blocks"):
        if key not in params:
            raise ConfigError(f"{where}: missing key {key}")
    expect_int(params["max_line_chars"], f"{where}.max_line_chars")
    check_keys(params["max_bytes"], _TIERS, f"{where}.max_bytes")
    for tier in _TIERS:
        if tier not in params["max_bytes"]:
            raise ConfigError(f"{where}.max_bytes: missing key {tier}")
        expect_int(params["max_bytes"][tier], f"{where}.max_bytes.{tier}")
    blocks = params["excluded_blocks"]
    if not isinstance(blocks, list):
        raise ConfigError(f"{where}.excluded_blocks: expected a list of {{begin, end}} tables")
    for i, block in enumerate(blocks):
        check_keys(block, {"begin", "end"}, f"{where}.excluded_blocks[{i}]")
        for key in ("begin", "end"):
            if key not in block:
                raise ConfigError(f"{where}.excluded_blocks[{i}]: missing key {key}")
            expect_str(block[key], f"{where}.excluded_blocks[{i}].{key}")
    return params


def _block_patterns(params: dict[str, Any]) -> list[re.Pattern[str]]:
    # Same shape as a hand-written `BEGIN.*?END\n?` with DOTALL: the block and one trailing newline.
    return [
        re.compile(re.escape(b["begin"]) + ".*?" + re.escape(b["end"]) + "\n?", re.DOTALL)
        for b in params["excluded_blocks"]
    ]


def limit_for(path: str, params: dict[str, Any]) -> int:
    depth = path.count("/")
    tiers = params["max_bytes"]
    if depth == 0:
        return tiers["root"]
    if depth == 1:
        return tiers["subproject"]
    return tiers["nested"]


def check(path: str, text: str, params: dict[str, Any]) -> list[Finding]:
    body = text
    for pattern in _block_patterns(params):
        body = pattern.sub("", body)
    found: list[Finding] = []
    size = len(body.encode("utf-8"))  # bytes after block removal
    limit = limit_for(path, params)
    if size > limit:
        found.append(Finding(path, 0, ID, f"file is {size} bytes, limit {limit}"))
    max_chars = params["max_line_chars"]
    # Line numbers count on the body after block removal; length is in characters.
    for number, line in enumerate(body.splitlines(), start=1):
        if len(line) > max_chars:
            found.append(Finding(path, number, ID, f"line is {len(line)} characters, limit {max_chars}"))
    return found
