# 全能文档存储技能 (Universal Document Storage)

一个统一的文档存储和管理系统，支持多种存储后端和智能分类。

## When to Use

当用户需要存储、管理和检索文档时使用此技能。支持本地存储、腾讯云COS、腾讯文档、Git、Obsidian等多种后端，并提供智能分类、搜索和查看功能。

## 技能功能

### 核心功能
1. **统一存储接口** - 支持本地存储、腾讯云COS、腾讯文档、Git、Obsidian
2. **多种格式支持** - Markdown、PDF、Word、Excel、JSON、YAML、文本等
3. **智能搜索功能** - 关键词、日期、分类、标签等多维度搜索
4. **文档打开功能** - 多种打开方式（按ID、按路径、按搜索）
5. **列表管理功能** - 查看所有文档，可按格式、分类、排序筛选
6. **自动分类系统** - 基于内容智能分类（会议纪要、工作报告、技术文档等）
7. **文档ID系统** - 每个文档都有唯一ID，便于管理和查找
8. **配置文件** - 可配置多种存储后端和默认设置

### 文件打开和查看方法

#### 根据ID打开文档
```bash
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --id "221304"
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --id "221304" --view info
```

#### 根据文件路径打开
```bash
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --file "文件路径"
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --file "文件路径" --view both
```

#### 搜索并打开第一个匹配文档
```bash
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --query "关键词" --open-first
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --query "会议" --open-first --view content
```

#### 列出所有文档
```bash
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/list.sh --storage local
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/list.sh --all
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --all
```

#### 查看模式选项
- `content` - 只显示文档内容
- `info` - 只显示文档信息（大小、类型、创建时间）
- `both` - 显示内容和信息

### 使用示例
```bash
# 1. 检查配置
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/setup.sh --check-only

# 2. 存储文档
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/store.sh --content "内容" --title "标题"

# 3. 列出文档
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/list.sh --storage local --sort date --limit 5

# 4. 打开文档查看内容
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --id "221304" --view content

# 5. 打开文档查看信息
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --file "/root/.openclaw/workspace/storage/local/测试文档.markdown" --view info

# 6. 搜索并打开
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --query "关键词" --open-first --view both
```

### 自动分类示例
```bash
# 自动分类为"会议纪要"
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/store.sh --content "项目工作会议纪要" --auto-categorize true

# 自动分类为"技术文档"
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/store.sh --content "Python代码示例" --auto-categorize true

# 自动分类为"学习笔记"
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/store.sh --content "今日学习心得" --auto-categorize true
```

### 技能已完成的功能
1. ✅ 本地文件系统存储
2. ✅ 智能搜索功能
3. ✅ 文件打开/查看功能
4. ✅ 列表管理功能
5. ✅ 自动分类系统
6. ✅ 文档ID管理
7. ✅ 多种文档格式支持
8. ✅ 统一接口设计

### 待实现的功能（框架已搭建）
1. 📦 腾讯云COS集成（需要配置API密钥）
2. 📝 腾讯文档集成（需要配置Token）
3. 🔗 Git仓库集成（需要配置仓库信息）
4. 📒 Obsidian笔记库集成（需要配置Vault路径）
5. 🔍 OCR识别功能
6. 🔄 跨存储同步
7. 📊 版本控制系统