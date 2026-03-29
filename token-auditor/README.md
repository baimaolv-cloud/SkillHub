# token-auditor

TOKEN 娑堣€楀璁″伐鍏?- 缁熻褰撴棩 TOKEN 娑堣€?TOP3 浠诲姟锛岀敓鎴愬璁℃姤鍛娿€?
## 鍔熻兘鐗规€?
- 鉁?璁板綍姣忎釜浠诲姟鐨?TOKEN 娑堣€?- 鉁?鑷姩鐢熸垚姣忔棩 TOP3 娑堣€楁姤鍛?- 鉁?鏀寔鎸変换鍔＄被鍨嬪垎绫伙紙DEBUG/CODE/REPORT/ROUTINE锛?- 鉁?鎻愪緵浼樺寲寤鸿

## 瀹夎

```bash
# 鍏嬮殕浠撳簱
git clone https://github.com/baimaolv-cloud/token-auditor.git

# 鎴栫洿鎺ヤ笅杞藉埌 OpenClaw skills 鐩綍
cp -r token-auditor ~/.qclaw/workspace/skills/
```

## 浣跨敤鏂规硶

### 1. 璁板綍浠诲姟娑堣€?
```bash
python scripts/log_token.py --task "qqbrowser-skill 淇" --type DEBUG --in 3200 --out 4100 --cached 153000
```

### 2. 鐢熸垚鏃ユ姤

```bash
python scripts/log_token.py --report
```

### 3. 鏌ョ湅鎽樿

```bash
python scripts/log_token.py --summary
```

## 鏃ュ織鏂囦欢缁撴瀯

```
workspace/logs/token-audit/
鈹溾攢鈹€ 2026-03-29.jsonl         # 褰撴棩璇︾粏璁板綍
鈹溾攢鈹€ 2026-03-29-summary.md    # 褰撴棩 TOP3 鎶ュ憡
鈹斺攢鈹€ archive/                 # 鍘嗗彶褰掓。
```

## 瀹¤鎶ュ憡绀轰緥

```markdown
# TOKEN 瀹¤鏃ユ姤 - 2026-03-29

## 馃搳 鎬昏

- **鎬绘秷鑰?*锛?2.6K TOKEN (4.7K in + 7.9K out)
- **缂撳瓨鍒╃敤**锛?33K TOKEN
- **浠诲姟鏁伴噺**锛? 涓?
## 馃敐 TOP3 娑堣€椾换鍔?
### 1锔忊儯 qqbrowser-skill 淇
- **娑堣€?*锛?.3K TOKEN (58%)
- **绫诲瀷**锛欴EBUG
- **浼樺寲寤鸿**锛氫娇鐢?browser_get_info --type title 鏇夸唬 browser_snapshot
```

## 鍙傛暟璇存槑

| 鍙傛暟 | 璇存槑 | 绀轰緥 |
|------|------|------|
| `--task` | 浠诲姟鍚嶇О | "qqbrowser-skill 淇" |
| `--type` | 浠诲姟绫诲瀷 | DEBUG/CODE/REPORT/ROUTINE |
| `--in` | 杈撳叆 TOKEN | 3200 |
| `--out` | 杈撳嚭 TOKEN | 4100 |
| `--cached` | 缂撳瓨 TOKEN | 153000 |
| `--cost` | 鎴愭湰 USD | 0.0000 |
| `--session` | 浼氳瘽 ID | session-xxx |
| `--report` | 鐢熸垚鎶ュ憡 | - |
| `--summary` | 鏄剧ず鎽樿 | - |

## 鐗堟湰鍘嗗彶

- **v1.0** (2026-03-29)
  - 鍒濆鐗堟湰
  - 鏀寔浠诲姟璁板綍鍜?TOP3 鎶ュ憡鐢熸垚

## 浣滆€?
灏忚櫨 (Xiao Xia) 馃 - OpenClaw AI Assistant

## 璁稿彲璇?
MIT License
