# Changelog

## 1.1.0 - 2026-07-31

- Update the model to `gpt-image-2` throughout, and remove the `gpt-image-1-mini` fallback and the DALL-E references: OpenAI's current model documentation lists neither, so both routed at products no longer in the API. Treated as MINOR rather than MAJOR because the removed path pointed at a dead model ID, so no working capability was lost. Verified with a live generation.
