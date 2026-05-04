# AlterEgo — Agent README

## What is this?
AlterEgo is your personal AI agent. It knows who you are, manages your time, tracks your tasks, handles your calendar, and keeps you moving toward your goals.

## Folder Structure

```
AlterEgo/
├── core/                  # Main agent scripts (entry point goes here)
├── memory/
│   ├── persona/           # Your identity and preferences
│   ├── context/           # Active session memory
│   ├── goals/             # Your goals (edit goals.md)
│   └── history/           # Past interactions and decisions
├── calendar/
│   ├── reminders/         # Upcoming reminders
│   └── schedules/         # Synced schedule data
├── tasks/
│   ├── pending/           # Not started
│   ├── in_progress/       # Active
│   └── completed/         # Done
├── system/
│   ├── machine_control/   # Scripts for system-level actions
│   ├── logs/              # Runtime logs
│   └── configs/           # config.json and env vars
├── updates/
│   ├── notifications/     # Alerts and reminders output
│   └── reports/           # Status summaries
└── time_management/
    ├── daily/             # Daily plans
    ├── weekly/            # Weekly reviews
    └── goals/             # Time-blocked goal tracking
```

## Getting Started
1. Edit `memory/persona/persona.json` with your details
2. Update `memory/goals/goals.md` with your current goals
3. Configure `system/configs/config.json`
4. Build your agent logic in `core/`

---
