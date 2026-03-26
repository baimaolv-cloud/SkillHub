# Skill Viewer

一个强大的 OpenClaw 技能管理和查看工具，帮助你轻松管理、分类和清理已安装的技能。

## 功能特点

### 📋 技能列表
- 列出所有已安装的技能
- 按分类展示技能
- 显示技能使用记录（最后使用时间）

### 🔍 搜索功能
- 关键词搜索技能
- 按分类筛选
- 查看技能详情

### 📊 使用记录
- 追踪每个技能的使用时间
- 记录技能安装日期
- 统计使用频率

### 🧹 智能清理
- 自动清理30天未使用的技能
- 预览将被清理的技能（不实际删除）
- 保护核心系统技能不被删除

### 📈 统计分析
- 技能数量统计
- 分类分布统计
- 使用频率分析

## 安装方法

### 从 GitHub 安装
```bash
git clone https://github.com/baimaolv-cloud/SkillHub.git ~/.openclaw/workspace/skills/skill-viewer
```

### 使用 skillhub
```bash
skillhub install skill-viewer
```

## 使用方法

### 列出所有技能
```bash
python3 ~/.openclaw/workspace/skills/skill-viewer/skill_viewer.py list
```

### 搜索技能
```bash
python3 ~/.openclaw/workspace/skills/skill-viewer/skill_viewer.py search "github"
```

### 查看技能详情
```bash
python3 ~/.openclaw/workspace/skills/skill-viewer/skill_viewer.py detail "github"
```

### 预览清理
```bash
python3 ~/.openclaw/workspace/skills/skill-viewer/skill_viewer.py clean-dry
```

### 执行清理
```bash
python3 ~/.openclaw/workspace/skills/skill-viewer/skill_viewer.py clean
```

## 配置说明

- **WORKSPACE_SKILLS_DIR**: `~/.openclaw/workspace/skills/`
- **USAGE_LOG_PATH**: `~/.openclaw/workspace/skills/.skill_usage.json`
- **OPENCLAW_DIR**: `~/.openclaw/`
- **AUTO_CLEAN_DAYS**: 30天未使用自动清理
- **PROTECTED_SKILLS**: 核心系统技能，永不删除

## 技能分类

技能会自动分为以下类别：
- 核心系统
- 搜索与信息
- 文档处理
- 浏览器与测试
- 效率工具
- 生活娱乐
- 安全审计
- 股票金融
- 编程开发
- 数学
- 独家密法
- 其他

## 保护名单

以下技能永远不会被自动清理：
```
openclaw-rules, openclaw-env, openclaw-openclaw, openclaw-calendar-guide,
find-skills, skillhub-preference, skill-viewer
```

## 技术实现

- 基于 Python 实现
- 支持 OpenClaw 平台
- 自动检测技能目录
- JSON格式的使用记录存储
- 智能分类算法

## 贡献

欢迎提交 Pull Request 或 Issue：
- GitHub: https://github.com/baimaolv-cloud/SkillHub

## 许可证

MIT License