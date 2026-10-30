# Changelog

All notable changes are listed here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-10-31

### Added

- Rule R1 (size): byte limit by path depth, per-line character limit, excluded marker blocks.
- Allowlist: time-boxed exceptions with a reason and an expiry date; expired, no-longer-needed and
  soon-to-expire entries are reported; `max_days` and `max_entries` bounds.
- Discovery: `git ls-files` entries matching configurable globs, never `*.local.md`; command-line
  file names only decide whether to run.
- `instruction-lint vendor --to DIR`: a reproducible, self-contained copy of the runner with an
  entry script, `verify.py` and a README manifest (upstream tag, commit, SHA-256 per file).
- `--version`, `--list-rules`, `--today`, `--warn-as-error`, `--config`.
