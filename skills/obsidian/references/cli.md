# Obsidian CLI

The CLI asks the running Obsidian app for answers that plain files can't give: resolved links, the tag and property index, Bases results, applied setting defaults, link-updating renames, file-recovery history. For reading, searching, and editing note text, the files themselves are usually simpler.

Behavior below was observed on Obsidian 1.13.7 (macOS). Commands differ by version; `obsidian help <command>` is the source of truth for parameters.

## Availability

- Requires the Obsidian 1.12 installer; the docs ask for 1.12.7 or later. Turn on **Settings → General → Advanced → Command line interface** and follow the registration prompt. The setting persists as `"cli": true` in the app's `obsidian.json`, which the running app rewrites from memory, so edit that file only while Obsidian is quit.
- The app does the work. Per the docs, if it isn't running, the first command launches it.
- Probe with `obsidian version`. A disabled CLI prints `Command line interface is not enabled…` rather than failing.
- On macOS, registration links `/usr/local/bin/obsidian` to the bundled native client `obsidian-cli` (an admin prompt). Older registrations instead left a `# Added by Obsidian` PATH entry in `~/.zprofile` pointing at the app's `MacOS` folder, where `obsidian` is the Electron entry point: it works, but starts several times slower than `obsidian-cli`. The docs say that entry can be deleted.
- Install, register, or reconfigure Obsidian only when requested or already authorized. Otherwise, report what's missing and continue with file-based work where sufficient.

## Calling It

- `vault=<name>` goes **before** the command: `obsidian vault="My Vault" tags counts`. Without it the CLI uses the vault of the current directory or the active vault.
- `path=` is an exact vault-relative path; `file=` resolves a name the way wikilinks do. Prefer `path=`.
- **Most commands act on the active file when `path=`/`file=` is omitted** — whatever note is open in the app. Always pass a target for anything that writes.
- Parameters are `name=value`; flags are bare words (`counts`, `total`, `verbose`). Quote values with spaces. In `content=` values, `\n` and `\t` become a newline and tab.
- Many listing commands take `format=json|tsv|csv`; prefer `json` for parsing.

## Output Traps

- **Exit status is 0 even on failure.** Errors arrive on stdout as text — `Error: File "x.md" not found.`, `Vault not found.`, `Error: Command "x" not found. It may require a plugin to be enabled.` Check the output, not `$?`.
- A folder that doesn't exist returns empty output, same as an empty folder.
- `create` on an existing path does not fail or overwrite: it creates `Name 1.md` and reports that path. Use `overwrite` deliberately, or check first.
- `search` covers the whole vault, including plugin data folders.
- `base:query` reports formula errors as `Error: ...` cell values.

## App-Only Answers Worth Using

| Need | Command |
|---|---|
| Broken links | `unresolved verbose` (misses literal `[[##x]]`; see `markdown.md`) |
| Links into / out of a note | `backlinks path=…`, `links path=…`; graph gaps: `orphans`, `deadends` |
| Tag and property vocabulary | `tags counts sort=count`, `properties counts sort=count`, `tag name=x verbose` |
| What a note indexed as | `properties path=…`, `tags path=…`, `aliases path=…` |
| Typed property write | `property:set path=… name=… value=… type=text\|list\|number\|checkbox\|date\|datetime` |
| Daily note | `daily:path` (applies defaults absent from `daily-notes.json`), `daily:read`, `daily:append content=…` |
| Bases | `bases`, `base:views`, `base:query path=… view=… format=json\|paths` |
| Rename / move with link updates | `rename path=… name=…`, `move path=… to=…` |
| Templates with variables resolved | `template:read name=… resolve title=…`, `create path=… template=…` |
| Checkbox tasks | `tasks todo verbose`, `task ref=path:line done` |
| Undo an edit | `history path=…`, `history:read path=… version=n`, `history:restore path=… version=n` (File Recovery snapshots) |

## Needs Explicit Intent

- `delete` moves to the trash unless `permanent` is passed.
- `eval` and `dev:*` run code or debugging inside the app.
- `plugin:install|enable|disable|uninstall`, `theme:*`, `snippet:*` change the vault's configuration.
- `sync*` commands act on Obsidian Sync; `restart` and `reload` interrupt the user's session.
