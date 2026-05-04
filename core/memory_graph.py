import json
import os
from datetime import datetime
import ollama

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR     = os.path.dirname(BASE_DIR)
MEMORIES_PATH = os.path.join(ROOT_DIR, "memory", "persona", "memories.json")

MODEL = "llama3.1:8b"

# ── Load existing memories ────────────────────────────────────────────────────
def load_memories() -> list:
    if not os.path.exists(MEMORIES_PATH):
        return []
    with open(MEMORIES_PATH, "r") as f:
        return json.load(f)


# ── Save memories ─────────────────────────────────────────────────────────────
def save_memories(memories: list):
    os.makedirs(os.path.dirname(MEMORIES_PATH), exist_ok=True)
    with open(MEMORIES_PATH, "w") as f:
        json.dump(memories, f, indent=2)


# ── Extract new memories from a session ──────────────────────────────────────
def extract_memories(messages: list) -> list:
    """
    Send the session transcript to Llama and ask it to extract
    important facts worth remembering long-term.
    Returns a list of new memory strings.
    """
    if not messages:
        return []

    # Build transcript
    transcript = ""
    for m in messages:
        role = "User" if m["role"] == "user" else "AlterEgo"
        transcript += f"{role}: {m['content']}\n"

    extraction_prompt = """You are a memory extraction system for a personal AI agent.

Read the conversation below and extract ONLY facts that are worth remembering long-term about the user.

Rules:
- Only extract concrete, specific facts (preferences, decisions, goals, habits, context)
- Skip small talk, greetings, generic exchanges
- Skip anything already obvious or generic
- Each memory should be one clear sentence
- Return ONLY a JSON array of strings, no explanation, no markdown, nothing else
- If nothing is worth remembering, return an empty array: []

Examples of good memories:
- "Prefers to keep emails short and direct"
- "Working on landing first 3 Makops retainer clients"
- "Dislikes over-explained answers"
- "Wants AlterEgo to handle calendar on Monday mornings"

Conversation:
""" + transcript + """

Return only a JSON array:"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": extraction_prompt}]
    )

    raw = response["message"]["content"].strip()

    # Clean up in case model adds markdown fences
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        extracted = json.loads(raw)
        if isinstance(extracted, list):
            return [str(m) for m in extracted]
    except json.JSONDecodeError:
        pass

    return []


# ── Merge new memories with existing, avoid duplicates ───────────────────────
def update_memories(messages: list) -> int:
    """
    Extract memories from session, merge with existing ones.
    Returns count of new memories added.
    """
    print("\n[AlterEgo is processing memories...]")

    existing = load_memories()
    existing_lower = [m.lower() for m in existing]

    new_memories = extract_memories(messages)

    added = 0
    for mem in new_memories:
        # Simple duplicate check
        if mem.lower() not in existing_lower:
            existing.append(mem)
            existing_lower.append(mem.lower())
            added += 1

    if added > 0:
        save_memories(existing)
        print(f"[{added} new memory/memories saved]\n")
    else:
        print("[No new memories extracted]\n")

    return added


# ── Format memories for system prompt injection ───────────────────────────────
def format_memories_for_prompt() -> str:
    memories = load_memories()
    if not memories:
        return ""
    lines = "\n".join(f"- {m}" for m in memories)
    return f"\n\n== LONG-TERM MEMORIES (facts learned about Your Majesty) ==\n{lines}"


# ── View all memories ─────────────────────────────────────────────────────────
def list_memories() -> list:
    return load_memories()


# ── Delete a specific memory by index ────────────────────────────────────────
def delete_memory(index: int) -> bool:
    memories = load_memories()
    if 0 <= index < len(memories):
        removed = memories.pop(index)
        save_memories(memories)
        print(f"[Memory deleted: '{removed}']")
        return True
    return False


# ── Add a memory manually ─────────────────────────────────────────────────────
def add_memory_manual(text: str):
    memories = load_memories()
    memories.append(text)
    save_memories(memories)
    print(f"[Memory added: '{text}']")
