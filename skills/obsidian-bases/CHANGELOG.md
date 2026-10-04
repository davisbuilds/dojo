## 2.0.0 - 2026-10-03

- Rewrite around common failure modes (unfiltered bases include the whole vault, property namespaces, quoting, Duration math, Link comparison, stale file fields) and add live verification with obsidian base:query; examples verified against Obsidian 1.13.7 (268 to 88 lines). Add random() to the function reference.
- Add a file-fields table to references/functions.md (file.basename and tag-matching behavior observed on 1.13.7); verification runs base:query when the CLI responds and says so when it can't.
