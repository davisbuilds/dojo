---
name: block-dangerous-rm
enabled: true
event: bash
pattern: rm\s+-rf
action: block
---

Dangerous rm command detected. Verify the path before proceeding.
