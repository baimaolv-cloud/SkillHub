# 全能文档存储技能 (Universal Document Storage)

一个统一的文档存储和管理系统，支持多种存储后端和智能分类。

## 功能特点

### 核心功能
1. **统一存储接口** - 支持本地存储、腾讯云COS、腾讯文档、Git、Obsidian
2. **多种格式支持** - Markdown、PDF、Word、Excel、JSON、YAML、文本等
3. **智能搜索功能** - 关键词、日期、分类、标签等多维度搜索
4. **文档打开功能** - 多种打开方式（按ID、按路径、按搜索）
5. **列表管理功能** - 查看所有文档，可按格式、分类、排序筛选
6. **自动分类系统** - 基于内容智能分类（会议纪要、工作报告、技术文档等）
7. **文档ID系统** - 每个文档都有唯一ID，便于管理和查找
8. **配置文件** - 可配置多种存储后端和默认设置

## 安装方法

### 方法一：GitHub仓库
```bash
git clone https://github.com/baimaolv-cloud/universal-doc-storage.git ~/.openclaw/workspace/skills/universal-doc-storage
```

### 方法二：SkillHub安装
```bash
skillhub install universal-doc-storage
```

### 方法三：ClawHub安装
```bash
clawhub install universal-doc-storage
```

### 方法四：手动安装
复制技能目录到：
```
~/.openclaw/workspace/skills/universal-doc-storage
```

## 快速测试
```bash
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/example.sh
```

## 使用方法

### 存储文档
```bash
# 存储会议纪要（自动分类）
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/store.sh --content "项目工作会议纪要" --title "项目会议" --auto-categorize true

# 存储JSON格式文档
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/store.sh --content '{"进度": "完成50%"}' --title "项目进度报告" --format json

# 存储学习笔记
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/store.sh --content "今天学习了..." --title "学习笔记" --tags "学习,笔记,总结"
```

### 列出文档
```bash
# 列出所有本地存储的文档
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/list.sh --storage local

# 列出按日期排序的文档
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/list.sh --storage local --sort date

# 列出指定格式的文档
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/list.sh --storage local --format markdown

# 列出所有存储类型的文档
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/list.sh --all
```

### 搜索文档
```bash
# 关键词搜索
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/search.sh --query "项目"

# 搜索指定分类的文档
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/search.sh --query "会议" --category meeting

# 搜索指定格式的文档
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/search.sh --query "技术" --format json

# 限制搜索结果数量
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/search.sh --query "笔记" --limit 5
```

### 打开文档
```bash
# 通过文档ID打开
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --id "221304"

# 查看文档内容
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --id "221304" --view content

# 查看文档信息
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --id "221304" --view info

# 查看内容和信息
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --id "221304" --view both

# 通过文件路径打开
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --file "/path/to/document.md"

# 搜索并打开第一个匹配文档
bash ~/.openclaw/workspace/skills/universal-doc-storage/scripts/open.sh --query "关键词" --open-first
```

## 技能结构

```
universal-doc-storage/
├── SKILL.md                # 核心技能配置
├── _meta.json              # 元数据配置（v0.1.0）
├── README.md               # 完整使用文档
├── LICENSE                 # MIT许可证
├── config/
│   ├── storage_config.yaml # 存储配置
│   ├── categories.yaml     # 分类配置
├── scripts/
│   ├── setup.sh            # 配置脚本
│   ├── store.sh            # 存储脚本
│   ├── open.sh             # 打开脚本
│   ├── search.sh           # 搜索脚本
│   ├── list.sh             # 列表脚本
│   ├── example.sh          # 示例脚本
│   ├── sync_to_git.sh      # GitHub同步脚本
│   ├── publish_to_clawhub.sh # ClawHub发布脚本
│   ├── install.sh          # 安装脚本
├── references/
│   ├── README.md           # 详细使用指南
│   ├── PUBLISH.md          # 发布指南
│   ├── SHARE.md            # 分享总结
├── tools/                  # 核心工具框架
```

## GitHub仓库
主仓库：https://github.com/baimaolv-cloud/universal-doc-storage

## 许可证
MIT License

## 版本
当前版本：0.1.0

## 作者
baimaolv-cloud