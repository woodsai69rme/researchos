"""
ResearchOS Alert Webhook Test Utility
Dispatches a test alert across configured Discord and Telegram webhooks
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Setup paths
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir.parent))
os.environ["PYTHONPATH"] = str(root_dir.parent)

from researchos.packages.core.schemas import Alert
from researchos.packages.monitoring.webhooks import alert_dispatcher


async def test_webhook_delivery():
    print("============================================================")
    print(" ResearchOS Alert Webhook Test Dispatcher")
    print("============================================================")
    
    discord_configured = bool(alert_dispatcher.discord_webhook_url)
    telegram_configured = bool(alert_dispatcher.telegram_bot_token and alert_dispatcher.telegram_chat_id)
    
    print(f"[*] Discord Webhook Configured:  {discord_configured}")
    print(f"[*] Telegram Webhook Configured: {telegram_configured}")
    
    if not discord_configured and not telegram_configured:
        print("\n[!] Neither Discord nor Telegram credentials found in .env or environment.")
        print("    To configure, add to C:\\Users\\karma\\researchos\\.env:")
        print("      DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...")
        print("      TELEGRAM_BOT_TOKEN=123456789:ABCdef...")
        print("      TELEGRAM_CHAT_ID=987654321")
        return

    test_alert = Alert(
        watchlist_id="test-sentinel-01",
        title="Hardware Deal Found: RTX 4090 (Deal Score 94/100)",
        message="Found ASUS TUF RTX 4090 24GB in Brisbane for $1,650 AUD with 24-month store warranty. Median market price is $2,400 AUD (31% discount).",
        significance="high",
        payload={
            "price_aud": 1650.0,
            "median_aud": 2400.0,
            "deal_score": 94,
            "location": "Brisbane, QLD",
            "source": "CeX Australia",
        }
    )

    print(f"\n[*] Dispatching simulated high-alpha alert...")
    results = await alert_dispatcher.dispatch(test_alert)
    print(f"[✓] Discord Delivery:  {'SUCCESS' if results.get('discord') else 'SKIPPED / FAILED'}")
    print(f"[✓] Telegram Delivery: {'SUCCESS' if results.get('telegram') else 'SKIPPED / FAILED'}")
    print("============================================================\n")


if __name__ == "__main__":
    asyncio.run(test_webhook_delivery())
