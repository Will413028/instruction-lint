"""Temporary contract leg (remove after adoption): the pinned public checkout must pass both tools.

Skipped unless HAWKR_CHECKOUT points at a checkout of the public hawkr repository at the
snapshot commit used for the legacy oracle (CI sets it in a dedicated job).
"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

import helpers

CHECKOUT = os.environ.get("HAWKR_CHECKOUT")


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


if __name__ == "__main__":
    unittest.main()
