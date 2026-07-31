# Changelog

## 1.1.0 - 2026-07-31

- Add an optional `--model` flag so the documented draft-then-final workflow is actually executable; previously the model was a hardcoded constant and the flag did not exist. Default is now `gemini-3.1-flash-image` with `gemini-3-pro-image` for finals, replacing IDs that either carried a superseded `-preview` suffix or were not image-capable models at all. Verified with a live generation.
