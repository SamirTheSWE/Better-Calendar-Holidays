<div align="center">

# Better Calendar Holidays

A self-hosted holiday ICS feed service — pick a country and region, get a subscribable calendar URL.

**[Try the hosted version](#)** — no setup required.

[Why](#why) • [Features](#features) • [Tech Stack](#tech-stack) • [Installation](#installation) • [Usage](#usage) • [Limitations](#limitations) • [Roadmap](#roadmap)

</div>

---

## Why

Most calendar apps (Outlook, Google Calendar, Apple Calendar) ship built-in country holiday feeds — but those events are **read-only**. You can't mark yourself as Out of Office on a holiday without creating a duplicate event alongside it.

Built-in feeds also have **incomplete regional coverage**. If you also add a regional sub-calendar to fill the gap, you often end up with **duplicate events** — the same holiday included from multiple region sources, cluttering your calendar.

Better Calendar Holidays solves all three problems: it gives you a **self-controlled** ICS URL (your calendar app treats it like any other subscribed feed), it aggregates data from two upstream APIs for broader coverage, and it **deduplicates** holidays across sources and regions before generating the feed.

---

## Features

- Subscribable `.ics` URL compatible with any calendar app (Outlook, Google Calendar, Apple Calendar, etc.)
- Aggregates **Nager.Date** (free, ~100 countries) and **Calendarific** (paid, broader coverage) with automatic fallback
- Deduplicates holidays across sources and regions
- Country + optional region selection via a clean web UI
- Redis caching and rate limiting
- Fully self-hosted — your data stays on your infrastructure

---

## Tech Stack

| Layer | Stack |
|---|---|
| Backend | FastAPI + Redis, Python 3.12 |
| Frontend | Angular 20 (standalone), Tailwind CSS 4, TypeScript 5.9 |
| Data Sources | Nager.Date API, Calendarific API |

---

## Installation

> [!IMPORTANT]
> **Prerequisites:** Python 3.12+, Node.js with pnpm, and a running Redis instance.

**Backend**

```bash
git clone https://github.com/SamirTheSWE/Better-Calendar-Holidays.git
cd backend
pip install -r requirements-dev.txt
cp .env.example .env
```

Edit `.env` and set:
- `CALENDARIFIC_API_KEY` — from [calendarific.com](https://calendarific.com)
- `REDIS_URL` — e.g. `redis://localhost:6379`

**Frontend**

```bash
cd frontend
pnpm install
```

---

## Usage

> [!TIP]
> Run both servers simultaneously. The frontend dev server proxies `/api` to the backend.

```bash
# Backend (from backend/)
PYTHONPATH=src uvicorn app:app --reload

# Frontend (from frontend/)
pnpm start
```

Open `http://localhost:4200`, select a country and optional region, then copy the generated ICS URL into your calendar app's "Subscribe to calendar" feature.

---

## Limitations

- **Calendarific free tier:** 500 requests/month. The app tracks quota in Redis and returns an error if exceeded.
- **Regional coverage:** depends on upstream APIs — not all regions are available for all countries.
- **Subscribed feed events are read-only:** All major calendar apps (Outlook, Google Calendar, Apple Calendar) treat events from subscribed ICS feeds as read-only — you cannot edit individual event properties (e.g. "Show As", reminders). If you need editable events, import the `.ics` file instead of subscribing, though imported events will not auto-update.
