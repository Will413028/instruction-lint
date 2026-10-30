"""Shared error type and small schema helpers for configuration validation."""
from __future__ import annotations

from typing import Any, Iterable


class ConfigError(Exception):
    """The configuration (or an allowlist entry) is invalid. The CLI exits with 2."""


def check_keys(table: Any, allowed: Iterable[str], where: str) -> None:
    """Fail on non-table values and on any key not in `allowed` (typos must not pass silently)."""
    if not isinstance(table, dict):
        raise ConfigError(f"{where}: expected a table")
    allowed = set(allowed)
    unknown = sorted(set(table) - allowed)
    if unknown:
        raise ConfigError(
            f"{where}: unknown key(s) {', '.join(unknown)} (allowed: {', '.join(sorted(allowed))})"
        )


def expect_int(value: Any, where: str, minimum: int = 1) -> int:
    # bool is a subclass of int; reject it explicitly.
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ConfigError(f"{where}: expected an integer >= {minimum}")
    return value


def expect_str(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{where}: expected a non-empty string")
    return value


def expect_str_list(value: Any, where: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ConfigError(f"{where}: expected a non-empty list of strings")
    return [expect_str(v, f"{where}[{i}]") for i, v in enumerate(value)]
