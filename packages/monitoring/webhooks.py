"""
ResearchOS Alert Webhook Dispatcher
Supports Discord Webhooks and Telegram Bot Notifications
"""
import os
import asyncio
import httpx
from typing import Optional, Dict, Any
from researchos.packages.core.config import settings
from researchos.packages.core.logging import logger
from researchos.packages.core.schemas import Alert


class AlertWebhookDispatcher:
    def __init__(self):
        self.discord_webhook_url = getattr(settings, "DISCORD_WEBHOOK_URL", None) or os.environ.get("DISCORD_WEBHOOK_URL")
        self.telegram_bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", None) or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = getattr(settings, "TELEGRAM_CHAT_ID", None) or os.environ.get("TELEGRAM_CHAT_ID")

    async def send_discord_alert(self, alert: Alert) -> bool:
        if not self.discord_webhook_url:
            return False

        color_map = {
            "critical": 0xEF4444,  # Red
            "high": 0xF59E0B,      # Amber
            "medium": 0x3B82F6,    # Blue
            "low": 0x10B981,       # Green
        }
        color = color_map.get(alert.significance.lower(), 0x3B82F6)

        payload = {
            "username": "ResearchOS Sentinel",
            "avatar_url": "https://raw.githubusercontent.com/woodsai69rme/researchos/master/apps/web/public/favicon.ico",
            "embeds": [
                {
                    "title": f"🚨 ResearchOS Alert: {alert.title}",
                    "description": alert.message,
                    "color": color,
                    "fields": [
                        {"name": "Significance", "value": alert.significance.upper(), "inline": True},
                        {"name": "Watchlist ID", "value": alert.watchlist_id, "inline": True},
                        {"name": "Timestamp", "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"), "inline": True},
                    ],
                    "footer": {"text": "ResearchOS Continuous Intelligence • Australia/Brisbane"},
                }
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(self.discord_webhook_url, json=payload)
                if res.status_code in (200, 204):
                    logger.info(f"Dispatched Discord webhook alert: {alert.title}")
                    return True
                else:
                    logger.warning(f"Discord webhook failed with status {res.status_code}")
        except Exception as e:
            logger.warning(f"Failed sending Discord webhook: {e}")
        return False

    async def send_telegram_alert(self, alert: Alert) -> bool:
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return False

        msg = (
            f"🚨 *ResearchOS Alert: {alert.title}*\n\n"
            f"{alert.message}\n\n"
            f"• *Significance:* `{alert.significance.upper()}`\n"
            f"• *Time:* `{alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}`"
        )

        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": msg,
            "parse_mode": "Markdown",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    logger.info(f"Dispatched Telegram alert: {alert.title}")
                    return True
                else:
                    logger.warning(f"Telegram alert failed with status {res.status_code}")
        except Exception as e:
            logger.warning(f"Failed sending Telegram alert: {e}")
        return False

    async def dispatch(self, alert: Alert) -> Dict[str, bool]:
        discord_res, telegram_res = await asyncio.gather(
            self.send_discord_alert(alert),
            self.send_telegram_alert(alert),
            return_exceptions=True
        )
        return {
            "discord": bool(discord_res is True),
            "telegram": bool(telegram_res is True),
        }


alert_dispatcher = AlertWebhookDispatcher()
