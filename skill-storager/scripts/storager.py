#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill-storager — 全能文档存储与管理
支持：本地存储 / 腾讯云COS / Git / Obsidian / 腾讯文档
"""

import os
import sys
import io
import json
import re
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ─── 路径 ────────────────────────────────────────────────────────────────────
SKILL_DIR    = Path(__file__).parent.parent
CONFIG_FILE  = SKILL_DIR / 'config' / 'config.json'
INDEX_FILE   = SKILL_DIR / 'config' / 'index.json'

# ─── 默认配置 ─────────────────────────────────────────────────────────────────
DEFAULT_CONFIG = {
    "backend": "local",
    "local": {
        "root": str(Path.home() / '.qclaw' / 'workspace' / 'documents')
    },
    "cos": {
        "secret_id": "",
        "secret_key": "",
        "bucket": "",
        "region": "ap-guangzhou"
    },
    "git": {
        "repo": "",
        "branch": "main"
    },
    "obsidian": {
        "vault": ""
    }
}

# ─── 自动分类规则 ─────────────────────────────────────────────────────────────
CATEGORY_RULES = [
    (r'会议|纪要|议程|决议',           '会议纪要'),
    (r'报告|总结|汇报|周报|月报',       '工作报告'),
    (r'方案|计划|规划|策略',           '方案计划'),
    (r'合同|协议|条款|甲方|乙方',       '合同协议'),
    (r'技术|架构|设计|接口|API|代码',   '技术文档'),
    (r'财务|预算|费用|报销|账单',       '财务文档'),
    (r'简历|履历|求职',               '个人文档'),
    (r'笔记|备忘|todo|待办',          '笔记备忘'),
]

SUPPORTED_EXTS = {'.md', '.txt', '.pdf', '.docx', '.doc', '.xlsx', '.xls',
                  '.json', '.yaml', '.yml', '.csv', '.html', '.rst'}


# ─── 工具函数 ─────────────────────────────────────────────────────────────────

def load_config() -> Dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(cfg: Dict):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')


def load_index() -> Dict:
    if INDEX_FILE.exists():
        try:
            return json.loads(INDEX_FILE.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {}


def save_index(idx: Dict):
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding='utf-8')


def gen_id(path: str) -> str:
    return hashlib.md5(path.encode()).hexdigest()[:8].upper()


def auto_category(text: str) -> str:
    for pattern, cat in CATEGORY_RULES:
        if re.search(pattern, text):
            return cat
    return '其他'


def fmt_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f'{size:.1f}{unit}'
        size /= 1024
    return f'{size:.1f}TB'


# ─── 本地后端 ─────────────────────────────────────────────────────────────────

class LocalBackend:
    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, content: str, filename: str, category: str = '') -> Dict:
        if not category:
            category = auto_category(content + filename)
        cat_dir = self.root / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        filepath = cat_dir / filename
        # 避免重名
        if filepath.exists():
            stem = filepath.stem
            suffix = filepath.suffix
            ts = datetime.now().strftime('%H%M%S')
            filepath = cat_dir / f'{stem}_{ts}{suffix}'
        filepath.write_text(content, encoding='utf-8')
        doc_id = gen_id(str(filepath))
        return {'id': doc_id, 'path': str(filepath), 'category': category,
                'filename': filepath.name, 'size': len(content.encode())}

    def read(self, path: str) -> str:
        return Path(path).read_text(encoding='utf-8', errors='ignore')

    def delete(self, path: str) -> bool:
        p = Path(path)
        if p.exists():
            p.unlink()
            return True
        return False

    def list_all(self) -> List[Dict]:
        docs = []
        for f in self.root.rglob('*'):
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS:
                rel = f.relative_to(self.root)
                parts = rel.parts
                category = parts[0] if len(parts) > 1 else '其他'
                stat = f.stat()
                docs.append({
                    'id':       gen_id(str(f)),
                    'filename': f.name,
                    'path':     str(f),
                    'category': category,
                    'size':     fmt_size(stat.st_size),
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    'ext':      f.suffix.lower()
                })
        return sorted(docs, key=lambda x: x['modified'], reverse=True)

    def search(self, keyword: str) -> List[Dict]:
        kw = keyword.lower()
        results = []
        for doc in self.list_all():
            if kw in doc['filename'].lower() or kw in doc['category'].lower():
                results.append(doc)
                continue
            try:
                content = Path(doc['path']).read_text(encoding='utf-8', errors='ignore')
                if kw in content.lower():
                    doc['snippet'] = self._snippet(content, kw)
                    results.append(doc)
            except Exception:
                pass
        return results

    def _snippet(self, content: str, kw: str) -> str:
        idx = content.lower().find(kw)
        if idx < 0:
            return ''
        start = max(0, idx - 40)
        end   = min(len(content), idx + 80)
        return '...' + content[start:end].replace('\n', ' ') + '...'


# ─── 主类 ─────────────────────────────────────────────────────────────────────

class Storager:
    def __init__(self):
        self.cfg = load_config()
        self.idx = load_index()
        backend = self.cfg.get('backend', 'local')
        if backend == 'local':
            self.backend = LocalBackend(self.cfg['local']['root'])
        else:
            # 其他后端暂时 fallback 到本地
            print(f'[warn] backend "{backend}" not yet implemented, using local')
            self.backend = LocalBackend(self.cfg['local']['root'])

    def _sync_index(self):
        """同步索引"""
        docs = self.backend.list_all()
        self.idx = {d['id']: d for d in docs}
        save_index(self.idx)

    # ── 存储 ──────────────────────────────────────────────────────────────────

    def store(self, content: str, filename: str, category: str = '') -> str:
        result = self.backend.save(content, filename, category)
        self.idx[result['id']] = result
        save_index(self.idx)
        lines = [
            f'✅ 文档已存储',
            f'   ID:       {result["id"]}',
            f'   文件名:   {result["filename"]}',
            f'   分类:     {result["category"]}',
            f'   路径:     {result["path"]}',
            f'   大小:     {fmt_size(result["size"])}',
        ]
        return '\n'.join(lines)

    # ── 读取 ──────────────────────────────────────────────────────────────────

    def open_doc(self, id_or_path: str) -> str:
        # 先按 ID 查
        if id_or_path.upper() in self.idx:
            doc = self.idx[id_or_path.upper()]
            content = self.backend.read(doc['path'])
            return f'📄 {doc["filename"]}  [{doc["category"]}]\n{"─"*50}\n{content}'
        # 再按路径查
        p = Path(id_or_path)
        if p.exists():
            return p.read_text(encoding='utf-8', errors='ignore')
        # 刷新索引再试
        self._sync_index()
        if id_or_path.upper() in self.idx:
            doc = self.idx[id_or_path.upper()]
            content = self.backend.read(doc['path'])
            return f'📄 {doc["filename"]}  [{doc["category"]}]\n{"─"*50}\n{content}'
        return f'❌ 未找到文档: {id_or_path}'

    # ── 列表 ──────────────────────────────────────────────────────────────────

    def list_docs(self, category: str = '', ext: str = '', limit: int = 50) -> str:
        self._sync_index()
        docs = self.backend.list_all()
        if category:
            docs = [d for d in docs if category in d['category']]
        if ext:
            ext = ext if ext.startswith('.') else f'.{ext}'
            docs = [d for d in docs if d['ext'] == ext.lower()]
        docs = docs[:limit]
        if not docs:
            return '📂 暂无文档'
        lines = [f'📂 文档列表 ({len(docs)} 条)', '─' * 50]
        cur_cat = ''
        for d in docs:
            if d['category'] != cur_cat:
                cur_cat = d['category']
                lines.append(f'\n【{cur_cat}】')
            lines.append(f'  [{d["id"]}] {d["filename"]}  {d["size"]}  {d["modified"]}')
        return '\n'.join(lines)

    # ── 搜索 ──────────────────────────────────────────────────────────────────

    def search(self, keyword: str) -> str:
        results = self.backend.search(keyword)
        if not results:
            return f'🔍 未找到包含 "{keyword}" 的文档'
        lines = [f'🔍 搜索: "{keyword}"  ({len(results)} 条)', '─' * 50]
        for d in results:
            lines.append(f'  [{d["id"]}] {d["filename"]}  [{d["category"]}]  {d["modified"]}')
            if d.get('snippet'):
                lines.append(f'    {d["snippet"]}')
        return '\n'.join(lines)

    # ── 删除 ──────────────────────────────────────────────────────────────────

    def delete(self, id_or_path: str) -> str:
        self._sync_index()
        doc = self.idx.get(id_or_path.upper())
        if doc:
            ok = self.backend.delete(doc['path'])
            if ok:
                del self.idx[id_or_path.upper()]
                save_index(self.idx)
                return f'🗑️ 已删除: {doc["filename"]}'
            return f'❌ 删除失败: {doc["path"]}'
        return f'❌ 未找到文档: {id_or_path}'

    # ── 配置 ──────────────────────────────────────────────────────────────────

    def show_config(self) -> str:
        lines = ['⚙️  skill-storager 配置', '─' * 50]
        lines.append(f'当前后端: {self.cfg.get("backend", "local")}')
        lines.append(f'本地路径: {self.cfg["local"]["root"]}')
        lines.append(f'文档数量: {len(self.backend.list_all())}')
        return '\n'.join(lines)

    def set_backend(self, backend: str) -> str:
        if backend not in ('local', 'cos', 'git', 'obsidian'):
            return f'❌ 不支持的后端: {backend}，可选: local / cos / git / obsidian'
        self.cfg['backend'] = backend
        save_config(self.cfg)
        return f'✅ 后端已切换为: {backend}'

    def set_local_root(self, path: str) -> str:
        self.cfg['local']['root'] = path
        save_config(self.cfg)
        Path(path).mkdir(parents=True, exist_ok=True)
        return f'✅ 本地存储路径已设置为: {path}'


# ─── 入口 ─────────────────────────────────────────────────────────────────────

def main():
    s = Storager()

    if len(sys.argv) < 2:
        print(s.show_config())
        return

    cmd = sys.argv[1]

    if cmd == 'list':
        cat = sys.argv[2] if len(sys.argv) > 2 else ''
        print(s.list_docs(category=cat))

    elif cmd == 'search' and len(sys.argv) > 2:
        print(s.search(' '.join(sys.argv[2:])))

    elif cmd == 'open' and len(sys.argv) > 2:
        print(s.open_doc(sys.argv[2]))

    elif cmd == 'store' and len(sys.argv) > 3:
        # store <filename> <content...>
        filename = sys.argv[2]
        content  = ' '.join(sys.argv[3:])
        print(s.store(content, filename))

    elif cmd == 'store-file' and len(sys.argv) > 2:
        # store-file <filepath> [category]
        filepath = Path(sys.argv[2])
        category = sys.argv[3] if len(sys.argv) > 3 else ''
        if not filepath.exists():
            print(f'❌ 文件不存在: {filepath}')
        else:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            print(s.store(content, filepath.name, category))

    elif cmd == 'delete' and len(sys.argv) > 2:
        print(s.delete(sys.argv[2]))

    elif cmd == 'config':
        print(s.show_config())

    elif cmd == 'set-backend' and len(sys.argv) > 2:
        print(s.set_backend(sys.argv[2]))

    elif cmd == 'set-root' and len(sys.argv) > 2:
        print(s.set_local_root(sys.argv[2]))

    else:
        print('''skill-storager — 全能文档存储与管理

用法:
  storager.py list [分类]              # 列出文档
  storager.py search <关键词>          # 搜索文档
  storager.py open <ID或路径>          # 打开文档
  storager.py store <文件名> <内容>    # 存储文本内容
  storager.py store-file <路径> [分类] # 存储本地文件
  storager.py delete <ID>             # 删除文档
  storager.py config                  # 查看配置
  storager.py set-backend <后端>      # 切换后端 (local/cos/git/obsidian)
  storager.py set-root <路径>         # 设置本地存储路径
''')


if __name__ == '__main__':
    main()
