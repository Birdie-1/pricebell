# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1. Project overview

PriceBell (Thai name "น้องเฝ้าพอร์ต") is a Telegram bot that alerts users when asset prices hit targets: Thai and US stocks, ETFs, gold, oil and USD/THB. It is a portfolio project for job interviews, used by the author and friends, so it does not need to scale.

**Status: step 0 (project setup) is done; next is step 1, the walking skeleton.** So far there is only tooling, the settings object and its tests; no bot code yet. `PLANNING.md` is the source of truth for decisions, scope, roadmap and open questions.

### How we work: the user writes the code, Claude guides

The user writes the application code themselves, both to learn and because they must be able to explain every line in an interview. Claude's role is guide and reviewer, not implementer.

- **Don't write implementation code into the project unless asked for that specific piece.** "How do I…?", "what should X look like?" or sharing a plan is not a request to write it. Discussing or reviewing the plan is not a go-ahead to scaffold either.
- **When asked how to do something:** explain the approach and the trade-offs, say which file or layer it belongs in, and point to the relevant convention or `PLANNING.md` section. Short illustrative snippets, signatures or pseudocode are fine; a finished implementation is not. Leave the user the actual writing.
- **When stuck:** give hints in steps, from a nudge to a more specific pointer, before showing a solution. Show a full solution only if the user asks for it.
- **Reviewing the user's code** is the main job: check it against the conventions below, the layering rules and the design points in `PLANNING.md` §8. Point out the issue and why it matters, and let the user fix it. Don't edit their files unless asked.
- **Explain so it can be retold:** when a design choice comes up (outbox, hysteresis, single-flight, token bucket…), explain it the way the user could explain it to an interviewer.
- **Talk in Thai**, the user's language. Code, identifiers, commit messages and the README stay in English.
- Claude may create or edit non-application files (this file, `PLANNING.md`, skills, notes) when asked.

Key decisions:

- **Telegram first, not LINE.** LINE is a second `Messenger` adapter in v3.
- **Out of scope:** TimescaleDB, React dashboard. Do not add them.
- **MVP before v2.** Indicator alerts (52-week, SMA50/200, RSI), daily summary, Finnhub, `exchange_calendars` and baht-gold pricing are v2 (`PLANNING.md` §9).
- **Build order:** walking skeleton first, then one vertical slice at a time, following the numbered MVP steps in `PLANNING.md` §9.2 (steps 0–9). Tables are added in the slice that first needs them, not up front. When reviewing or guiding, check which step the user is on and keep work inside it.
- **Telegram library: python-telegram-bot** (chosen over aiogram because it is easier to learn). Use it only in the Telegram adapter and handlers. Don't use its JobQueue or `AIORateLimiter`: the scheduler (APScheduler) and the send queue are our own so the engine stays platform-agnostic.
- **Still open:** public vs link-only access, default % per asset class. Ask rather than pick.

Planned stack: Python 3.12, FastAPI, python-telegram-bot, SQLAlchemy 2, PostgreSQL (SQLite in-memory for tests), APScheduler, yfinance (MVP), Docker, an always-on host (Fly.io or Railway) with Neon or Supabase.

### Planned architecture

One FastAPI app with two entry points that share the price provider and Postgres:

1. **Telegram updates** → bot adapter (secret-token check, dedupe by `update_id`) → command/button handlers.
2. **Scheduler** (one APScheduler job every 60 s, `max_instances=1`) → alert engine (pure rules) → `AlertEvent` rows (outbox) → send queue (token bucket, honours Telegram `429 retry_after`).

Tables: `users`, `watchlist_items`, `alerts`, `alert_events`, `processed_updates` (columns in `PLANNING.md` §6).

## 2. Directory map

Current contents:

| Path | What it is |
|---|---|
| `PLANNING.md` | Full plan in Thai: decisions, UX, architecture, data model, assets, roadmap, risks, open questions |
| `CLAUDE.md` | This file |
| `.gitignore` | Ignores `.env*` (except `.env.example`), venvs, tool caches, local DB files |
| `.env.example` | Placeholder env vars; copy to `.env` (git-ignored) and fill in |
| `pyproject.toml` | Package metadata (hatchling, src layout), dependencies, `dev` extra (pytest, ruff), ruff and pytest config |
| `src/pricebell/settings.py` | `Settings` (pydantic-settings): reads `TELEGRAM_BOT_TOKEN` as `SecretStr` from env or `.env`, `extra="forbid"`. Not instantiated at import time; `main.py` will create it |
| `tests/unit/test_settings.py` | Settings tests; each builds `Settings(_env_file=None)` so tests never read the local `.env` |

**Planned code layout** (decided 25 Nov 2026; full tree and rationale in `PLANNING.md` §6.1). It is a target: create each folder in the slice that first needs it, not up front. Once code exists, add the real paths to the table above.

