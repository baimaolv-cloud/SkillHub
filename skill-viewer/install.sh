#!/bin/bash

# Skill Viewer 安装脚本
# 自动安装 skill-viewer 技能到 OpenClaw

set -e

echo "🚀 开始安装 skill-viewer..."

# 检查 OpenClaw 目录
OPENCLAW_DIR="$HOME/.openclaw"
if [ ! -d "$OPENCLAW_DIR" ]; then
    echo "❌ OpenClaw 目录不存在: $OPENCLAW_DIR"
    exit 1
fi

SKILLS_DIR="$OPENCLAW_DIR/workspace/skills"
if [ ! -d "$SKILLS_DIR" ]; then
    echo "❌ OpenClaw skills 目录不存在: $SKILLS_DIR"
    exit 1
fi

# 创建技能目录
SKILL_DIR="$SKILLS_DIR/skill-viewer"
if [ -d "$SKILL_DIR" ]; then
    echo "⚠️ skill-viewer 已存在，是否覆盖？(y/n)"
    read -r answer
    if [[ "$answer" != "y" ]] && [[ "$answer" != "Y" ]]; then
        echo "❌ 取消安装"
        exit pr "/tmp/skill-viewer.zip"
fi

# 下载技能文件
echo "📥 下载 skill-viewer..."
mkdir -p /tmp/skill-viewer

# 下载主文件
curl -L https://raw.githubusercontent.com/baimaolv-cloud/SkillHub/main/skill-viewer/skill_viewer.py -o /tmp/skill-viewer/skill_viewer.py
curl -L https://raw.githubusercontent.com/baimaolv-cloud/SkillHub/main/skill-viewer/SKILL.md -o /tmp/skill-viewer/SKILL.md
curl -L https://raw.githubusercontent.com/baimaolv-cloud/SkillHub/main/skill-viewer/config.json -o /tmp/skill-viewer/config.json
curl -L https://raw.githubusercontent.com/baimaolv-cloud/SkillHub/main/skill-viewer/README.md -o /tmp/skill-viewer/README.md

# 安装技能
echo "📦 安装 skill-viewer..."
rm -rf "$SKILL_DIR"
mkdir -p "$SKILL_DIR"
cp /tmp/skill-viewer/* "$SKILL_DIR/"
chmod +x "$SKILL_DIR/skill_viewer.py"

# 清理临时文件
rm -rf /tmp/skill-viewer

echo "✅ skill-viewer 安装完成！"
echo ""
echo "📚 使用方法："
echo "1. 列出所有技能：python3 $SKILL_DIR/skill_viewer.py list"
echo "2. 搜索技能：python3 $SKILL_DIR/skill_viewer.py search '关键词'"
echo "3. 查看技能详情：python3 $SKILL_DIR/skill_viewer.py detail '技能名'"
echo "4. 预览清理：python3 $SKILL_DIR/skill_viewer.py clean-dry"
echo "5. 执行清理：python3 $SKILL_DIR/skill_viewer.py clean"
echo ""
echo "💡 技能已安装到：$SKILL_DIR"
echo "🎉 开始管理你的 OpenClaw 技能吧！"