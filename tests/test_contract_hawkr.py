"""Temporary contract leg (remove after adoption): the pinned public checkout must pass both tools.

A second test runs every rule, configured at the levels each rule's spec calls for
(tests/fixtures/hawkr-all-rules.toml), and writes the full report. Error-level hits are listed
here with a verdict; a new one means a rule bug or a regression and fails the test.

Skipped unless HAWKR_CHECKOUT points at a checkout of the public hawkr repository at the
snapshot commit used for the legacy oracle (CI sets it in a dedicated job).
"""
import collections
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

import helpers

CHECKOUT = os.environ.get("HAWKR_CHECKOUT")
ALL_RULES = helpers.FIXTURES / "hawkr-all-rules.toml"

# Error-level hits on the pinned checkout, each judged by hand as (rule, path).
EXPECTED_ERRORS = {
    # Real: the file has an eighth section between the fixed seven; cleanup is out of scope here.
    ("R2", "backend/internal/modules/accountsuspension/AGENTS.md"),
}


@unittest.skipUnless(CHECKOUT, "HAWKR_CHECKOUT not set")
class HawkrCheckoutTest(unittest.TestCase):
    def test_both_tools_exit_zero_on_the_pinned_checkout(self):
        root = Path(CHECKOUT)
        old = subprocess.run([sys.executable, str(helpers.LEGACY)], cwd=root, capture_output=True, text=True)
        new = helpers.run_new(root, "--config", str(helpers.HAWKR_LIMITS))
        print(f"\nlegacy exit={old.returncode} new exit={new.returncode}")
        self.assertEqual(old.returncode, 0, old.stderr)
        self.assertEqual(new.returncode, 0, new.stderr)
        self.assertEqual(new.stderr, "")

    def test_all_rules_report_on_the_pinned_checkout(self):
        root = Path(CHECKOUT)
        new = helpers.run_new(root, "--config", str(ALL_RULES))
        lines = [line for line in (new.stderr + new.stdout).splitlines() if line]
        counts = collections.Counter()
        errors = set()
        for line in new.stderr.splitlines():
            m = re.match(r"(?P<path>[^:]+):\d+: (?P<rule>[A-Za-z0-9]+): ", line)
            self.assertIsNotNone(m, line)
            errors.add((m.group("rule"), m.group("path")))
        for stream, level in ((new.stderr, "error"), (new.stdout, "warn")):
            for line in stream.splitlines():
                counts[(re.match(r"[^:]+:\d+: ([A-Za-z0-9]+):", line).group(1), level)] += 1
        summary = "\n".join(f"{rule} {level}: {n}" for (rule, level), n in sorted(counts.items()))
        report = Path(os.environ.get("HAWKR_REPORT", "")) if os.environ.get("HAWKR_REPORT") else None
        text = "\n".join(lines) + "\n\n# summary\n" + summary + "\n"
        if report:
            report.write_text(text, encoding="utf-8")
        print("\n" + summary)
        self.assertEqual(errors, EXPECTED_ERRORS, "new or vanished error-level hit: judge it (real issue or rule bug)")
        self.assertEqual(new.returncode, 1 if errors else 0)


if __name__ == "__main__":
    unittest.main()
