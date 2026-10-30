import time
import unittest

import helpers

LIMIT_SECONDS = 1.0


class PerfTest(unittest.TestCase):
    def test_full_scan_of_46_files_under_one_second(self):
        files = {"AGENTS.md": ("line of text\n" * 300)}
        for i in range(45):
            files[f"mod{i // 5}/sub{i}/AGENTS.md"] = "line of text\n" * 200
        root = helpers.make_repo(files)
        self.assertEqual(len(files), 46)
        best = None
        for _ in range(3):
            start = time.perf_counter()
            r = helpers.run_new(root)
            elapsed = time.perf_counter() - start
            self.assertEqual(r.returncode, 0, r.stderr)
            best = elapsed if best is None else min(best, elapsed)
        print(f"\nfull scan of 46 files (process start included, best of 3): {best:.3f} s (limit {LIMIT_SECONDS} s)")
        self.assertLess(best, LIMIT_SECONDS)


if __name__ == "__main__":
    unittest.main()
