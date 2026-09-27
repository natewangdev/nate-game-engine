# Data Model: Logging Layout

**Feature**: `003-logging-layout` | **Date**: 2026-09-27

Chinese companion: [`data-model.zh-CN.md`](./data-model.zh-CN.md).

## LogLayout

| Field | Type | Rules |
|-------|------|-------|
| log_dir | Path | Resolved absolute; default `{cwd}/logs` |
| day | str | Local `YYYY-MM-DD` at construct |
| day_dir | Path | `{log_dir}/{day}` |
| log_file | Path | `{day_dir}/nge-NNN.log` |
| screenshot_dir | Path | `{day_dir}/screenshot` |

## LogFileIndex / ScreenshotIndex

Integer sequences from scanning existing files; pad to 3 digits when &lt; 1000.

## ErrorScreenshotJob

| Field | Rules |
|-------|-------|
| message | Truncate to 200 chars + `…` for overlay |
| region | Window client screen rect if hwnd else full frame |
| path | `{screenshot_dir}/{HHMMSS}-{xxx}.jpg` |
