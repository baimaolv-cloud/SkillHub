---
name: skill-viewer
description: 查看和管理 OpenClaw 已安装的 skills。列出技能、按分类查看、搜索、查看详情、记录使用时间、自动清理 30 天未使用的 skill。
triggers:
  - 查看技能
  - 列出技能
  - 有什么技能
  - skills列表
  - 技能管理
  - 查找技能
  - 搜索技能
  - 清理技能
  - 删除未使用技能
  - 技能使用记录
---

# Skill Viewer

查看和管理 OpenClaw 已安装的 skills，支持使用记录追踪与自动清理。

## 功能

1. **列出所有技能** - 查看全部已安装技能（含最后使用时间）
2. **按分类查看** - 按类别筛选技能
3. **搜索技能** - 根据关键词查找技能
4. **查看技能详情** - 读取 skill 的 SKILL.md 文件
5. **使用记录** - 查看每个 skill 的最后使用时间
6. **自动清理** - 删除 30 天内未使用的 skill（保护核心 skill）

## 使用方法

### 列出所有技能
```
查看所有技能 / 列出技能 / skills列表
```

### 清理未使用技能
```
清理技能 / 删除未使用技能
→ 执行: python skill_viewer.py clean
```

### 预览将被清理的技能（不实际删除）
```
→ 执行: python skill_viewer.py clean-dry
```

### 查看使用记录
```
→ 执行: python skill_viewer.py usage
```

### 记录某 skill 使用时间
```
→ 执行: python skill_viewer.py record <skill_name>
```

## 自动清理规则

- **阈值**：30 天内从未使用 → 自动删除
- **保护名单**（永不删除）：
  `qclaw-rules`, `qclaw-env`, `qclaw-openclaw`, `qclaw-calendar-guide`,
  `find-skills`, `skillhub-preference`, `skill-viewer`
- **只删除** `~/.qclaw/workspace/skills/` 下的 skill（系统内置 skill 不受影响）
- **使用记录**存储于 `~/.qclaw/workspace/skills/.skill_usage.json`

## 命令行

```bash
python skill_viewer.py list                  # 列出所有技能（含使用时间）
python skill_viewer.py category <name>       # 按分类查看
python skill_viewer.py search <keyword>      # 搜索技能
python skill_viewer.py detail <name>         # 查看详情
python skill_viewer.py usage                 # 查看使用记录
python skill_viewer.py record <skill_name>   # 记录某 skill 使用时间
python skill_viewer.py clean-dry             # 预览将被清理的 skill（不删除）
python skill_viewer.py clean                 # 自动删除 30 天未使用的 skill
```

## 技能分类

- **核心系统**: qclaw-rules, qclaw-env, qclaw-openclaw
- **搜索与信息**: search, multi-search-engine, find-skills
- **文档处理**: docx, pdf, tencent-docs
- **数据与分析**: analytics-dashboard, quant-backtest
- **内容创作**: content-factory, humanize-ai-text
- **效率工具**: proactive-agent, niuamaxia-scheduler
- **健康管理**: nutritionist, habit-tracker
- **新闻资讯**: news-summary, tech-news-digest
- **安全审计**: skill-vetter, skill-creator
- **独家密法**: skill-viewer（自创技能）
