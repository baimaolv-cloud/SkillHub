---
name: skill-storager
version: 1.0.0
description: 全能文档存储与管理技能。支持本地、腾讯云COS、腾讯文档、Git、Obsidian等多种存储后端，提供智能分类、搜索、文档ID管理。
triggers:
  - 存储文档
  - 保存文件
  - 文档管理
  - 搜索文档
  - 查看文档
  - 文档存储
---

# skill-storager — 全能文档存储技能

统一的文档存储和管理系统，支持多种存储后端和智能分类。

## 功能

1. **统一存储接口** - 本地 / 腾讯云COS / 腾讯文档 / Git / Obsidian
2. **多格式支持** - Markdown、PDF、Word、Excel、JSON、YAML、文本等
3. **智能搜索** - 关键词、日期、分类、标签多维度搜索
4. **文档打开** - 按ID / 路径 / 关键词搜索打开
5. **列表管理** - 按格式、分类、排序筛选
6. **自动分类** - 智能识别会议纪要、工作报告、技术文档等
7. **文档ID系统** - 每个文档唯一ID，便于管理

## 使用示例

`
存储文档 / 保存文件 / 文档管理
搜索文档 <关键词>
查看文档 <ID>
列出所有文档
`

## 存储后端

| 后端 | 说明 | 依赖 |
|------|------|------|
| 本地 | 默认，无需配置 | 无 |
| 腾讯云COS | 云端对象存储 | tencent-cos-skill（可选）|
| 腾讯文档 | 在线协作文档 | tencent-docs（可选）|
| Git | 版本控制存储 | git |
| Obsidian | 知识库管理 | obsidian（可选）|

## 兼容性

- OpenClaw >= 2026.0.0
- 原始来源：universal-doc-storage (xiaoxinBot)，重新打包为 skill-storager