| Path | Layer | What goes there |
|---|---|---|
| `src/pricebell/main.py` | composition root | Builds the app and wires concrete classes together. The only module that knows every implementation |
| `src/pricebell/settings.py` | config | The single settings object; the only place that reads `os.environ` (exists since step 0) |
| `src/pricebell/domain/` | domain (pure) | `PriceSnapshot`, symbol alias table, alert rules. Imports nothing outside the stdlib |
| `src/pricebell/ports.py` | interfaces | `PriceProvider`, `Messenger` (`typing.Protocol`), `OutgoingMessage` |
| `src/pricebell/services/` | services | Use cases (watchlist, alert engine); owns the transaction boundary |
| `src/pricebell/messages.py` | shared | th/en strings keyed by id, disclaimer, price-timestamp line. Platform-neutral |
| `src/pricebell/providers/` | adapter | yfinance provider, TTL cache + single-flight |
| `src/pricebell/db/` | adapter | SQLAlchemy models, session |
| `src/pricebell/bot/` | adapter | Everything Telegram: `app.py`, `handlers/`, `callbacks.py`, `keyboards.py`, `messenger.py` (`TelegramMessenger`) |
| `src/pricebell/queue/` | adapter | Send queue (step 8) |
| `tests/` | tests | `fakes.py` (`FakePriceProvider`, `FakeMessenger`), `unit/`, `integration/` |

## 3. Commands

