# ResearchOS Continuous 12-Hour / 24-Hour Monitoring & Alerts

## Watchlists Engine
ResearchOS features a background scheduler (`researchos.apps.scheduler.scheduler`) that automatically checks active watchlists on customizable cadences (1h, 6h, 12h, 24h, weekly).

## Change Detection Snapshot Differ
During each monitoring cycle, the engine diffs the current research state against the previous snapshot:
1. **Price Drops:** Triggers HIGH significance alerts when hardware/listings drop in price.
2. **Free Quota Shifts:** Alerts when provider API quotas or free tiers are modified.
3. **New Model Releases:** Alerts on newly released SWE-Bench coding models or open-source weights.
4. **Promo Expirations:** Warns before developer trials and credit packages expire.

## Alert Channels
- **Live UI Notifications:** Displayed in the Dashboard Alerts Tab.
- **Discord / Telegram Webhooks:** Configured via `DISCORD_WEBHOOK_URL` and `TELEGRAM_BOT_TOKEN` in `.env`.
- **System Audit Log:** Logged with severity ratings (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
