# 调研：窗口操作

英文权威版：[`research.md`](./research.md)。

决策与英文版等价：EnumWindows 可见顶层 + 不区分大小写子串；activate 失败抛 `WindowError`；`SetWindowPos` 置顶；外框 `GetWindowRect`+移动不改大小；可 monkeypatch 的模块级 Win32 辅助；无新依赖。
