---
version: alpha
name: modern-fixture
colors:
  primary: "oklch(60% 0.15 250)"
  overlay: "rgba(0, 0, 0, 0.5)"
omitted:
  - typography
  - section: spacing
    reason: "Spacing remains in the consuming layout."
  - rounded
  - components
---

## Overview

A small color-only system. Preserve the source color representations.

## Colors

Primary and overlay colors are consumed directly by the application stylesheet.
