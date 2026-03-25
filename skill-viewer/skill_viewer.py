#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill Viewer - 查看和管理 OpenClaw 已安装的 skills
- 使用记录从用户首次登录时间起算
- 超过 30 天未使用自动删除
- 主动调用时醒目提示今日新装 / 今日刚删除的 skill
"""

import os
import json
import re
import shutil
import sys
import io
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta, date

# ─── 路径常量 ────────────────────────────────────────────────────────────────
WORKSPACE_SKILLS_DIR = Path.home() / '.qclaw' / 'workspace' / 'skills'
USAGE_LOG_PATH       = WORKSPACE_SKILLS_DIR / '.skill_usage.json'
# 首次登录时间锚点文件（QClaw AppData 目录创建时间）
QCLAW_APPDATA        = Path.home() / 'AppData' / 'Roaming' / 'QClaw'

# ─── 配置 ────────────────────────────────────────────────────────────────────
AUTO_CLEAN_DAYS = 30

# 保护名单：永不自动删除
PROTECTED_SKILLS = {
    'qclaw-rules', 'qclaw-env', 'qclaw-openclaw', 'qclaw-calendar-guide',
    'find-skills', 'skillhub-preference', 'skill-viewer'
}

# 技能分类映射
SKILL_CATEGORIES = {
    '核心系统':   ['qclaw-rules', 'qclaw-env', 'qclaw-openclaw', 'qclaw-calendar-guide'],
    '搜索与信息': ['search', 'multi-search-engine', 'find-skills', 'tavily-search', 'tavily-ai'],
    '文档处理':   ['docx', 'pdf', 'pptx', 'xlsx', 'tencent-docs', 'create-readme', 'changelog-maintenance'],
    '设计与前端': ['frontend-design', 'web-design-guidelines', 'canvas-design', 'algorithmic-art'],
    '浏览器与测试': ['agent-browser', 'webapp-testing'],
    '数据与分析': ['analytics-dashboard', 'quant-backtest', 'macro-monitor', 'log-analyzer'],
    '内容创作':   ['content-factory', 'content-repurposer', 'video-script', 'humanize-ai-text',
                   'wechat-article-crayon', 'wechat-article-typeset'],
    '效率工具':   ['gog', 'capability-evolver', 'proactive-agent', 'niuamaxia-scheduler', 'file-skill'],
    '学术与研究': ['arxiv-reader', 'arxiv-watcher', 'citation-manager', 'study-habits'],
    '生活娱乐':   ['movie-advisor', 'music-recommender', 'travel-planner', 'tarot', 'weather'],
    '健康管理':   ['nutritionist', 'habit-coach', 'habit-tracker'],
    '新闻资讯':   ['news-summary', 'tech-news-digest'],
    '安全审计':   ['skill-vetter', 'skill-creator'],
    '邮件通讯':   ['email-skill', 'imap-smtp-email'],
    '股票金融':   ['stock', 'stock-copilot-pro', 'stock-price-query',
                   'stock-screener-cn', 'stock-watcher'],
    '编程开发':   ['clangd-lsp', 'code-mentor', 'cpp', 'cpp-pro', 'debug-checklist',
                   'lsp', 'lsp-python', 'py', 'python', 'python-code-test',
                   'python-dataviz', 'python-executor', 'python-script-generator',
                   'feishu-docx-powerwrite', 'wps-skill'],
    '数学':       ['math', 'math-evaluate', 'math-solver', 'math-utils-native',
                   'mathproofs-claw', 'precision-calc', 'office'],
    '独家密法':   ['skill-viewer'],
    '其他':       []
}


# ─── 首次登录时间 ─────────────────────────────────────────────────────────────

def get_first_login_time() -> datetime:
    """
    取用户首次登录时间：
    优先读 usage_log 中的 _first_login 字段（持久化），
    否则用 QClaw AppData 目录创建时间，并写入 log 保存。
    """
    log = load_usage_log()
    if '_first_login' in log:
        try:
            return datetime.fromisoformat(log['_first_login'])
        except Exception:
            pass

    # 从文件系统取
    if QCLAW_APPDATA.exists():
        ts = QCLAW_APPDATA.stat().st_ctime
        first = datetime.fromtimestamp(ts)
    else:
        first = datetime.now()

    log['_first_login'] = first.isoformat()
    save_usage_log(log)
    return first


# ─── 使用记录 I/O ─────────────────────────────────────────────────────────────

def load_usage_log() -> Dict:
    if USAGE_LOG_PATH.exists():
        try:
            return json.loads(USAGE_LOG_PATH.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {}


def save_usage_log(log: Dict):
    USAGE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    USAGE_LOG_PATH.write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8'
    )


def record_usage(skill_name: str):
    """记录 skill 使用时间"""
    log = load_usage_log()
    log[skill_name] = datetime.now().isoformat()
    save_usage_log(log)


def get_last_used(skill_name: str, log: Dict) -> Optional[datetime]:
    ts = log.get(skill_name)
    if ts and not ts.startswith('_'):
        try:
            return datetime.fromisoformat(ts)
        except Exception:
            pass
    return None


def get_install_time(skill: Dict) -> Optional[datetime]:
    """获取 skill 安装时间（目录创建时间）"""
    try:
        return datetime.fromisoformat(skill['installed_at'])
    except Exception:
        return None


def should_delete(skill: Dict, log: Dict, first_login: datetime) -> tuple:
    """
    判断是否应删除，返回 (bool, reason_str)

    规则：
    - 从未使用：以 max(首次登录, 安装时间) 为起点，超过30天 → 删
      特例：当天刚装的 skill，首次登录计时器不生效
    - 用过：从最后一次使用时间重新起算，超过30天未再用 → 删
    """
    name = skill['name']
    last_used = get_last_used(name, log)
    now = datetime.now()

    if last_used is not None:
        # 用过：从最后使用时间重新起算
        days = (now - last_used).days
        if days >= AUTO_CLEAN_DAYS:
            return True, f'上次使用后 {days} 天未再使用'
        return False, ''

    # 从未使用
    install_time = get_install_time(skill)
    is_installed_today = install_time and install_time.date() == now.date()

    # 计时器B：安装时间起
    if install_time:
        days_from_install = (now - install_time).days
        if days_from_install >= AUTO_CLEAN_DAYS:
            return True, f'安装起 {days_from_install} 天未使用'

    # 计时器A：首次登录起（当天刚装的跳过）
    if not is_installed_today:
        days_from_login = (now - first_login).days
        if days_from_login >= AUTO_CLEAN_DAYS:
            return True, f'首次登录起 {days_from_login} 天未使用'

    return False, ''


# ─── 今日操作日志 ─────────────────────────────────────────────────────────────

TODAY_LOG_KEY = f'_today_{date.today().isoformat()}'


def append_today_event(event_type: str, skill_name: str):
    """记录今日新装/删除事件"""
    log = load_usage_log()
    today = log.setdefault(TODAY_LOG_KEY, {'installed': [], 'deleted': []})
    if skill_name not in today[event_type]:
        today[event_type].append(skill_name)
    save_usage_log(log)


def get_today_events() -> Dict:
    log = load_usage_log()
    return log.get(TODAY_LOG_KEY, {'installed': [], 'deleted': []})


# ─── 主类 ─────────────────────────────────────────────────────────────────────

class SkillViewer:
    def __init__(self):
        self.skills_dirs = [
            Path('D:/Program Files/QClaw/resources/openclaw/config/skills'),
            WORKSPACE_SKILLS_DIR,
            Path.home() / '.agents' / 'skills',
        ]
        self.deletable_dir = WORKSPACE_SKILLS_DIR
        self.skills: List[Dict] = []

    def scan_skills(self) -> List[Dict]:
        skills = []
        seen = set()
        for skills_dir in self.skills_dirs:
            if not skills_dir.exists():
                continue
            for skill_dir in skills_dir.iterdir():
                if not skill_dir.is_dir():
                    continue
                name = skill_dir.name
                if name in seen or name.startswith('.'):
                    continue
                seen.add(name)
                info = self._parse_skill(skill_dir)
                info['name'] = name
                info['category'] = self._categorize_skill(name)
                info['deletable'] = str(skill_dir).startswith(str(self.deletable_dir))
                # 记录安装时间（目录创建时间）
                try:
                    info['installed_at'] = datetime.fromtimestamp(
                        skill_dir.stat().st_ctime
                    ).isoformat()
                except Exception:
                    info['installed_at'] = None
                skills.append(info)
        self.skills = sorted(skills, key=lambda x: x['name'])
        return self.skills

    def _parse_skill(self, skill_dir: Path) -> Dict:
        info = {'description': '', 'triggers': [], 'path': str(skill_dir)}
        skill_md = skill_dir / 'SKILL.md'
        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8', errors='ignore')
            m = re.search(r'description:\s*(.+)', content)
            if m:
                info['description'] = m.group(1).strip().strip('"')
            tm = re.search(r'triggers:\s*\n((?:\s*-\s*.+\n)*)', content)
            if tm:
                info['triggers'] = [t.strip('- \n') for t in tm.group(1).split('\n') if t.strip()]
        return info

    def _categorize_skill(self, name: str) -> str:
        for cat, skills in SKILL_CATEGORIES.items():
            if name.lower() in [s.lower() for s in skills]:
                return cat
            for s in skills:
                if s.lower() in name.lower() or name.lower() in s.lower():
                    return cat
        return '其他'

    # ── 今日提醒横幅 ──────────────────────────────────────────────────────────

    def _today_banner(self) -> str:
        events = get_today_events()
        lines = []
        if events['installed']:
            lines.append('╔' + '═' * 52 + '╗')
            lines.append('║  🆕  今日新安装的 Skill' + ' ' * 29 + '║')
            for s in events['installed']:
                line = f'║    • {s}'
                lines.append(line + ' ' * (53 - len(line)) + '║')
            lines.append('╚' + '═' * 52 + '╝')
        if events['deleted']:
            lines.append('╔' + '═' * 52 + '╗')
            lines.append('║  🗑️  今日已自动删除的 Skill' + ' ' * 26 + '║')
            for s in events['deleted']:
                line = f'║    • {s}'
                lines.append(line + ' ' * (53 - len(line)) + '║')
            lines.append('╚' + '═' * 52 + '╝')
        return '\n'.join(lines)

    # ── 列表 ──────────────────────────────────────────────────────────────────

    def _usage_tag(self, skill: Dict, log: Dict, first_login: datetime) -> tuple:
        """生成使用状态标签，返回 (tag_str, will_delete)"""
        name = skill['name']
        last = get_last_used(name, log)
        now = datetime.now()

        if last:
            d = (now - last).days
            will_delete = should_delete(skill, log, first_login)[0]
            return f'[{d}天前使用]', will_delete

        # 从未使用：展示安装天数，无安装记录则用登录天数
        install_time = get_install_time(skill)
        d = (now - install_time).days if install_time else (now - first_login).days
        will_delete = should_delete(skill, log, first_login)[0]
        return f'[从未使用/{d}天]', will_delete

    def list_all(self) -> str:
        if not self.skills:
            self.scan_skills()
        log = load_usage_log()
        first_login = get_first_login_time()

        banner = self._today_banner()
        lines = []
        if banner:
            lines.append(banner)
            lines.append('')

        lines += ['📚 OpenClaw 已安装技能列表', '=' * 50, '']
        by_cat: Dict[str, List] = {}
        for skill in self.skills:
            by_cat.setdefault(skill['category'], []).append(skill)

        for cat in list(SKILL_CATEGORIES.keys()) + ['其他']:
            if cat not in by_cat:
                continue
            skills = by_cat[cat]
            lines.append(f'\n【{cat}】({len(skills)})')
            lines.append('-' * 40)
            for skill in skills:
                tag, will_del = self._usage_tag(skill, log, first_login)
                desc = skill['description'][:38] + '..' if len(skill['description']) > 38 else skill['description']
                protected = skill['name'] in PROTECTED_SKILLS
                warn = ' ⚠️即将删除' if will_del and not protected else ''
                lines.append(f'  • {skill["name"]}  {tag}{warn}')
                if desc:
                    lines.append(f'    {desc}')

        lines += ['', '=' * 50, f'总计: {len(self.skills)} 个技能',
                  f'首次登录: {first_login.strftime("%Y-%m-%d")}  |  清理阈值: {AUTO_CLEAN_DAYS} 天']
        return '\n'.join(lines)

    def list_by_category(self, category: str) -> str:
        if not self.skills:
            self.scan_skills()
        matched = next((c for c in SKILL_CATEGORIES if category in c or c in category), None)
        if not matched:
            return f'未找到分类: {category}'
        skills = [s for s in self.skills if s['category'] == matched]
        lines = [f'📂 {matched} 技能列表 ({len(skills)})', '=' * 50, '']
        for skill in skills:
            lines.append(f'• {skill["name"]}')
            if skill['description']:
                lines.append(f'  {skill["description"]}')
            if skill['triggers']:
                lines.append(f'  触发词: {", ".join(skill["triggers"][:3])}')
            lines.append('')
        return '\n'.join(lines)

    def search(self, keyword: str) -> str:
        if not self.skills:
            self.scan_skills()
        kw = keyword.lower()
        results = [s for s in self.skills
                   if kw in s['name'].lower() or kw in s['description'].lower()
                   or kw in s['category'].lower()
                   or any(kw in t.lower() for t in s['triggers'])]
        if not results:
            return f'未找到包含 "{keyword}" 的技能'
        lines = [f'🔍 搜索结果: "{keyword}" ({len(results)})', '=' * 50, '']
        for s in results:
            lines += [f'• {s["name"]} [{s["category"]}]', f'  {s["description"]}', '']
        return '\n'.join(lines)

    def get_detail(self, skill_name: str) -> str:
        if not self.skills:
            self.scan_skills()
        log = load_usage_log()
        first_login = get_first_login_time()
        for skill in self.skills:
            if skill_name.lower() in skill['name'].lower():
                last = get_last_used(skill['name'], log)
                now = datetime.now()
                if last:
                    d = (now - last).days
                    last_str = last.strftime('%Y-%m-%d %H:%M')
                else:
                    install_time = get_install_time(skill)
                    d = (now - install_time).days if install_time else (now - first_login).days
                    last_str = f'从未使用（安装/登录起 {d} 天）'
                will_del, reason = should_delete(skill, log, first_login)
                del_str = f'  ⚠️ {reason}' if will_del and skill['name'] not in PROTECTED_SKILLS else ''
                lines = [f'📖 {skill["name"]}', '=' * 50, '',
                         f'分类: {skill["category"]}',
                         f'路径: {skill["path"]}',
                         f'最后使用: {last_str}{del_str}',
                         f'距今: {d} 天']
                if skill['description']:
                    lines += ['', f'描述: {skill["description"]}']
                if skill['triggers']:
                    lines.append(f'\n触发词: {", ".join(skill["triggers"])}')
                skill_md = Path(skill['path']) / 'SKILL.md'
                if skill_md.exists():
                    content = skill_md.read_text(encoding='utf-8', errors='ignore')
                    lines += ['\n' + '=' * 50, 'SKILL.md 内容:', '=' * 50,
                              content[:2000] + ('...(已截断)' if len(content) > 2000 else '')]
                return '\n'.join(lines)
        return f'未找到技能: {skill_name}'

    def show_usage(self) -> str:
        if not self.skills:
            self.scan_skills()
        log = load_usage_log()
        first_login = get_first_login_time()
        now = datetime.now()
        lines = [f'📊 Skill 使用记录  (首次登录: {first_login.strftime("%Y-%m-%d")})',
                 '=' * 50, '']
        rows = []
        for skill in self.skills:
            last = get_last_used(skill['name'], log)
            if last:
                d = (now - last).days
                last_str = last.strftime('%Y-%m-%d %H:%M')
                sort_key = d
            else:
                install_time = get_install_time(skill)
                d = (now - install_time).days if install_time else (now - first_login).days
                last_str = '从未使用'
                sort_key = 9999
            will_del = should_delete(skill, log, first_login)[0]
            rows.append((sort_key, skill['name'], last_str, d, will_del))
        rows.sort(reverse=True)
        for _, name, last_str, d, will_del in rows:
            lock = ' 🔒' if name in PROTECTED_SKILLS else ''
            warn = ' ⚠️ 超期将删' if will_del and name not in PROTECTED_SKILLS else ''
            lines.append(f'  {name}{lock}{warn}')
            lines.append(f'    最后使用: {last_str}  ({d} 天)')
        lines += ['', '=' * 50, f'总计: {len(rows)} 个技能']
        return '\n'.join(lines)

    # ── 自动清理 ──────────────────────────────────────────────────────────────

    def auto_clean(self, dry_run: bool = False) -> str:
        if not self.skills:
            self.scan_skills()
        log = load_usage_log()
        first_login = get_first_login_time()

        to_delete = []
        for skill in self.skills:
            name = skill['name']
            if name in PROTECTED_SKILLS:
                continue
            if not skill['deletable']:
                continue
            ok, reason = should_delete(skill, log, first_login)
            if ok:
                to_delete.append((skill, reason))

        if not to_delete:
            return f'✅ 没有需要清理的 skill（阈值 {AUTO_CLEAN_DAYS} 天，首次登录 {first_login.strftime("%Y-%m-%d")}）'

        lines = [f'🗑️  自动清理：{len(to_delete)} 个 skill 超过 {AUTO_CLEAN_DAYS} 天未使用', '']
        deleted, failed = [], []

        for skill, reason in to_delete:
            name = skill['name']
            path = Path(skill['path'])

            if dry_run:
                lines.append(f'  [预览] {name}  ({reason})')
            else:
                try:
                    shutil.rmtree(path)
                    if name in log:
                        del log[name]
                    deleted.append(name)
                    append_today_event('deleted', name)
                    lines.append(f'  ✅ 已删除: {name}  ({reason})')
                except Exception as e:
                    failed.append(name)
                    lines.append(f'  ❌ 失败: {name}  ({e})')

        if not dry_run:
            save_usage_log(log)
            lines += ['', f'共删除 {len(deleted)} 个，失败 {len(failed)} 个。']

        return '\n'.join(lines)


# ─── 入口 ─────────────────────────────────────────────────────────────────────

def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    viewer = SkillViewer()

    if len(sys.argv) < 2:
        # 主动调用：显示今日提醒 + 列表
        print(viewer.list_all())
        return

    cmd = sys.argv[1]

    if cmd in ('list', 'all'):
        print(viewer.list_all())
    elif cmd == 'category' and len(sys.argv) > 2:
        print(viewer.list_by_category(sys.argv[2]))
    elif cmd == 'search' and len(sys.argv) > 2:
        print(viewer.search(sys.argv[2]))
    elif cmd == 'detail' and len(sys.argv) > 2:
        print(viewer.get_detail(sys.argv[2]))
    elif cmd == 'record' and len(sys.argv) > 2:
        record_usage(sys.argv[2])
        print(f'✅ 已记录 {sys.argv[2]} 使用时间')
    elif cmd == 'installed' and len(sys.argv) > 2:
        # 新装 skill 时调用：skill_viewer.py installed <name>
        append_today_event('installed', sys.argv[2])
        print(f'✅ 已记录 {sys.argv[2]} 今日安装')
    elif cmd == 'usage':
        print(viewer.show_usage())
    elif cmd == 'clean':
        print(viewer.auto_clean(dry_run=False))
    elif cmd == 'clean-dry':
        print(viewer.auto_clean(dry_run=True))
    else:
        print('''Usage:
  skill_viewer.py                       # 列出所有技能（含今日提醒）
  skill_viewer.py list                  # 同上
  skill_viewer.py category <name>       # 按分类查看
  skill_viewer.py search <keyword>      # 搜索技能
  skill_viewer.py detail <name>         # 查看详情
  skill_viewer.py usage                 # 查看使用记录
  skill_viewer.py record <skill_name>   # 记录某 skill 使用时间
  skill_viewer.py installed <name>      # 记录某 skill 今日安装
  skill_viewer.py clean-dry             # 预览将被清理的 skill
  skill_viewer.py clean                 # 自动删除超期 skill
''')


if __name__ == '__main__':
    main()
