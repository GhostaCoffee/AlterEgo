import json
import os
from datetime import datetime

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR    = os.path.dirname(BASE_DIR)
HISTORY_DIR = os.path.join(ROOT_DIR, "memory", "history")
PERSONA_DIR = os.path.join(ROOT_DIR, "memory", "persona")
GOALS_PATH  = os.path.join(ROOT_DIR, "memory", "goals", "goals.md")
CONTEXT_PATH = os.path.join(ROOT_DIR, "memory", "context", "last_session.json")

MAX_HISTORY_SESSIONS  = 20
MAX_MESSAGES_IN_CONTEXT = 10


# ── Save current session ─────────────────────────────────────────────────────
def save_session(messages: list):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    path = os.path.join(HISTORY_DIR, f"session_{timestamp}.json")

    data = {
        "timestamp": timestamp,
        "message_count": len(messages),
        "messages": messages
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    os.makedirs(os.path.dirname(CONTEXT_PATH), exist_ok=True)
    with open(CONTEXT_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n[Session saved → {path}]")
    _prune_old_sessions()


# ── Load recent context ───────────────────────────────────────────────────────
def load_recent_context() -> list:
    if not os.path.exists(CONTEXT_PATH):
        return []
    try:
        with open(CONTEXT_PATH, "r") as f:
            data = json.load(f)
        return data.get("messages", [])[-MAX_MESSAGES_IN_CONTEXT:]
    except Exception:
        return []


# ── Load full system prompt with all memory layers injected ──────────────────
def load_system_prompt() -> str:
    from memory_graph import format_memories_for_prompt

    prompt_path = os.path.join(PERSONA_DIR, "system_prompt.txt")
    with open(prompt_path, "r") as f:
        prompt = f.read()

    # Layer 1: Current goals
    if os.path.exists(GOALS_PATH):
        with open(GOALS_PATH, "r") as f:
            goals = f.read()
        prompt += f"\n\n== CURRENT GOALS ==\n{goals}"

    # Layer 2: Long-term memories (learned facts about Your Majesty)
    prompt += format_memories_for_prompt()

    # Layer 3: Recent session context
    recent = load_recent_context()
    if recent:
        summary_lines = []
        for m in recent:
            role = "You" if m["role"] == "user" else "AlterEgo"
            summary_lines.append(f"{role}: {m['content'][:200]}")
        prompt += f"\n\n== RECENT CONTEXT (last session) ==\n" + "\n".join(summary_lines)

    return prompt


# ── Search history ────────────────────────────────────────────────────────────
def search_history(keyword: str) -> list:
    results = []
    if not os.path.exists(HISTORY_DIR):
        return results
    for filename in sorted(os.listdir(HISTORY_DIR), reverse=True):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(HISTORY_DIR, filename)
        with open(path, "r") as f:
            data = json.load(f)
        for msg in data.get("messages", []):
            if keyword.lower() in msg.get("content", "").lower():
                results.append({
                    "session": filename,
                    "role": msg["role"],
                    "content": msg["content"]
                })
    return results


# ── Prune old sessions ────────────────────────────────────────────────────────
def _prune_old_sessions():
    if not os.path.exists(HISTORY_DIR):
        return
    sessions = sorted([f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")])
    while len(sessions) > MAX_HISTORY_SESSIONS:
        oldest = os.path.join(HISTORY_DIR, sessions.pop(0))
        os.remove(oldest)
        print(f"[Memory pruned → removed {oldest}]")


# ── Memory stats ──────────────────────────────────────────────────────────────
def memory_stats() -> dict:
    sessions = []
    if os.path.exists(HISTORY_DIR):
        sessions = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]

    total_size = 0
    for root, dirs, files in os.walk(os.path.join(ROOT_DIR, "memory")):
        for file in files:
            total_size += os.path.getsize(os.path.join(root, file))

    return {
        "total_sessions": len(sessions),
        "memory_size_kb": round(total_size / 1024, 2),
        "oldest_session": sessions[0] if sessions else "none",
        "latest_session": sessions[-1] if sessions else "none"
    }
