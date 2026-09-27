# 契约：ESP32-S3 HID 串口行协议

**功能**：`001-nge2-mvp` | **日期**：2026-09-26

> 英文权威版：[`hid-protocol.md`](./hid-protocol.md)。执行 Spec Kit 时忽略本中文版。

与英文版信息等价：CDC 行协议、PING/MA/CLK/BTN/KD/KU/KP/MOD/STOP、像素到 0..32767 映射、keymap Usage ID、构造时探活、关闭时 STOP（须释放按住的鼠标键与键盘键）、端口独占。`BTN` 为左右键按下/抬起公开 API 所必需。
