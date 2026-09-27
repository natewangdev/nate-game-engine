# 研究：日志布局

**功能**：`003-logging-layout`

> 英文权威版：[`research.md`](./research.md)。

与英文版等价：共享 `nge` 根 + 每实例 FileHandler/ERROR 截图 Handler；序号 max+1 三位填充；Pillow 叠中文；截图失败用 WARNING + 防重入；删除 `enable_file_logging`。
