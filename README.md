# instruction-lint

A linter for agent instruction files (`AGENTS.md`, `CLAUDE.md`). Rules and limits live in one
TOML file; the runner is a thin Python program that uses only the standard library
(Python 3.11 or newer). A local git hook and CI call the same program with the same config.

Status: walking skeleton (version 0.0.0). One rule exists so far.

| Rule | Level (default) | What it checks |
|---|---|---|
| `R1` | error | byte limit per path-depth tier (root, depth 1, deeper) and a character limit per line; optional marker blocks (for example text a tool injects) are not counted |
| `allowlist` | error | time-boxed exceptions: expired or no-longer-needed entries fail, entries warn before they expire |

## Usage

```sh
python3 -m instruction_lint            # from a git repository; analyzes tracked files only
instruction-lint --list-rules          # rules and their effective levels
instruction-lint --today 2026-01-31    # replace the current date (reproducible runs)
instruction-lint --config path.toml    # explicit config instead of .instruction-lint.toml
instruction-lint --warn-as-error
```

Output is one line per finding: `file:line: rule-id: message`. Findings about a whole file use
line `0` (printed as `:0`). Errors go to stderr, warnings to stdout. Exit codes: `0` no errors,
`1` at least one error, `2` usage or configuration problem.

Files given on the command line only decide whether to run at all; the full tracked set is
always analyzed (cross-file checks and allowlist checks need it). Untracked local instruction
files (`*.local.md`) are never analyzed.

## Configuration

`.instruction-lint.toml` at the repository root extends the shipped preset. Unknown keys fail.

```toml
extends = ["preset:default"]        # default; other entries are paths relative to this file

[discover]
globs = ["AGENTS.md", "**/AGENTS.md"]

[rules.R1]
level = "error"                     # error | warn | off
max_line_chars = 500
excluded_blocks = [{ begin = "<!-- BEGIN:x -->", end = "<!-- END:x -->" }]

[rules.R1.max_bytes]
root = 12000
subproject = 10000
nested = 6000

[allowlist]
max_days = 90

[[allowlist.entries]]
rule = "R1"
path = "docs/AGENTS.md"
reason = "split planned in the tracker"
expires = 2026-12-31
```

## Install and wire up

pre-commit:

```yaml
- repo: https://github.com/Will413028/instruction-lint
  rev: <tag or full commit SHA>
  hooks:
    - id: instruction-lint
```

GitHub Actions (pin to a full commit SHA):

```yaml
- uses: actions/checkout@<sha>
- uses: Will413028/instruction-lint@<sha>
```

Development: `make check` runs the unit tests (needs Python 3.11+, override with `PYTHON=...`).
Design notes are in `docs/design.md`, decisions in `docs/adr/`.

## License

MIT, see `LICENSE`.
