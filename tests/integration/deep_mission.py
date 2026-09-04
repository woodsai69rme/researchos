import asyncio
from pathlib import Path
from researchos.packages.core.config import OperatingMode, ResearchDepth
from researchos.packages.research.planner import ResearchPlanner
from researchos.packages.research.swarm import SearchSwarm
from researchos.packages.research.synthesis import ResearchSynthesizer
from researchos.packages.research.exporter import report_exporter


async def run_mission():
    planner = ResearchPlanner()
    swarm = SearchSwarm()
    synth = ResearchSynthesizer()

    mission_query = (
        "Complete 2026 playbook: AI video automated music video pipelines, "
        "RTX GPU arbitrage deals in Brisbane, and 1,000hp Barra TH400 conversion kits"
    )
    print(f"[*] Launching Deep Research Mission: {mission_query}")

    plan = planner.create_plan(user_query=mission_query, mode=OperatingMode.FREE_ONLY, depth=ResearchDepth.DEEP)
    print(f"[✓] Plan: Domain={plan.domain_category} | Variants={len(plan.search_queries)}")

    results = await swarm.execute_swarm(plan)
    source_cnt = len(results.get("sources", []))
    listing_cnt = len(results.get("listings", []))
    biz_cnt = len(results.get("businesses", []))
    print(f"[✓] Swarm Harvest: {source_cnt} sources, {listing_cnt} listings, {biz_cnt} workshops")

    report = await synth.synthesize(plan, results)
    print(f"[✓] Synthesis Complete: Actual Spend=${report.actual_spend_aud:.2f} AUD | Confidence={int(report.confidence_score*100)}%")

    out_file = report_exporter.export_to_markdown(report, filename="EMPIRE_CROSS_DOMAIN_INTEL_2026.md")
    print(f"[✓] Intelligence Report Exported to: {out_file}")


if __name__ == "__main__":
    asyncio.run(run_mission())
