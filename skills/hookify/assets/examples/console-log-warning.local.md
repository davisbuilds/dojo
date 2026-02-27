---
name: warn-console-log
enabled: true
event: file
pattern: console\.log\(
action: warn
---

Console.log detected. Remove before committing or use a proper logging library.
