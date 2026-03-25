---
name: skill-storager
version: 1.0.0
description: 全能文档存储与管理技能。支持本地、腾讯云COS、Git、Obsidian等多种存储后端，提供智能分类、搜索、文档ID管理。
triggers:
  - 存储文档
  - 保存文件
  - 文档管理
  - 搜索文档
  - 查看文档
  - 文档存储
  - 列出文档
---

# skill-storager — 全能文档存储技能

统一的文档存储和管理系统，支持多种存储后端和智能分类。

## 功能

1. **统一存储接口** - 本地 / 腾讯云COS / Git / Obsidian
2. **多格式支持** - Markdown、PDF、Word、Excel、JSON、YAML、文本等
3. **智能搜索** - 文件名、分类、全文内容多维度搜索
4. **文档ID系统** - 每个文档唯一8位ID，便于快速访问
5. **自动分类** - 智能识别会议纪要、工作报告、技术文档、合同协议等
6. **列表管理** - 按分类、格式筛选，支持分页

## 使用方法

### 存储文档
```
存储文档 / 保存文件 → storager.py store <文件名> <内容>
存储本地文件       → storager.py store-file <路径> [分类]
```

### 查找文档
```
搜索文档 <关键词>  → storager.py search <关键词>
列出所有文档       → storager.py list
列出某分类文档     → storager.py list <分类>
```

### 打开文档
```
查看文档 <ID>      → storager.py open <ID>
查看文档 <路径>    → storager.py open <路径>
```

### 删除文档
```
→ storager.py delete <ID>
```

### 配置管理
```
查看配置           → storager.py config
切换后端           → storager.py set-backend local|cos|git|obsidian
设置存储路径       → storager.py set-root <路径>
```

## 自动分类规则

| 关键词 | 分类 |
|--------|------|
| 会议/纪要/议程 | 会议纪要 |
| 报告/总结/周报 | 工作报告 |
| 方案/计划/规划 | 方案计划 |
| 合同/协议/条款 | 合同协议 |
| 技术/架构/API  | 技术文档 |
| 财务/预算/报销 | 财务文档 |
| 笔记/备忘/todo | 笔记备忘 |

## 存储后端

| 后端 | 说明 | 状态 |
|------|------|------|
| local | 本地文件系统（默认） | ✅ 已实现 |
| cos | 腾讯云COS对象存储 | 🔧 配置后可用 |
| git | Git仓库存储 | 🔧 配置后可用 |
| obsidian | Obsidian知识库 | 🔧 配置后可用 |

## 文件结构

```
skill-storager/
├── SKILL.md
├── _meta.json
├── scripts/
│   └── storager.py      # 核心脚本
└── config/
    └── config.json      # 配置文件
```

## 兼容性

- OpenClaw >= 2026.0.0
- Python >= 3.8
- 原始来源：universal-doc-storage (xiaoxinBot)，重新实现为 skill-storager
