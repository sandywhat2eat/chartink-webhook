# ChartInk Webhook Server

Flask app (`webhook_server.py`) that relays third-party webhooks to Discord channels. Discord webhook URLs are looked up from the `controls` table by strategy name (`get_webhook_for_strategy`).

## Endpoints

- `POST /webhook` — ChartInk alerts (stocks + trigger_prices)
- `POST /webhook/tradingview` — TradingView alerts, routed per agent/strategy
- `POST /webhook/notion` — Notion automation -> Discord (Citadel Roadmap)
- `GET /webhook/notion/test` — fires a sample Citadel message to verify Discord wiring

## Notion -> Discord Bridge

**Purpose:** Notion's native automation payload is not Discord-compatible. This bridge translates a Roadmap page-change event into a formatted Discord message and posts it to the `BUILDER_INFRA` channel.

**Flow:**
1. Notion automation fires on a Citadel Roadmap page change and POSTs JSON to `/webhook/notion`.
2. Handler accepts payload at top level OR wrapped in `data` / `page`, then reads `properties`.
3. `_extract_notion_property` safely pulls these typed fields:
   - `Item` (title)
   - `Plan Status` (select) — drives emoji + action hint via `PLAN_STATUS_EMOJI` / `PLAN_STATUS_HINT`
   - `Priority` (select)
   - `Meeting Required` (select)
   - `Builders Involved` (multi_select)
   - `User Suggested Builders` (multi_select)
4. `_build_notion_discord_message` composes a markdown message: status header, item, priority, meeting flag, builders, page URL, and a status-specific hint pointing the agent at `citadel-product-management.md`.
5. Posts `{content, username: "Citadel"}` to the `BUILDER_INFRA` Discord webhook URL pulled from `controls`.
6. Returns JSON with `discord_status` and a `summary` of extracted fields.

**Failure modes** (logged + returned):
- Invalid JSON -> 400
- Missing `properties` -> 200 with `ignored` (treated as no-op so Notion doesn't retry-storm)
- `BUILDER_INFRA` webhook not configured in `controls` -> 500
- Discord non-2xx -> 502 with response body snippet

**Testing:** `curl https://<host>/webhook/notion/test` sends a sample `Needs Re-Plan` / P1 payload through the real Discord path.

## Environment

Always activate the venv before running scripts: `source /root/venv/bin/activate`.
