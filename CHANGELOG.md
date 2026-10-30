# Changelog

All notable changes are listed here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [0.2.1] - 2026-10-31

### Changed

- The README written by `instruction-lint vendor` now has an "Upgrades" section that documents the upgrade
  path (regenerate from a newer tag, open a pull request, review the diff), so a vendored copy needs no hand edits.

## [0.2.0] - 2026-10-31

### Added

- Rule R2 (shape): required section headings, exact or ordered, plus optional title, one-line purpose,
  bullet-only sections and must-match patterns, per glob.
- Rule R3a (test-names): a backticked test name must be defined in a tracked test file (Go and Python
  patterns in the preset).
- Rule R3b (path-refs): a backticked path must exist; resolved against the file's directory, its
  ancestors, the root and configured `base_dirs` (heuristic).
- Rule R3c (spec-refs): `§N` references must match a numbered heading of the spec document mapped to the file.
- Rule R4 (rot): dates and issue numbers at the rule level, narrative words at `narrative_level`.
- Rule R5 (duplicates): identical lines in ancestor/descendant files at the rule level, in sibling
  files at `sibling_level`; always compares the full tracked set.
- Rule R6 (constants): copied-constant candidates, always warnings.
- Rule C1 (claude-md): `import-only` (default) or `forbid`.
- `instruction-lint check-pins`: every reference to this tool (pre-commit `rev:`, `uvx --from git+...@`,
  `uses: owner/instruction-lint@`) must pin the same full 40-hex SHA; reports `file:line`.
- `instruction-lint config --format json`: the effective merged configuration as deterministic JSON.
- `rubric.md` and `docs/pr-template-snippet.md` for the judgment checks that do not run in CI;
  `docs/versioning.md` for the release and upgrade process.
- Findings may carry their own level (a rule at `error` can still report some findings as warnings);
  the rule level only caps them.

### Changed

- All new rules enter the default preset at `warn`. A rule whose own spec says `error` (R2, R3a, R4
  dates and issue numbers, R5 ancestor/descendant, C1) is raised per repository with `level = "error"`.
- R1 output format, exit codes and limits are unchanged.

### Graduated

Rules above `warn` in the default preset. Everything not listed here must start at `warn`
(`tests/test_versioning.py` enforces it).

- `R1`: shipped at `error` in 0.1.0, before the warn-first policy.

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