Run from the repo root. The venv uses Python 3.12 (the machine's default `python3` is 3.13 from Anaconda, so call `python3.12` explicitly).

```bash
python3.12 -m venv .venv          # once
source .venv/bin/activate         # every new shell
pip install -e ".[dev]"           # after changing pyproject.toml
cp .env.example .env              # once, then put the BotFather token in .env

pytest -v                                         # all tests
pytest tests/unit/test_settings.py::test_missing_token_raises   # one test
ruff check .                                      # lint
ruff format .                                     # format (ruff format --check . to only check)

ruff check . && ruff format --check . && pytest   # the "done" check before committing
```

Not yet: running the bot (step 1), Docker (step 3), Postgres via docker-compose (step 4), GitHub Actions CI (v3). Add them here when they exist.

The Telegram bot token from BotFather goes in `.env`, never in code.

## 4. Conventions

**Layering**

- `Messenger` and `PriceProvider` are interfaces. The alert engine must not import anything Telegram-specific; adding LINE in v3 must not require touching the engine.
- Imports point inward only: `domain` imports nothing; `services` imports only `domain`, `ports` and `messages`; `bot/`, `providers/`, `db/` and `queue/` are outer adapters; only `main.py` imports concrete adapters. In review, flag any import that breaks this.
- `Messenger` takes a platform-neutral `OutgoingMessage` (text plus buttons as action + database id), built by the service layer. Each adapter maps it to its own format; `TelegramMessenger` maps buttons to InlineKeyboard and `callback_data`. Platform formats (`callback_data`, Flex Message) never appear outside their adapter.
- The provider fetches each symbol once per cycle in a batch, behind a TTL cache with single-flight, shared by chat handlers and the scheduler.
- Alert state changes and the `AlertEvent` insert happen in one transaction. `AlertEvent` has a unique (alert, dedupe key) so re-runs or overlapping runs never double-send. Postgres uses `FOR UPDATE SKIP LOCKED`.
- Duplicate-alert suppression: armed/disarmed state, 0.5% hysteresis, 30-minute cooldown; %-change alerts fire at most once per day.
- Store times in UTC, display in Asia/Bangkok.
- Webhook secret token is compared in constant time.

**Bot messages and buttons**

- Replies are bilingual (Thai/English), chosen from the user's Telegram `language_code`. Every command has a slash form and a Thai text form (e.g. `/price NVDA` = `ราคา NVDA` = `NVDA`).
- Buttons first, typing as a fallback; any main task takes 1–3 taps. Multi-step flows edit the same message (`editMessageText`) instead of sending new ones.
- Confirm by showing the result with an "undo" button, not by asking "are you sure?". For a custom price, use `ForceReply` so the user types only a number.
- `callback_data` is formatted `cmd:id` (e.g. `ad:42`) and always references a database id, never a list position.
- Every price shows its timestamp and data delay. If the source is down, say when the data was last updated.
- Alert wording states facts ("RSI below 30"), never advice ("buy signal"). Messages carry a "not investment advice" disclaimer.
- Quiet hours (default 23:00–07:00 Bangkok) send with `disable_notification`; they do not drop or delay alerts.
- `/demo` fires a simulated alert within 10 seconds so an interviewer can see the full flow without waiting for the market.

**Writing code**

These were set before any code existed. If the scaffold does something different, update this section rather than working around it.

- *Python style:* Python 3.12 syntax (`X | None`, `list[str]`). Type hints on every function signature. `ruff check` and `ruff format` must pass. Identifiers, comments and docstrings are in English.
- *Async:* Telegram handlers, provider HTTP calls and DB access are async. Alert rules are plain synchronous functions.
- *Pure alert rules:* a rule takes (alert state, price snapshot, `now`) and returns (new state, optional event). No DB, network, logging or clock reads inside. The engine around it does the I/O.
- *Time:* never call `datetime.now()` or `utcnow()` inside logic. Take `now` as a parameter, or inject a clock in services. All datetimes are timezone-aware UTC; convert to Asia/Bangkok only when formatting a message.
- *Prices:* store prices and thresholds as `Numeric` columns and handle them as `Decimal` in the domain. Convert provider floats to `Decimal` at the provider boundary. Round only when formatting.
- *Symbols:* normalise user input to the Yahoo symbol (e.g. `PTT` → `PTT.BK`, `ทอง` → `GC=F`) once, at the input boundary, through a single alias table. Everything past that boundary sees only Yahoo symbols.
- *User-facing text:* no literal user text in handlers. All strings live in one messages module keyed by id, with `th` and `en` versions; the disclaimer and price-timestamp line are added there, not by each handler.
- *Callback data:* encode and decode `callback_data` in one module. Encoding asserts the 64-byte limit. Handlers never split the string themselves.
- *Database:* SQLAlchemy 2.0 style (`Mapped[...]`, `mapped_column`, `select()`), no legacy `Query` API. A session is opened per update or per scheduler cycle, and the transaction boundary lives in the service layer, not in handlers or rules.
- *Config:* read settings (bot token, webhook secret, DB URL, poll interval) from environment variables in one settings object. Nothing else reads `os.environ`.
- *Logging:* use `logging`, never `print`. Log the alert lifecycle (fired, queued, sent, retried) with the alert id and dedupe key so a missed alert can be traced.
- *Tests:* no network in tests. Use a fake `PriceProvider` (scripted price series) and a fake `Messenger` (records what was sent). Dedupe and hysteresis are tested with backtests over price series that oscillate around the threshold. Each design point in `PLANNING.md` §8 should have a test that proves it.

**Git**

The folder is a git repository; the default branch is `main`. The history is part of the portfolio, so interviewers will read it.

- *When:* commit, push or open a PR only when the user asks.
- *Commit messages:* Conventional Commits in English, imperative mood, subject ≤ 72 characters: `type(scope): summary`.
  - Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`.
  - Scopes follow the architecture: `bot`, `handlers`, `provider`, `alerts`, `queue`, `db`, `config`, `deploy`. Leave the scope out for changes that cut across.
  - Use the body to explain why, especially for design points from `PLANNING.md` §8 (e.g. why hysteresis is 0.5%).
- *Commit size:* one logical change per commit. Tests go in the same commit as the code they cover. Formatting-only changes go in their own commit.
- *Branches:* `feat/<short-name>`, `fix/<short-name>`, `docs/<short-name>` off `main`. Merge into `main` with a squash merge so each feature is one commit on `main`. Once GitHub Actions CI exists (v3), `main` only takes PRs with green CI.
- *Tags:* tag the commit that was deployed at the end of each roadmap phase: `mvp`, `v2`, `v3`.
- *Don't commit:* `.env` (commit a `.env.example` with placeholder values instead), local DB files, or anything restored from the old LINE scaffold that isn't used.

**Language of written material:** README and diagrams are in English (interviewers may be outside Thailand). `PLANNING.md` is in Thai.

## 5. Quirks

- **yfinance is unofficial.** It can return 429 or be blocked from cloud IPs. Use the cache, batch requests, never poll closed markets, and surface data age rather than failing silently.
- **Thai stocks (`.BK`) are ~15 minutes delayed** on Yahoo. US stocks are near real-time.
- **`GC=F` is USD per troy ounce**, not the Thai baht-weight 96.5% gold price. A baht-gold price (v2) must be labelled as an estimate.
- **Gold and oil futures trade almost 24 hours**; stock markets don't. US market hours shift with DST, so Bangkok-time opening hours change twice a year.
- **Free hosting tiers that sleep** (e.g. Render free) stop the scheduler and alerts stop firing. The app needs an always-on instance.
- **Telegram limits:** `callback_data` ≤ 64 bytes; roughly 1 message/second per chat and 30/second overall. Alerts fired together during a sharp market move must go through the send queue. These figures are approximate; check the official docs before relying on them.
- **SQLite tests can't cover Postgres locking.** `FOR UPDATE SKIP LOCKED` is ignored on SQLite, so the in-memory test DB cannot prove that overlapping scheduler runs never double-send. Keep the unique (alert, dedupe key) constraint as the real guarantee, and test concurrency against Postgres when it matters.
- **Old buttons stay clickable.** A user can press a button on a message for an alert that was deleted; reply "this item was deleted" instead of erroring.
- **Older LINE-era material.** Earlier notes and a scaffold targeted LINE. That MVP was moved to `~/.Trash/pricebell-mvp-20261125-101237`; its provider, cache, alert rules (hysteresis/cooldown/outbox) and tests can be reused for Telegram if the user asks to restore it.
