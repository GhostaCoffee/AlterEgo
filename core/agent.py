import ollama
from datetime import datetime
from memory_manager import load_system_prompt, save_session, search_history, memory_stats
from memory_graph import update_memories, list_memories, delete_memory, add_memory_manual

MODEL = "llama3.1:8b"

COMMANDS = {
    "exit":          "quit, save session + extract memories",
    "save":          "save session without quitting",
    "search":        "search memory — usage: :search <keyword>",
    "stats":         "show memory stats",
    "memories":      "list all long-term memories",
    "remember":      "manually add a memory — usage: :remember <fact>",
    "forget":        "delete a memory by number — usage: :forget <number>",
    "clear":         "clear screen",
    "help":          "show this list",
}

def print_help():
    print("\n[Commands]")
    for cmd, desc in COMMANDS.items():
        print(f"  :{cmd:<12} {desc}")
    print()

def print_banner():
    print("\n" + "=" * 50)
    print("  AlterEgo — Online")
    print(f"  {datetime.now().strftime('%A, %B %d %Y — %H:%M')}")
    print("=" * 50)
    print("  Type :help for commands\n")

def shutdown(messages):
    save_session(messages)
    if messages:
        update_memories(messages)  # ← extract and save memories from this session
    print("AlterEgo — Offline.\n")

def main():
    print_banner()
    system_prompt = load_system_prompt()
    messages = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            shutdown(messages)
            break

        if not user_input:
            continue

        if user_input.startswith(":"):
            cmd = user_input[1:].strip().lower()

            if cmd == "exit":
                shutdown(messages)
                break

            elif cmd == "save":
                save_session(messages)

            elif cmd.startswith("search "):
                keyword = cmd[7:].strip()
                results = search_history(keyword)
                if results:
                    print(f"\n[Found {len(results)} result(s) for '{keyword}']")
                    for r in results[:5]:
                        print(f"  [{r['session']}] {r['role']}: {r['content'][:150]}")
                    print()
                else:
                    print(f"\n[No results for '{keyword}']\n")

            elif cmd == "stats":
                s = memory_stats()
                print(f"\n[Memory Stats]")
                print(f"  Sessions stored : {s['total_sessions']}")
                print(f"  Total size      : {s['memory_size_kb']} KB")
                print(f"  Oldest session  : {s['oldest_session']}")
                print(f"  Latest session  : {s['latest_session']}\n")

            elif cmd == "memories":
                mems = list_memories()
                if mems:
                    print(f"\n[Long-term Memories — {len(mems)} total]")
                    for i, m in enumerate(mems):
                        print(f"  {i}. {m}")
                    print()
                else:
                    print("\n[No long-term memories yet. Just talk — they'll build up.]\n")

            elif cmd.startswith("remember "):
                fact = cmd[9:].strip()
                add_memory_manual(fact)

            elif cmd.startswith("forget "):
                try:
                    index = int(cmd[7:].strip())
                    delete_memory(index)
                except ValueError:
                    print("[Usage: :forget <number> — use :memories to see numbers]\n")

            elif cmd == "clear":
                import os; os.system("cls")
                print_banner()

            elif cmd == "help":
                print_help()

            else:
                print(f"[Unknown command '{cmd}'. Type :help]\n")

            continue

        # ── Chat ──
        messages.append({"role": "user", "content": user_input})

        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "system", "content": system_prompt}] + messages
        )

        reply = response["message"]["content"]
        messages.append({"role": "assistant", "content": reply})
        print(f"\nAlterEgo: {reply}\n")

if __name__ == "__main__":
    main()
