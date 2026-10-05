"""Résume les sessions Claude Code récentes en un digest compact pour /improve-system.

Lit ~/.claude/projects/*/*.jsonl modifiés depuis le dernier passage (ou --days N),
garde : messages humains (tronqués), commandes /skills lancées, erreurs d'outils,
messages qui ressemblent à une correction. Écrit ~/.claude/improve-system/digest.md.

  python digest.py              # depuis le dernier passage (7 j si premier)
  python digest.py --days 30    # forcer une fenêtre
  python digest.py --mark       # enregistrer « maintenant » comme dernier passage
"""
import argparse, json, re, sys, time
from collections import Counter
from pathlib import Path

HOME = Path.home() / ".claude"
PROJECTS = HOME / "projects"
OUT = HOME / "improve-system"
STATE = OUT / "state.json"
MAX_CHARS = 50_000          # doit tenir dans un seul Read (~25k tokens)
MSG_CHARS = 350

CORRECTION = re.compile(
    r"\b(non|pas ça|pas ca|refais|recommence|encore|j'ai dit|je t'ai dit|pourquoi|arr[êe]te|faux|"
    r"bug|marche pas|fonctionne pas|c'est nul|toujours pas|n'importe quoi|t'as oubli|oublie pas|"
    r"au lieu de|pas comme ça|mauvais|cass[ée])\b", re.I)


def text_of(content):
    if isinstance(content, str):
        return content
    out = []
    for b in content or []:
        if isinstance(b, dict) and b.get("type") == "text":
            out.append(b.get("text", ""))
    return "\n".join(out)


def clean(s):
    m = re.search(r"<command-name>(.*?)</command-name>.*?<command-args>(.*?)</command-args>", s, re.S)
    if m:
        s = f"{m.group(1)} {m.group(2)}"
    s = re.sub(r"<(system-reminder|ide_[a-z_]+|local-command-[a-z]+)>.*?</\1>", "", s, flags=re.S)
    s = re.sub(r"<[^>]{1,40}>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def session(path):
    humans, errors, commands, tools = [], [], [], Counter()
    proj, start = path.parent.name, None
    for line in path.open(encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("isSidechain"):
            continue
        start = start or d.get("timestamp")
        if d.get("cwd"):
            proj = Path(d["cwd"]).name
        msg = d.get("message") or {}
        content = msg.get("content")
        if d.get("type") == "assistant" and isinstance(content, list):
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    tools[b.get("name", "?")] += 1
        if d.get("type") != "user":
            continue
        if isinstance(content, list):
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("is_error"):
                    c = b.get("content")
                    e = clean(c if isinstance(c, str) else text_of(c))
                    if e and "doesn't want" not in e and "rejected" not in e:
                        errors.append(e[:200])
        if d.get("toolUseResult") is not None or d.get("isMeta"):
            continue
        raw = text_of(content)
        if not raw or raw.startswith("Tool loaded") or "<task-notification>" in raw:
            continue
        m = re.search(r"<command-name>/?(.*?)</command-name>", raw)
        if m:
            commands.append(m.group(1))
        t = clean(raw)
        if t:
            humans.append(t)
    return {"proj": proj, "start": (start or "")[:16].replace("T", " "), "humans": humans,
            "errors": errors, "commands": commands, "tools": tools}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=float)
    ap.add_argument("--mark", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "rapports").mkdir(exist_ok=True)
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    if a.mark:
        state["last_run"] = time.time()
        STATE.write_text(json.dumps(state))
        print("dernier passage enregistré")
        return
    since = time.time() - a.days * 86400 if a.days else state.get("last_run", time.time() - 7 * 86400)
    recent = time.time() - 120     # ignorer la session en cours (écrite à l'instant)
    files = sorted((p for p in PROJECTS.glob("*/*.jsonl") if since < p.stat().st_mtime < recent),
                   key=lambda p: p.stat().st_mtime)
    sessions, seen = [], {}
    for s in map(session, files):          # sessions reprises / forkées = mêmes messages : garder la plus récente
        if s["humans"]:
            key = tuple(s["humans"][:4])
            if key in seen:
                sessions[seen[key]] = s
            else:
                seen[key] = len(sessions); sessions.append(s)

    cmds, tools, errs, per_proj = Counter(), Counter(), Counter(), Counter()
    for s in sessions:
        cmds.update(s["commands"]); tools.update(s["tools"]); per_proj[s["proj"]] += 1
        errs.update(re.sub(r"\d+", "N", e)[:120] for e in s["errors"])

    head = [f"# Digest — {len(sessions)} sessions depuis {time.strftime('%Y-%m-%d %H:%M', time.localtime(since))}", "",
            "## Stats",
            "- Sessions par projet : " + ", ".join(f"{p} {n}" for p, n in per_proj.most_common()),
            "- Skills / commandes lancés : " + (", ".join(f"/{c} ×{n}" for c, n in cmds.most_common(25)) or "aucun"),
            "- Outils : " + ", ".join(f"{t} {n}" for t, n in tools.most_common(15)),
            "", "## Erreurs d'outils récurrentes"]
    head += [f"- ×{n} {e}" for e, n in errs.most_common(20) if n > 1] or ["- rien de récurrent"]
    head += ["", "## Corrections (messages qui recadrent Claude)"]
    for s in sessions:
        for h in s["humans"][1:]:
            if CORRECTION.search(h[:200]):
                head.append(f"- [{s['proj']}] {h[:MSG_CHARS]}")

    body = ["", "## Sessions (1er message = la demande, puis les relances)"]
    for s in sessions:
        body.append(f"\n### {s['start']} · {s['proj']} · {len(s['humans'])} msg · {len(s['errors'])} erreurs")
        for i, h in enumerate(s["humans"][:12]):
            body.append(f"{'>' if i == 0 else '-'} {h[:MSG_CHARS * (2 if i == 0 else 1)]}")
        if len(s["humans"]) > 12:
            body.append(f"- … +{len(s['humans']) - 12} messages")

    text = "\n".join(head)[: MAX_CHARS // 2]
    text += "\n".join(body)[: MAX_CHARS - len(text)]
    (OUT / "digest.md").write_text(text, encoding="utf-8")
    print(f"{len(sessions)} sessions -> {OUT / 'digest.md'} ({len(text)} car.)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
