# Hardening Matrix

## Node Repos

Minimum baseline:

- commit a lockfile
- pin `packageManager` in `package.json`
- use `pnpm install --frozen-lockfile` or `npm ci` in CI
- add explicit top-level `permissions:` to every GitHub workflow
- pin `uses:` refs to commit SHAs

Common backlog:

- remove `npm install -g` from CI and docs where local project install is safer
- replace `latest` and `curl | sh` bootstrap paths
- reduce bot workflow write scope

## Python Repos

Minimum baseline:

- use `uv.lock`, `poetry.lock`, or hash-pinned requirements
- use `uv sync --frozen` or `pip install --require-hashes`
- avoid fresh `pip install -r requirements.txt` in CI unless that file is hash-pinned

Common backlog:

- remove runtime scanner installs from CI
- pin publish actions and release tooling
- separate publish and test permissions

## GitHub Actions

Minimum baseline:

- top-level `permissions:` block in every workflow
- no mutable `@main`, `@master`, `@beta`, `@release/*`, or plain `@vN` refs
- prefer pinned runner images for Ubuntu jobs when practical

Escalate when:

- bot/comment workflows have write scope
- install-capable commands are granted to agent actions
- workflows build or publish from issue-comment triggers

## GitLab CI

Minimum baseline:

- reduce fresh installs during pipeline execution
- use pinned images or versioned internal images
- treat `include:` refs as policy surface, not just convenience

## Remote Bootstrap And Downloads

Preferred order:

1. package-manager install from committed lockfile
2. pinned versioned artifact with checksum verification
3. fail closed if required tooling is absent

Avoid by default:

- `curl | sh`
- `npm@latest`
- `pnpm@latest`
- `releases/latest`
- default-branch `git clone` fallbacks in install paths
