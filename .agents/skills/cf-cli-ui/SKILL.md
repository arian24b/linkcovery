---
name: cf-cli-ui
description: Restyle the terminal UI of a user's own CLI tool to look and behave like Cloudflare's `cf` CLI (banner, semantic palette, status lines, boxed errors, JSON output, prompts, NO_COLOR/TTY rules), and give it the shared command set (help, version, update, init, config). For Python CLIs use the `cfuicli` package (import `cfui`) instead of hand-rolling. Use when asked to make a CLI "cf-like", "Cloudflare style", unify CLI UI/UX, or add a new CLI to the arian24b tool family.
---

# cf-style CLI UI

Derived from the installed `cf` package (v1.0.0-beta.14, `dist/theme|banner|ui|output|prompt`), its README, and https://developers.cloudflare.com/cf/ . Source: https://github.com/cloudflare/cf (packages/cli). Re-check `~/.bun/install/global/node_modules/cf/dist/{theme,banner,ui,output}-*.mjs` if cf has been upgraded.

## Fast path: Python CLIs use `cfuicli`

`pip install cfuicli` (PyPI project `cfuicli`, import name `cfui`, stdlib-only, Python 3.12+). Source: https://github.com/arian24b/cfui. It already implements everything below (palette, helpers, banner, boxed errors, JSON, prompts, help layout, the common commands). Do not copy its code into a tool; depend on it.

```python
from cfui import App, Arg, Fail, ui
from cfui.common import YES, JSON, DRY_RUN, add_config, confirm, run_parallel

app = App(
    "tool",
    repo="https://github.com/me/tool",
    pypi="tool",
    description="Does things.",
)


@app.command(
    "greet",
    "Say hi",
    args=[Arg("--name", required=True, prompt="Your name"), JSON],
)
def greet(a):
    ui.data({"hello": a.name}) if a.json else ui.success(f"hi {a.name}")


def main():
    app.main()
```

What the app gives every tool for free:
- `help [command]` / `-h`, `version` / `-v` (name, version, git repo, Python), `update [--check]` (self update via uv/pipx/pip, override with `App(upgrade=fn)`), `-q/--quiet` (and `<TOOL>_QUIET`).
- A required option or positional (`Arg(..., required=True)`) is prompted for on a TTY and fails with `--flag is required. Pass --flag <value> or run interactively.` (exit 2) when piped or in CI. Never write your own wizard or TUI; ask only for what is missing.
- `sys.exit("message")` and `raise Fail(msg, hint)` become the boxed error; Ctrl-C exits 130.
- Groups (`app.group("config", ...)`), aliases, `default="count"` for single-command tools, `raw=True` for passthrough commands, `help_args=` / `Arg(group=...)` for grouped help.
- `cfui.common`: shared `YES/JSON/FORCE/DRY_RUN/JOBS/TIMEOUT/BACKGROUND` args, `confirm`, `parse_value`, `run_parallel`, and `add_config(...)` which registers `config show|get|set|reset|path|validate`.

If a tool already has its own `version` or `update` meaning (e.g. "update Throne"), rename that command (`app-update`, `update-models`, `upgrade`); `version` and `update` always mean the tool itself.

## Common command contract (every tool in the family)

| command / flag | meaning |
|---|---|
| `help [command]`, `-h/--help` | cf-style help: usage, description, Commands/Options, Global flags, docs footer |
| `version`, `-v/--version` | `name X.Y.Z`, `repo <git url>`, Python/Go version |
| `update [--check]` | self update; `--check` only compares versions |
| `init` | only if the tool needs first-run files (config, `.env`, cron); no questions, flags decide |
| `config show/get/set/reset/path/validate` | only if the tool has settings (`add_config`) |
| `-q/--quiet`, `<TOOL>_QUIET=1` | no banner, notes or success markers |
| `-y/--yes`, `--json`, `--dry-run`, `-f/--force` | same spelling and meaning everywhere |

## Other languages

Go (dokploytools): no shared library. Port `ui.go` (palette, `paint`, markers, `errorBox`, `printJSON`, `ask/need`), a table-driven `help.go`, and `fillMissing` for positionals; see https://github.com/arian24b/dokploytools/tree/main/src. Keep the same roles, shapes and exit codes.

## Workflow (hand-rolled, other languages)
1. Find the target CLI's output layer (grep `console.log`, `print`, `chalk`, `colorama`, `rich`, `fmt.Print`). Centralize into ONE small `ui` module (theme + 5 helpers below). Don't scatter styling.
2. Replace ad-hoc colors/emoji with the semantic palette and helpers.
3. Apply the behavior rules. Run the tool in a TTY, piped, and with `NO_COLOR=1` to verify.

## Palette (semantic, truecolor hex; legible on light+dark)
| role | hex | use |
|---|---|---|
| brand | `#BF6600` | banner, rule, headings (bold) |
| success | `#3A8E52` | ✔ lines, JSON strings |
| error | `#D45350` | ✖, error box |
| warning | `#BF6600` | ⚠, update notices, JSON numbers |
| info | `#3D82BB` | ℹ, code/commands, JSON keys |
| muted | `#7F7F7F` | secondary text, `·` separators, `→` hints |
| json boolean | `#926CC1` | true/false (null → muted) |

