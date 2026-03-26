# 全能文档存储技能 (Universal Document Storage)

## 概述
全能文档存储技能是一个统一的文档存储和管理系统，支持多种存储后端和智能分类。它为OpenClaw用户提供了一套完整的文档管理解决方案。

## 功能特点
- **统一存储接口** - 支持本地存储、腾讯云COS、腾讯文档、Git、Obsidian
- **多种格式支持** - Markdown、PDF、Word、Excel、JSON、YAML、文本等
- **智能搜索功能** - 关键词、日期、分类、标签等多维度搜索
- **文档打开功能** - 多种打开方式（按ID、按路径、按搜索）
- **列表管理功能** - 查看所有文档，可按格式、分类、排序筛选
- **自动分类系统** - 基于内容智能分类（会议纪要、工作报告、技术文档等）
- **文档ID系统** - 每个文档都有唯一ID，便于管理和查找
- **配置文件** - 可配置多种存储后端和默认设置

## Skill-Storager升级版
skill-storager是全能文档存储技能的升级版，提供更强大的文档存储和管理能力：

### 升级特性
✅ **增强的搜索功能** - 支持更智能的关键词匹配  
✅ **优化的分类系统** - 更准确的自动分类  
✅ **批量操作优化** - 支持大规模文件处理  
✅ **性能改进** - 更快的存储和检索速度  
✅ **错误处理** - 更好的异常处理机制  
✅ **版本控制增强** - 完整的文档版本管理和历史记录

### 安装方法（skill-storager）
```bash
git clone https://github.com/baimaolv-cloud/universal-doc-storage.git ~/.openclaw/workspace/skills/skill-storager
bash ~/.openclaw/workspace/skills/skill-storager/scripts/example.sh
```

### GitHub仓库
**全能文档存储**：https://github.com/baimaolv-cloud/universal-doc-storage  
**Topics标签**：storage, document, cos, tencent, docs, git, obsidian, openclaw, claw

### 技能版本
- **全能文档存储**：v0.1.0（基础版本）
- **skill-storager**：v0.2.0（升级版本）

## 许可证
MIT License

## 作者
baimaolv-cloud