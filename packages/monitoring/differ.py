"""
ResearchOS Snapshot Differ & Change Detection Engine
"""
from typing import Any, Dict, List, Optional
from researchos.packages.core.schemas import Alert, Watchlist


class SnapshotDiffer:
    def detect_changes(
        self,
        watchlist: Watchlist,
        previous_snapshot: Dict[str, Any],
        current_snapshot: Dict[str, Any],
    ) -> List[Alert]:
        alerts: List[Alert] = []

        if not previous_snapshot:
            return alerts

        # 1. Detect price changes
        old_prices = previous_snapshot.get("prices", {})
        curr_prices = current_snapshot.get("prices", {})
        for item, curr_p in curr_prices.items():
            if item in old_prices:
                old_p = old_prices[item]
                if curr_p < old_p:
                    drop = old_p - curr_p
                    alerts.append(
                        Alert(
                            watchlist_id=watchlist.watchlist_id,
                            title=f"Price Drop Detected: {item}",
                            message=f"Price dropped by ${drop:,.2f} AUD from ${old_p:,.2f} to ${curr_p:,.2f}.",
                            category=watchlist.category,
                            significance="HIGH",
                            old_value=f"${old_p:,.2f}",
                            new_value=f"${curr_p:,.2f}",
                        )
                    )

        # 2. Detect free tier / quota changes
        old_quotas = previous_snapshot.get("quotas", {})
        curr_quotas = current_snapshot.get("quotas", {})
        for prov, curr_q in curr_quotas.items():
            if prov in old_quotas:
                old_q = old_quotas[prov]
                if curr_q != old_q:
                    alerts.append(
                        Alert(
                            watchlist_id=watchlist.watchlist_id,
                            title=f"Free Quota Shift: {prov}",
                            message=f"Free quota limit adjusted from '{old_q}' to '{curr_q}'.",
                            category="ai_models",
                            significance="MEDIUM",
                            old_value=str(old_q),
                            new_value=str(curr_q),
                        )
                    )

        # 3. Detect new listings or models
        old_items = set(previous_snapshot.get("items", []))
        curr_items = set(current_snapshot.get("items", []))
        new_items = curr_items - old_items
        for n in new_items:
            alerts.append(
                Alert(
                    watchlist_id=watchlist.watchlist_id,
                    title=f"New Release / Listing: {n}",
                    message=f"Discovered new entry in {watchlist.category}: {n}",
                    category=watchlist.category,
                    significance="MEDIUM",
                    new_value=n,
                )
            )

        return alerts
