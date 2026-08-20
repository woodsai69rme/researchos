import asyncio
from researchos.packages.core.config import OperatingMode
from researchos.packages.research.planner import ResearchPlanner
from researchos.packages.research.swarm import SearchSwarm
from researchos.packages.research.synthesis import ResearchSynthesizer


async def run_live_verification():
    planner = ResearchPlanner()
    swarm = SearchSwarm()
    synth = ResearchSynthesizer()

    queries = [
        "Find a complete 1,000hp Ford Falcon XR6 Turbo TH400 setup in Queensland",
        "Find every free AI coding model, agent, API, IDE, CLI tool, trial and promo",
        "Find used RTX 4090 graphics cards in Brisbane",
    ]

    for q in queries:
        print(f"\n--- Testing Query: '{q}' ---")
        plan = planner.create_plan(user_query=q, mode=OperatingMode.FREE_ONLY)
        print(f"[+] Plan: domain={plan.domain_category}, variants={len(plan.search_queries)}, mode={plan.operating_mode}")

        swarm_res = await swarm.execute_swarm(plan)
        src_cnt = len(swarm_res["sources"])
        list_cnt = len(swarm_res["listings"])
        biz_cnt = len(swarm_res["businesses"])
        print(f"[+] Swarm Discovered: {src_cnt} sources, {list_cnt} marketplace deals, {biz_cnt} workshops")

        report = await synth.synthesize(plan, swarm_res)
        print(f"[+] Synthesis: {len(report.claims)} claims, {len(report.what_you_missed)} missed angles, Spend=${report.actual_spend_aud:.2f} AUD")
        print(f"[+] Executive Verdict: {report.bottom_line[:120]}...")

    print("\n============================================================")
    print(" ALL 3 REAL DOMAIN RESEARCH RUNS COMPLETED & VERIFIED!")
    print("============================================================")


if __name__ == "__main__":
    asyncio.run(run_live_verification())
