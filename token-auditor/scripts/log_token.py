#!/usr/bin/env python3
"""
TOKEN 瀹¤鏃ュ織璁板綍宸ュ叿

鐢ㄦ硶锛?  python log_token.py --task "qqbrowser-skill 淇" --type DEBUG --in 3200 --out 4100 --cached 153000
  python log_token.py --report                    # 鐢熸垚褰撴棩 TOP3 鎶ュ憡
  python log_token.py --summary                   # 鏄剧ず褰撴棩鎽樿
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 鏃ュ織鐩綍
LOG_DIR = Path.home() / ".qclaw" / "workspace" / "logs" / "token-audit"
ARCHIVE_DIR = LOG_DIR / "archive"

def ensure_dirs():
    """纭繚鏃ュ織鐩綍瀛樺湪"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

def get_today_log() -> Path:
    """鑾峰彇褰撴棩鏃ュ織鏂囦欢璺緞"""
    today = datetime.now().strftime("%Y-%m-%d")
    return LOG_DIR / f"{today}.jsonl"

def get_today_summary() -> Path:
    """鑾峰彇褰撴棩鎽樿鏂囦欢璺緞"""
    today = datetime.now().strftime("%Y-%m-%d")
    return LOG_DIR / f"{today}-summary.md"

def log_token(
    task_name: str,
    task_type: str,
    tokens_in: int,
    tokens_out: int,
    tokens_cached: int,
    cost_usd: float = 0.0,
    session_id: Optional[str] = None,
    details: Optional[dict] = None
):
    """璁板綍 TOKEN 娑堣€?""
    ensure_dirs()
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "task_name": task_name,
        "task_type": task_type,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "tokens_cached": tokens_cached,
        "tokens_total": tokens_in + tokens_out,
        "cost_usd": cost_usd,
        "session_id": session_id or "unknown",
        "details": details or {}
    }
    
    log_file = get_today_log()
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    print(f"[OK] Logged: {task_name} ({log_entry['tokens_total']} TOKEN)")
    return log_entry

def generate_report():
    """鐢熸垚褰撴棩 TOP3 鎶ュ憡"""
    ensure_dirs()
    
    log_file = get_today_log()
    if not log_file.exists():
        print("鉂?褰撴棩鏃?TOKEN 璁板綍")
        return
    
    # 璇诲彇鎵€鏈夎褰?    records = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    if not records:
        print("鉂?褰撴棩鏃?TOKEN 璁板綍")
        return
    
    # 缁熻
    total_in = sum(r["tokens_in"] for r in records)
    total_out = sum(r["tokens_out"] for r in records)
    total_cached = sum(r["tokens_cached"] for r in records)
    total_cost = sum(r["cost_usd"] for r in records)
    
    # 鎸?task_name 鍒嗙粍缁熻
    task_stats = {}
    for r in records:
        name = r["task_name"]
        if name not in task_stats:
            task_stats[name] = {
                "count": 0,
                "tokens_in": 0,
                "tokens_out": 0,
                "tokens_cached": 0,
                "cost_usd": 0.0,
                "type": r["task_type"],
                "details": []
            }
        task_stats[name]["count"] += 1
        task_stats[name]["tokens_in"] += r["tokens_in"]
        task_stats[name]["tokens_out"] += r["tokens_out"]
        task_stats[name]["tokens_cached"] += r["tokens_cached"]
        task_stats[name]["cost_usd"] += r["cost_usd"]
        task_stats[name]["details"].append(r["details"])
    
    # 鎺掑簭 TOP3
    top3 = sorted(
        task_stats.items(),
        key=lambda x: x[1]["tokens_in"] + x[1]["tokens_out"],
        reverse=True
    )[:3]
    
    # 鐢熸垚鎶ュ憡
    today = datetime.now().strftime("%Y-%m-%d")
    report = f"""# TOKEN 瀹¤鏃ユ姤 - {today}

## 馃搳 鎬昏

