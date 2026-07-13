## 1.0.1

- Add the required `version: 1.0.0` field to `init_skill.py`'s `SKILL_TEMPLATE`.
  A freshly scaffolded skill previously failed contract validation on creation,
  which also deadlocked the pre-write validation hook: the invalid scaffold
  blocked the very edit that would have added the missing field.