Never use raw red/green/yellow names; always roles. Color only when: stdout is TTY, `NO_COLOR` unset, `FORCE_COLOR` != `0`. Downgrade to 256/16 colors per terminal capability (use chalk/picocolors-equivalent detection).

## Symbols
Unicode: `✔ ✖ ⚠ ℹ →`. Fallback (non-unicode terminals/Windows legacy): `√ × ‼ i >`.

## Helpers (exact shapes)
```
success(m) = green ✔ + " " + m
warning(m) = orange ⚠ + " " + m
info(m)    = blue ℹ + " " + m
hint(m)    = muted "→ " + muted m
```
Success markers with no payload go to **stderr** and only if stderr is a TTY.

## Banner (interactive commands only, not for piped/--quiet)
```
🍊☁️  cf · v1.0.0 · update available: v1.1.0     <- brand+bold name, muted "·" and version, warning update note
──────────────────────────────────────────────  <- brand "─" repeated to the visible length of line 1 (strip ANSI before measuring)
```
Replace `cf` with the tool's name; keep the emoji slot to a single tool glyph. Append `· delegated` (muted) only if the tool has an analogous mode.

## Errors (boxed, stderr)
```

┌ Error                      <- ┌ and title in error color, title bold
│ Message wrapped to cols-2  <- │ error-colored, bold; wrap on word boundaries, min width 20
│
│ Hint / how to fix          <- muted lines after a blank │
└
```
Options: custom title; `rawMessage` skips wrapping/bold (for pre-formatted text). Exit non-zero; Ctrl-C/cancel in a prompt exits **130**.

## Output
- Structured results: pretty JSON (`indent 2`) on **stdout**, nothing else on stdout. Humans/agents/`jq` all consume it.
- Colorize JSON only if TTY + color on + length <= 50,000 chars: keys info, strings success, numbers warning, booleans purple, null muted.
- Unwrap API envelopes (`{result:[...], result_info}` → `result`).
- Binary/text payloads write raw to stdout.
- Everything decorative (banner, spinners, success markers) → stderr or TTY-only.

## Interactivity
- Prompts via `@clack/prompts` in JS (text, select, password with `•` mask); `cfui.ui.ask/confirm` in Python; stdin prompts on stderr elsewhere. Sanitize labels (strip control chars).
- Non-interactive (no TTY / CI): never prompt; fail with `--flag is required. Pass --flag <value> or run interactively.` Secrets may come via stdin.
- Progress animation (clack spinner) only on color-capable TTY; disabled for pipes, `NO_COLOR`, `<TOOL>_QUIET=1`.

## Global flags / env to mirror
`-q/--quiet` (suppress non-essential output), `-h/--help`, `-v/--version`, `--profile`; env `NO_COLOR`, `FORCE_COLOR`, `<TOOL>_QUIET`; optional OSC 9;4 terminal-tab progress, opt-out `<TOOL>_NO_OSC_PROGRESS=1`.

## Help layout (yargs-style)
`tool <command> [options]` → one-line description → `Commands` (two columns: `tool name   description`, wrapped) → `Global flags` (`-q, --quiet   desc  [boolean] [default: false]`) → `Options` → footer `For more information, visit <docs url>`. Command tree: `tool <resource> [group] <verb>` (e.g. `cf zones list`). Add a `tool cli search "<task>"` discovery command only if the CLI has >50 commands.

## Reference snippet (Node, ~25 lines)
```js
const on = process.stdout.isTTY && !('NO_COLOR' in process.env) && process.env.FORCE_COLOR !== '0'
const hex = h => s => on ? `\x1b[38;2;${[1,3,5].map(i=>parseInt(h.slice(i,i+2),16)).join(';')}m${s}\x1b[39m` : s
export const c = { brand:hex('#BF6600'), success:hex('#3A8E52'), error:hex('#D45350'),
  warning:hex('#BF6600'), info:hex('#3D82BB'), muted:hex('#7F7F7F'),
  bold: s => on ? `\x1b[1m${s}\x1b[22m` : s }
export const ok   = m => console.error(`${c.success('✔')} ${m}`)
export const warn = m => console.error(`${c.warning('⚠')} ${m}`)
export const note = m => console.error(`${c.info('ℹ')} ${m}`)
export const banner = (name, v) => {
  const t = `🍊☁️  ${c.brand(c.bold(name))} ${c.muted('·')} ${c.muted('v'+v)}`
  return `${t}\n${c.brand('─'.repeat(t.replace(/\x1b\[[0-9;]*m/g,'').length))}`
}
export const errorBox = (msg, hint) => [ '', `${c.error('┌')} ${c.error(c.bold('Error'))}`,
  ...msg.split('\n').map(l => `${c.error('│')} ${c.error(c.bold(l))}`),
  ...(hint ? [c.error('│'), ...hint.split('\n').map(l => `${c.error('│')} ${c.muted(l)}`)] : []),
  c.error('└') ].join('\n')
```
(Port to Python/Go/Rust with the same roles and shapes.)

## Caveats
- cf is beta; palette/layout may change. Don't copy Cloudflare logos/trademarks into a tool you distribute; the 🍊☁️ banner glyph is optional, swap for the tool's own.
- Don't run `cf zones list` etc. just to inspect style: it prints real account data. Read `dist/` or use `--help`.
