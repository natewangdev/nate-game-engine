# Contract: Logging Public API

**Feature**: `003-logging-layout` | **Date**: 2026-09-27

Chinese companion: [`public-api.zh-CN.md`](./public-api.zh-CN.md).

## `NGE2` constructor (delta)

```text
NGE2(
    resource_dir=...,
    ...,
    log_dir=None,   # str | Path | None → default {cwd}/logs
)
# enable_file_logging REMOVED
```

## Log line format (console + file)

```text
HH:MM:SS LEVEL   message
```

No logger name segment.

## Paths

- Log: `{log_dir}/{YYYY-MM-DD}/nge-NNN.log`
- Screenshot: `{log_dir}/{YYYY-MM-DD}/screenshot/{HHMMSS}-{xxx}.jpg`

## Helpers

- `nge2.log.get_logger` unchanged (namespaced under `nge` for filtering; name not printed)
- Low-level `add_file_logging` may remain for tests but engine path uses layout helpers
