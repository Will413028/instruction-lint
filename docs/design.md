# Design

## Problem

Agent instruction files are loaded whole whenever an agent works in their directory, so they
need budgets, and they rot: duplicated text, stale references, one-off exceptions that never
expire. A review checklist does not hold. A deterministic check that runs in the same way
locally and in CI does.

## Goals

- One rule file (TOML) plus a thin Python runner; no third-party dependencies at run time.
- The local hook and CI run the same program, the same rules, the same version.
- Three levels per rule: `error` (blocks), `warn` (prints), `off`.
- Exceptions are time-boxed: every allowlist entry has a reason and an expiry date, and the
  list can only shrink.
- Reproducible: same input and same injected date give the same output. No network, no telemetry.

## Non-goals

- No LLM in the gate (non-deterministic, paid, and the checked text is untrusted input).
- Not a Markdown style linter; it knows instruction-file semantics (tiers, budgets), not prose style.
- Untracked local instruction files (`*.local.md`) are out of scope; CI cannot see them.
- Not published to a package index. Distribution is a git repository (pre-commit hook, composite
  action, `uvx --from git+...`) and, later, a pinned vendored copy for restricted environments (see Vendored copy).

## Model

```
preset (shipped) <- repo config (.instruction-lint.toml, `extends`) -> effective config
effective config + git ls-files (full set) -> rules -> findings -> allowlist -> output + exit code
```

- Rules are data: a rule module reads parameters, and repo-specific behaviour is never a
  branch in code. Differences between repositories are config values.
- Merge: tables merge key by key (the child wins); every other value, lists included, is replaced.
- Unknown keys, unknown rule ids and malformed allowlist entries fail the configuration (exit 2).
  A typo must not silently disable a check.

## File discovery

Files are `git ls-files` entries matching `discover.globs` (default `AGENTS.md`, `**/AGENTS.md`,
`CLAUDE.md`, `**/CLAUDE.md`), never a file ending in `.local.md`, skipping files deleted in the
working tree. File names given on the command line only decide whether to run: cross-file rules
and the allowlist "no longer needed" check need the whole set, and a partial view would make
them pass locally and fail in CI. Hooks therefore use `pass_filenames: false`.

## Rule R1: size

- Byte limit by path depth of the file relative to the repo root: depth 0 (`root`), depth 1
  (`subproject`), deeper (`nested`). Depth is the number of `/` in the path.
- Per-line limit in characters.
- `excluded_blocks`: marker pairs; the text from a begin marker through the end marker (and one
  trailing newline) is removed before measuring.
- Exact semantics: files are read as UTF-8 in text mode (CRLF becomes LF); bytes are counted on
  the body after block removal; line length is in characters; a limit is exceeded when
  `measured > limit` (equal passes); line numbers count on the body after block removal.
  These match the checker this rule replaces; a contract test compares both on boundary fixtures.

## Allowlist

Each entry: `rule`, `path`, `reason`, `expires`.

- A live entry suppresses that rule's findings in that file.
- Expired (`expires` before today): error, and the finding is not suppressed. An entry that
  expires today is still live.
- No longer needed (the file does not violate the rule, or is not an analyzed file): error.
- Within `warn_days` (default 14) of expiry: warning "expires in N days".
- `max_days` (default 90): an `expires` later than today plus `max_days` fails the configuration.
- `max_entries` (default 10): more entries fail the configuration.
- Renewal means editing the config and writing a new reason; there are no inline suppressions.

Because expiry depends on the date, a repository with no commits can turn red. Run CI on a
weekly schedule so warnings appear before that happens.

## Output and exit codes

`file:line: rule-id: message`, one finding per line, sorted by file, line, rule. Line `0` means
the whole file and is printed as `:0` so the format has one shape. Errors go to stderr,
warnings to stdout. Exit `0`: no errors; `1`: at least one error; `2`: usage or configuration
problem. `--warn-as-error` promotes warnings. The format and exit codes are part of the
contract; changing them is a major version change.

## Verification strategy

- Unit tests per component (config, discovery, allowlist, CLI).
- Contract test: a frozen snapshot of the legacy checker runs next to the new tool on
  generated git repositories with boundary cases (limit, limit +/- 1 per tier, 500/501
  character lines, multibyte text, marker blocks). Both outputs are normalised to
  `(path, line, kind, measured, limit)` sets and compared together with exit codes. A mismatch
  means one of the two tools is wrong; the normalisation is not adjusted to hide it.
- A temporary second leg runs both tools on a pinned public checkout and expects exit 0 from both.
- Timing test: a full scan of 46 synthetic files finishes in under a second.
- Date-injection test: the same `--today` gives byte-identical output.
- CI matrix: Python 3.11 to 3.13 on Linux and macOS; the repository checks its own instruction
  files through the composite action.

## Vendored copy

For environments that cannot install from git, `instruction-lint vendor --to <dir>` writes one
self-contained directory: the runner package with the default preset, an entry script
(`instruction-lint.py`), `verify.py` and a `README.md` that records the upstream tag, the upstream
commit and a SHA-256 for every file. Options: `--ref-tag` / `--ref-commit` (default: the exact tag
and HEAD of the source checkout, else `untagged`), `--force` (replace a non-empty target).

- Run it from the repository root: `python3 <dir>/instruction-lint.py` (Python >= 3.11, standard
  library only, no network). Its output and exit codes equal `python3 -m instruction_lint`.
- The output is reproducible: same source and same two upstream values give a byte-identical tree
  (sorted order, fixed newlines, no timestamps, no machine paths or user names).
- `python3 <dir>/verify.py` recomputes the hashes and fails (exit 1, naming the file) on a
  modified, missing or unlisted file.

Known limitation: verification only detects accidental modification. A deliberate change can edit
the files and the manifest together, so it is not tamper-proof. The real gate is review of the
diff of the pull request that upgrades the vendored copy.

## Versioning

Semantic versions as git tags. New rules enter as `warn`; promoting a rule to `error` is a minor
change with a changelog entry; renaming or removing a rule id is a major change. Consumers pin
a full commit SHA with the version in a comment.
