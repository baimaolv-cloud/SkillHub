---
name: skill-usage-tracker
description: "自动追踪 skill 使用记录。每当消息触发某个 skill 时，自动更新 skill-viewer 的使用日志，无需手动调用 record 命令。"
metadata:
  {
    "openclaw": {
      "emoji": "📊",
      "events": ["message:preprocessed"]
    }
  }
---

# skill-usage-tracker

自动追踪 skill 使用记录，配合 skill-viewer 的自动清理功能使用。

## 工作原理

监听每条进入 agent 的消息，扫描消息内容中是否匹配已安装 skill 的触发词（triggers），
若匹配则自动调用 skill-viewer 的 `record` 命令更新使用时间。

## 依赖

- skill-viewer 已安装于 `~/.qclaw/workspace/skills/skill-viewer/`
- Python 3.x

## 安装

```bash
openclaw hooks enable skill-usage-tracker
```