- **鎬绘秷鑰?*锛歿total_in + total_out}K TOKEN ({total_in}K in + {total_out}K out)
- **缂撳瓨鍒╃敤**锛歿total_cached}K TOKEN
- **棰勪及鎴愭湰**锛?{total_cost:.4f}
- **浠诲姟鏁伴噺**锛歿len(task_stats)} 涓?
## 馃敐 TOP3 娑堣€椾换鍔?
"""
    
    for i, (task_name, stats) in enumerate(top3, 1):
        total_tokens = stats["tokens_in"] + stats["tokens_out"]
        percentage = (total_tokens / (total_in + total_out) * 100) if (total_in + total_out) > 0 else 0
        
        report += f"""### {i}锔忊儯 {task_name}
- **娑堣€?*锛歿total_tokens}K TOKEN ({percentage:.1f}%)
- **绫诲瀷**锛歿stats["type"]}
- **娆℃暟**锛歿stats["count"]} 娆?- **璇︽儏**锛?"""
        
        # 姹囨€?details
        all_details = {}
        for d in stats["details"]:
            for k, v in d.items():
                if k not in all_details:
                    all_details[k] = 0
                all_details[k] += v if isinstance(v, (int, float)) else 1
        
        for k, v in all_details.items():
            report += f"  - {k}锛歿v} 娆n"
        
        report += "\n"
    
    report += f"""## 馃挕 浼樺寲寤鸿

_鏍规嵁浠婃棩娑堣€楁儏鍐碉紝寤鸿鍏虫敞 TOP1 浠诲姟鐨?TOKEN 浼樺寲_

---

*鐢熸垚鏃堕棿锛歿datetime.now().strftime("%Y-%m-%d %H:%M")}*
*绱浠诲姟锛歿len(records)} 鏉¤褰?
"""
    
    # 鍐欏叆鎶ュ憡
    summary_file = get_today_summary()
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"[OK] Report generated: {summary_file}")
    print(report)

def show_summary():
    """鏄剧ず褰撴棩鎽樿"""
    log_file = get_today_log()
    if not log_file.exists():
        print("鉂?褰撴棩鏃?TOKEN 璁板綍")
        return
    
    records = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    if not records:
        print("鉂?褰撴棩鏃?TOKEN 璁板綍")
        return
    
    total_in = sum(r["tokens_in"] for r in records)
    total_out = sum(r["tokens_out"] for r in records)
    total_cached = sum(r["tokens_cached"] for r in records)
    
    print(f"""
馃搳 浠婃棩 TOKEN 娑堣€楁憳瑕?鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣
杈撳叆 TOKEN锛歿total_in}K
杈撳嚭 TOKEN锛歿total_out}K
缂撳瓨 TOKEN锛歿total_cached}K
鎬绘秷鑰楋細{total_in + total_out}K
浠诲姟鏁伴噺锛歿len(records)} 涓?鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣鈹佲攣
""")

def main():
    parser = argparse.ArgumentParser(description="TOKEN 瀹¤宸ュ叿")
    parser.add_argument("--task", help="浠诲姟鍚嶇О")
    parser.add_argument("--type", default="UNKNOWN", help="浠诲姟绫诲瀷 (DEBUG/CODE/REPORT/ROUTINE)")
    parser.add_argument("--in", dest="tokens_in", type=int, default=0, help="杈撳叆 TOKEN")
    parser.add_argument("--out", dest="tokens_out", type=int, default=0, help="杈撳嚭 TOKEN")
    parser.add_argument("--cached", dest="tokens_cached", type=int, default=0, help="缂撳瓨 TOKEN")
    parser.add_argument("--cost", dest="cost_usd", type=float, default=0.0, help="鎴愭湰 USD")
    parser.add_argument("--session", dest="session_id", help="浼氳瘽 ID")
    parser.add_argument("--report", action="store_true", help="鐢熸垚鎶ュ憡")
    parser.add_argument("--summary", action="store_true", help="鏄剧ず鎽樿")
    
    args = parser.parse_args()
    
    if args.report:
        generate_report()
    elif args.summary:
        show_summary()
    elif args.task:
        log_token(
            task_name=args.task,
            task_type=args.type,
            tokens_in=args.tokens_in,
            tokens_out=args.tokens_out,
            tokens_cached=args.tokens_cached,
            cost_usd=args.cost_usd,
            session_id=args.session_id
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
