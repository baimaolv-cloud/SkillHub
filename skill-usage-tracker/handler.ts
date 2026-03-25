import { execSync } from "child_process";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";

// skill-viewer 使用记录文件路径
const USAGE_LOG = path.join(
  os.homedir(),
  ".qclaw",
  "workspace",
  "skills",
  ".skill_usage.json"
);

// skill 目录列表
const SKILL_DIRS = [
  path.join(os.homedir(), ".qclaw", "workspace", "skills"),
  "D:/Program Files/QClaw/resources/openclaw/config/skills",
];

// 缓存：skill 名 → triggers 列表（避免每次重新扫描）
let skillTriggersCache: Map<string, string[]> | null = null;
let cacheBuiltAt = 0;
const CACHE_TTL_MS = 5 * 60 * 1000; // 5分钟刷新一次

function buildSkillTriggersCache(): Map<string, string[]> {
  const map = new Map<string, string[]>();
  for (const dir of SKILL_DIRS) {
    if (!fs.existsSync(dir)) continue;
    for (const entry of fs.readdirSync(dir)) {
      if (entry.startsWith(".")) continue;
      const skillMd = path.join(dir, entry, "SKILL.md");
      if (!fs.existsSync(skillMd)) continue;
      try {
        const content = fs.readFileSync(skillMd, "utf-8");
        // 提取 triggers
        const triggersMatch = content.match(/triggers:\s*\n((?:\s*-\s*.+\n)*)/);
        const triggers: string[] = [];
        if (triggersMatch) {
          for (const line of triggersMatch[1].split("\n")) {
            const t = line.replace(/^\s*-\s*/, "").trim();
            if (t) triggers.push(t.toLowerCase());
          }
        }
        // 也把 skill 名本身作为触发词
        triggers.push(entry.toLowerCase());
        map.set(entry, triggers);
      } catch {
        // ignore
      }
    }
  }
  return map;
}

function getSkillTriggers(): Map<string, string[]> {
  const now = Date.now();
  if (!skillTriggersCache || now - cacheBuiltAt > CACHE_TTL_MS) {
    skillTriggersCache = buildSkillTriggersCache();
    cacheBuiltAt = now;
  }
  return skillTriggersCache;
}

function recordUsage(skillName: string): void {
  try {
    // 直接写 JSON，不依赖 python 命令
    let log: Record<string, string> = {};
    if (fs.existsSync(USAGE_LOG)) {
      log = JSON.parse(fs.readFileSync(USAGE_LOG, "utf-8"));
    }
    log[skillName] = new Date().toISOString();
    fs.writeFileSync(USAGE_LOG, JSON.stringify(log, null, 2), "utf-8");
  } catch (e) {
    console.error(`[skill-usage-tracker] Failed to record ${skillName}:`, e);
  }
}

function detectSkills(text: string): string[] {
  const lower = text.toLowerCase();
  const triggers = getSkillTriggers();
  const matched = new Set<string>();

  for (const [skillName, skillTriggers] of triggers) {
    for (const trigger of skillTriggers) {
      if (trigger.length >= 3 && lower.includes(trigger)) {
        matched.add(skillName);
        break;
      }
    }
  }
  return Array.from(matched);
}

const handler = async (event: any) => {
  if (event.type !== "message" || event.action !== "preprocessed") return;

  const body: string = event.context?.bodyForAgent || event.context?.body || "";
  if (!body || body.length < 3) return;

  const matched = detectSkills(body);
  if (matched.length === 0) return;

  for (const skillName of matched) {
    recordUsage(skillName);
    console.log(`[skill-usage-tracker] recorded: ${skillName}`);
  }
};

export default handler;
