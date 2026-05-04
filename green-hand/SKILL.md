---
name: green-hand
description: 新手快速上手 WorkBuddy 的技能安装引导工具。自动从 GitHub、SkillHub、ClawHub 安装精选技能，处理各类安装异常（Xcode 工具缺失、GitHub raw 超时等），帮助新手一键完成环境配置。
triggers:
  - 新手安装
  - 快速上手
  - 安装推荐技能
  - green-hand
  - 初始化技能
  - 安装精选技能
  - 新手引导
---

# Green Hand — 新手技能安装引导

为 WorkBuddy 新手提供一键式技能安装体验，自动从三个来源安装精选技能，并处理各类安装异常。

## 功能

1. **从 GitHub 安装指定用户的技能** — 支持指定用户，自动发现并安装其公开技能
2. **从 SkillHub 安装星数前 N 的技能** — 自动去重，跳过已安装
3. **从 ClawHub 安装星数前 N 的技能** — 与 SkillHub 去重，只装不重复的
4. **异常处理** — 自动处理 Xcode 工具缺失、GitHub raw 超时等问题
5. **安装报告** — 最终汇总安装结果

## 使用方法

### 完整安装（推荐新手）
```
新手安装 / 快速上手 / green-hand
```
自动执行：
1. 从 `baimaolv-cloud` 安装精选技能（hardware-master, skill-viewer, word2ppt 等）
2. 从 SkillHub 安装星数前 10
3. 从 ClawHub 安装星数前 10（去重）

### 自定义安装
```
green-hand --github-user <用户名> --skillhub-top 5 --clawhub-top 5
```

参数说明：
- `--github-user`：GitHub 用户名（默认 `baimaolv-cloud`）
- `--skillhub-top`：SkillHub 安装星数前 N（默认 10）
- `--clawhub-top`：ClawHub 安装星数前 N（默认 10）
- `--skip-github`：跳过 GitHub 安装
- `--skip-skillhub`：跳过 SkillHub 安装
- `--skip-clawhub`：跳过 ClawHub 安装

## 安装流程详解

### Step 1: 从 GitHub 安装

目标：从指定 GitHub 用户安装精选技能。

**实现方式：**
1. 通过 GitHub API 获取用户的公开仓库列表
   ```
   https://api.github.com/users/<user>/repos?type=public&per_page=100
   ```
2. 筛选名称含 `skill` 或以常见 skill 命名的仓库
3. 对每个仓库，尝试下载 `SKILL.md` 到 `~/.workbuddy/skills/<repo-name>/`
4. 如果仓库包含子目录技能（如 `SkillHub` 仓库），遍历 `contents` API 获取子目录

**异常处理：**
- **GitHub raw 下载超时** → 改用 Contents API (`/repos/{owner}/{repo}/contents/{path}`)，base64 解码后写入
- **仓库不存在** → 搜索确认正确用户名，提示用户

**推荐安装的 GitHub 技能（baimaolv-cloud）：**
- `hardware-master-skill` — 硬件评分
- `skill-viewer` — 技能查看管理（在 SkillHub 仓库子目录）
- `word2ppt` — Word 转 PPT

### Step 2: 从 SkillHub 安装星数前 N

目标：安装 SkillHub 星数排名最高的 N 个技能。

**SkillHub CLI 调用方式：**
```bash
# 注意：--dir 是全局选项，必须放在子命令前面
python3 ~/.skillhub/skills_store_cli.py --dir ~/.workbuddy/skills/ install <slug>
```

**异常处理：**
- **skillhub 命令需要 Xcode 工具** → 直接用 Python 运行 `~/.skillhub/skills_store_cli.py` 绕过
- **skillhub 未安装** → 提示用户先安装 SkillHub CLI

**获取星数排名：**
```bash
# 查看本地索引（如果已下载）
cat ~/.skillhub/skills_index.local.json | python3 -c "..." 
```

### Step 3: 从 ClawHub 安装星数前 N（去重）

目标：安装 ClawHub 星数前 N，排除 SkillHub 已安装的。

**ClawHub API：**
```
https://clawhub.ai/api/v1/skills?sort=stars&limit=20
```
返回 JSON，包含 `slug`、`stars` 等字段。

**去重逻辑：**
1. 获取 SkillHub 已安装的 slug 列表
2. 获取 ClawHub 星数排名
3. 过滤掉已在 SkillHub 列表中的 slug
4. 取前 N 个，调用 SkillHub CLI 安装（ClawHub 技能也通过 SkillHub CLI 安装）

### Step 4: 生成安装报告

汇总所有安装操作，输出：
- ✅ 成功安装的技能列表（含星数）
- ⚠️ 跳过的原因（已安装/不支持）
- ❌ 安装失败的技能及原因

## 技术要点

### GitHub Contents API 下载文件（解决 raw 超时）

```python
import urllib.request, base64, json, os

def download_github_file(owner, repo, path, dest):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
        content = base64.b64decode(data["content"]).decode("utf-8")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as f:
        f.write(content)
```

### SkillHub CLI 正确调用方式

```bash
# ❌ 错误：--dir 放在子命令后
skillhub install <slug> --dir ~/.workbuddy/skills/

# ✅ 正确：--dir 是全局选项，放在子命令前
skillhub --dir ~/.workbuddy/skills/ install <slug>

# ✅ 绕过 Xcode 工具问题，直接调用 Python
python3 ~/.skillhub/skills_store_cli.py --dir ~/.workbuddy/skills/ install <slug>
```

### ClawHub API 获取星数排名

```python
import urllib.request, json

def get_clawhub_top(limit=10):
    url = f"https://clawhub.ai/api/v1/skills?sort=stars&limit={limit}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read())
```

## 默认精选技能列表

| 来源 | 技能 | 说明 |
|------|------|------|
| GitHub (baimaolv-cloud) | hardware-master-skill | 硬件评分 |
| GitHub (baimaolv-cloud) | skill-viewer | 技能管理 |
| GitHub (baimaolv-cloud) | word2ppt | Word 转 PPT |
| SkillHub Top 10 | self-improving-agent, gog, tavily-search... | 星数最高 |
| ClawHub Top 10 | self-improving, skill-vetter, multi-search-engine... | 去重后安装 |

## 注意事项

- 安装前自动检查 `~/.workbuddy/skills/` 目录是否存在，不存在则创建
- 每个技能安装后验证 `SKILL.md` 是否存在
- 遇到安装失败时记录错误并继续，不中断整个流程
- 最终报告明确区分：新增安装 / 已跳过 / 安装失败
