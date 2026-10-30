"""Rule registry. Each rule module exposes ID, NAME, DESCRIPTION, validate() and check()."""
from __future__ import annotations

from . import size

RULES = {rule.ID: rule for rule in (size,)}
