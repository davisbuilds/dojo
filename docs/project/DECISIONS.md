# Catalog decisions

## Vercel skills and shipping profile retirement

**Date:** 2026-10-23. **Scope:** the Dojo catalog and distribution profile contract.

Retire `vercel-react-best-practices`, `vercel-deploy`, and
`vercel-preview-logs`. Retire the `shipping` overlay because its entire membership
was the deploy and preview-log skills. Saved selections containing `shipping`
must fail explicitly as an unknown profile; do not silently drop or remap it.

### Why

- **React reference:** the broad React/Next.js trigger and frozen rule collection
  do not supply a distinct Dojo capability. Universal requirements such as avoiding
  barrel imports also conflict with conditional advice inside the collection.
  Framework and compiler behavior should be checked against the project's actual
  versions and relevant current documentation when it matters.
- **Deploy:** ordinary CLI instructions were coupled to an automatic fallback
  that uploaded a project archive to a third-party deployment service. Its readiness
  probe treated client errors as ready and could finish successfully after timing
  out, while the skill prohibited subsequent HTTP verification. These are poor
  defaults for authority and completion claims; preserving the wrapper is not
  necessary to preserve deployment capability.
- **Preview logs:** generic troubleshooting instructions depended on a wrapper
  that redirected CLI configuration into a shared temporary directory. That changes
  authentication behavior without establishing isolation, and copied command syntax
  can drift independently of the installed CLI.

This is a source and consumer review, not an experiment showing that agents perform
better without these skills. Prior content is recoverable from Git history
(`6739192` precedes the retirement); historical profile captures remain unchanged.

### What owns the work now

Project operations docs own deployment targets, environment selection, credentials,
and rollout expectations. Use the installed CLI's help and current vendor docs for
commands. Vercel's [inspect documentation](https://vercel.com/docs/cli/inspect)
describes completion waiting and timeout behavior; its
[logs documentation](https://vercel.com/docs/cli/logs) owns current log-selection
syntax. A completed deployment still needs checks appropriate to the behavior claimed.
React's [compiler introduction](https://react.dev/learn/react-compiler/introduction)
illustrates why optimization advice needs framework and build context.

Existing diagnosis, review, testing, and verification skills remain available when
their triggers fit. No replacement platform skill or generic deployment guide is
introduced. Reconsider a shared capability if repeated real work reveals a concrete
gap that project guidance and current tools do not address.

### Distribution boundary

Managed consumers own project links and deployment declarations outside this repo.
Remove references to the retired skills before syncing the canonical deletion,
while preserving unrelated selections and project deployment behavior. Deployment
owners keep their migration receipts; historical evidence is not an installation
to rewrite.
