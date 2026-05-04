#!/usr/bin/env python3
"""
green_hand.py - WorkBuddy 新手技能安装引导工具
自动从 GitHub、SkillHub、ClawHub 安装精选技能
"""

import urllib.request
import json
import base64
import os
import sys
import subprocess
import time

SKILLS_DIR = os.path.expanduser("~/.workbuddy/skills")
SKILLHUB_PY = os.path.expanduser("~/.skillhub/skills_store_cli.py")
GITHUB_API = "https://api.github.com"
CLAWHUB_API = "https://clawhub.ai/api/v1/skills?sort=stars&limit=20"


def run(cmd, check=True):
    """执行 shell 命令，返回 (stdout, stderr, returncode)"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"命令失败: {cmd}\n{result.stderr}")
    return result.stdout, result.stderr, result.returncode


def github_api(path):
    """调用 GitHub API，返回解析后的 JSON"""
    url = f"{GITHUB_API}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def download_github_file(owner, repo, path, dest):
    """通过 GitHub Contents API 下载文件（base64 解码）"""
    data = github_api(f"/repos/{owner}/{repo}/contents/{path}")
    content = base64.b64decode(data["content"]).decode("utf-8")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as f:
        f.write(content)
    return dest


def download_github_dir(owner, repo, path, dest_dir):
    """递归下载 GitHub 目录"""
    items = github_api(f"/repos/{owner}/{repo}/contents/{path}")
    count = 0
    for item in items:
        dest = os.path.join(dest_dir, item["name"])
        if item["type"] == "file":
            download_github_file(owner, repo, item["path"], dest)
            count += 1
        elif item["type"] == "dir":
            count += download_github_dir(owner, repo, item["path"], dest)
    return count


def install_skillhub_slug(slug):
    """通过 SkillHub CLI 安装一个技能"""
    os.makedirs(SKILLS_DIR, exist_ok=True)
    cmd = f'python3 "{SKILLHUB_PY}" --dir "{SKILLS_DIR}" install {slug}'
    stdout, stderr, code = run(cmd, check=False)
    return code == 0, stdout + stderr


def get_installed_skills():
    """获取已安装的技能 slug 集合"""
    if not os.path.exists(SKILLS_DIR):
        return set()
    return set(os.listdir(SKILLS_DIR))


def step1_github(github_user="baimaolv-cloud"):
    """Step 1: 从 GitHub 用户安装精选技能"""
    print(f"\n📦 Step 1: 从 GitHub @{github_user} 安装技能...")
    results = {"success": [], "skip": [], "fail": []}

    # 获取用户的公开仓库
    try:
        repos = github_api(f"/users/{github_user}/repos?type=public&per_page=100")
    except Exception as e:
        print(f"  ❌ 无法获取仓库列表: {e}")
        return results

    # 筛选可能是技能的仓库
    skill_repos = []
    for repo in repos:
        name = repo["name"].lower()
        if "skill" in name or name in ("word2ppt", "hardware-master"):
            skill_repos.append(repo["name"])

    # 特殊处理：SkillHub 仓库包含子目录技能
    has_skillhub_repo = any(r for r in repos if r["name"] == "SkillHub")

    for repo_name in skill_repos:
        dest_dir = os.path.join(SKILLS_DIR, repo_name)
        if os.path.exists(dest_dir):
            results["skip"].append(f"{repo_name} (已安装)")
            continue
        try:
            # 尝试直接下载 SKILL.md（仓库根目录）
            download_github_file(github_user, repo_name, "SKILL.md",
                                os.path.join(dest_dir, "SKILL.md"))
            results["success"].append(repo_name)
            print(f"  ✅ {repo_name}")
        except Exception as e1:
            # 如果失败，尝试遍历子目录（如 SkillHub 仓库）
            try:
                count = download_github_dir(github_user, repo_name, "", dest_dir)
                if count > 0:
                    results["success"].append(f"{repo_name} ({count} files)")
                    print(f"  ✅ {repo_name} ({count} files)")
                else:
                    results["fail"].append(f"{repo_name} (无 SKILL.md)")
            except Exception as e2:
                results["fail"].append(f"{repo_name}: {e2}")
                print(f"  ❌ {repo_name}: {e2}")

    # 特殊处理 SkillHub 仓库的子目录技能
    if has_skillhub_repo:
        try:
            items = github_api(f"/repos/{github_user}/SkillHub/contents/")
            for item in items:
                if item["type"] == "dir":
                    slug = item["name"]
                    dest = os.path.join(SKILLS_DIR, slug)
                    if os.path.exists(dest):
                        results["skip"].append(f"{slug} (已安装)")
                        continue
                    try:
                        download_github_dir(github_user, "SkillHub", slug, dest)
                        results["success"].append(slug)
                        print(f"  ✅ {slug} (from SkillHub/)")
                    except Exception as e:
                        results["fail"].append(f"{slug}: {e}")
        except Exception as e:
            print(f"  ⚠️  无法读取 SkillHub 子目录: {e}")

    return results


def step2_skillhub(top_n=10):
    """Step 2: 从 SkillHub 安装星数前 N"""
    print(f"\n📦 Step 2: 从 SkillHub 安装星数前 {top_n}...")
    results = {"success": [], "skip": [], "fail": []}

    # 检查 SkillHub CLI
    if not os.path.exists(SKILLHUB_PY):
        print("  ⚠️  SkillHub CLI 未安装，跳过")
        results["fail"].append("SkillHub CLI 未安装")
        return results

    # 读取本地索引获取星数排名
    index_path = os.path.expanduser("~/.skillhub/skills_index.local.json")
    if not os.path.exists(index_path):
        print("  ⚠️  SkillHub 索引未找到，先运行 skillhub update")
        results["fail"].append("索引未找到")
        return results

    with open(index_path) as f:
        index = json.load(f)

    # 按星数排序
    sorted_skills = sorted(index, key=lambda x: x.get("stars", 0), reverse=True)
    installed = get_installed_skills()

    count = 0
    for skill in sorted_skills:
        if count >= top_n:
            break
        slug = skill.get("slug") or skill.get("name")
        if not slug or slug in installed:
            continue
        ok, msg = install_skillhub_slug(slug)
        if ok:
            results["success"].append(f"{slug} ({skill.get('stars', 0)}⭐)")
            print(f"  ✅ {slug} ({skill.get('stars', 0)}⭐)")
            count += 1
        else:
            results["fail"].append(f"{slug}: {msg[:80]}")
            print(f"  ❌ {slug}: {msg[:80]}")

    return results


def step3_clawhub(top_n=10):
    """Step 3: 从 ClawHub 安装星数前 N（与 SkillHub 去重）"""
    print(f"\n📦 Step 3: 从 ClawHub 安装星数前 {top_n}（去重）...")
    results = {"success": [], "skip": [], "fail": []}

    # 获取 ClawHub 排名
    try:
        with urllib.request.urlopen(CLAWHUB_API, timeout=15) as resp:
            clawhub_skills = json.loads(resp.read())
    except Exception as e:
        print(f"  ❌ ClawHub API 调用失败: {e}")
        results["fail"].append(f"API 失败: {e}")
        return results

    # 获取 SkillHub 已安装的 slug（用于去重）
    index_path = os.path.expanduser("~/.skillhub/skills_index.local.json")
    skillhub_slugs = set()
    if os.path.exists(index_path):
        with open(index_path) as f:
            for s in json.load(f):
                skillhub_slugs.add(s.get("slug") or s.get("name"))

    installed = get_installed_skills()
    count = 0

    for skill in clawhub_skills:
        if count >= top_n:
            break
        slug = skill.get("slug") or skill.get("name")
        if not slug:
            continue
        if slug in skillhub_slugs or slug in installed:
            results["skip"].append(f"{slug} (已存在于 SkillHub 或已安装)")
            continue
        ok, msg = install_skillhub_slug(slug)
        if ok:
            results["success"].append(f"{slug} ({skill.get('stars', 0)}⭐)")
            print(f"  ✅ {slug} ({skill.get('stars', 0)}⭐)")
            count += 1
        else:
            results["fail"].append(f"{slug}: {msg[:80]}")
            print(f"  ❌ {slug}: {msg[:80]}")

    return results


def print_report(r1, r2, r3):
    """打印安装报告"""
    print("\n" + "=" * 50)
    print("📊 安装报告")
    print("=" * 50)

    for step_name, r in [("Step 1 (GitHub)", r1), ("Step 2 (SkillHub)", r2), ("Step 3 (ClawHub)", r3)]:
        print(f"\n{step_name}:")
        if r["success"]:
            print(f"  ✅ 成功: {', '.join(r['success'])}")
        if r["skip"]:
            print(f"  ⚠️  跳过: {', '.join(r['skip'])}")
        if r["fail"]:
            print(f"  ❌ 失败: {', '.join(r['fail'])}")

    total_success = len(r1["success"]) + len(r2["success"]) + len(r3["success"])
    print(f"\n🎉 共计安装成功: {total_success} 个技能")
    print("=" * 50)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="WorkBuddy 新手技能安装引导")
    parser.add_argument("--github-user", default="baimaolv-cloud", help="GitHub 用户名")
    parser.add_argument("--skillhub-top", type=int, default=10, help="SkillHub 安装前 N")
    parser.add_argument("--clawhub-top", type=int, default=10, help="ClawHub 安装前 N（去重）")
    parser.add_argument("--skip-github", action="store_true", help="跳过 GitHub 安装")
    parser.add_argument("--skip-skillhub", action="store_true", help="跳过 SkillHub 安装")
    parser.add_argument("--skip-clawhub", action="store_true", help="跳过 ClawHub 安装")
    args = parser.parse_args()

    os.makedirs(SKILLS_DIR, exist_ok=True)

    r1 = {"success": [], "skip": [], "fail": []}
    r2 = {"success": [], "skip": [], "fail": []}
    r3 = {"success": [], "skip": [], "fail": []}

    if not args.skip_github:
        r1 = step1_github(args.github_user)
    if not args.skip_skillhub:
        r2 = step2_skillhub(args.skillhub_top)
    if not args.skip_clawhub:
        r3 = step3_clawhub(args.clawhub_top)

    print_report(r1, r2, r3)


if __name__ == "__main__":
    main()
