#!/usr/bin/env python
"""
ResearchOS Interactive Terminal Command Center
CLI interface for Universal Search, Deep Research, Deal Hunter & System Diagnostics
"""
import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add project root and parent to sys.path
root_dir = Path(__file__).resolve().parent
parent_dir = root_dir.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(parent_dir))
os.environ["PYTHONPATH"] = str(parent_dir)

from researchos.packages.core.config import settings, OperatingMode, ResearchDepth
from researchos.packages.core.logging import logger
from researchos.packages.security.policy import policy_enforcer
from researchos.packages.research.planner import ResearchPlanner
from researchos.packages.research.swarm import SearchSwarm
from researchos.packages.research.synthesis import ResearchSynthesizer
from researchos.packages.models.catalog import model_catalog
from researchos.packages.pricing.video_costs import VideoCostEngine
from researchos.packages.promotions.hunter import PromotionHunter
from researchos.packages.business.automotive import automotive_engine
from researchos.packages.monitoring.watchlists import monitoring_engine


class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def print_banner():
    print(rf"""{Colors.CYAN}{Colors.BOLD}
  ____                               _      ___  ____  
 |  _ \ ___  ___  ___  __ _ _ __ ___| |__  / _ \/ ___| 
 | |_) / _ \/ __|/ _ \/ _` | '__/ __| '_ \| | | \___ \ 
 |  _ <  __/\__ \  __/ (_| | | | (__| | | | |_| |___) |
 |_| \_\___||___/\___|\__,_|_|  \___|_| |_|\___/|____/ 
{Colors.RESET}  {Colors.GREEN}Universal Deep Research • Deal Hunter • Barra 1000hp • Free-First $0.00 Spend Lock{Colors.RESET}
  {Colors.YELLOW}Default Region: Brisbane, Queensland, Australia (AUD){Colors.RESET}
  {"=" * 76}
""")


async def execute_query(query: str, mode: OperatingMode = OperatingMode.FREE_ONLY, depth: ResearchDepth = ResearchDepth.NORMAL):
    print(f"\n{Colors.CYAN}[*] Initializing Research Swarm for:{Colors.RESET} {Colors.BOLD}{query}{Colors.RESET}")
    print(f"{Colors.YELLOW}[*] Operating Mode: {mode.value} (Spend Cap: $0.00 AUD){Colors.RESET}")

    planner = ResearchPlanner()
    swarm = SearchSwarm()
    synth = ResearchSynthesizer()

    # Step 1: Planning
    plan = planner.create_plan(user_query=query, mode=mode, depth=depth)
    print(f"{Colors.GREEN}[✓] Plan Generated:{Colors.RESET} Domain={plan.domain_category}, Search Queries={len(plan.search_queries)}")
    for q in plan.search_queries:
        print(f"    • {q}")

    # Step 2: Swarm Execution
    print(f"\n{Colors.CYAN}[*] Launching Parallel Search Swarm across Web, Code, Social & AU Marketplaces...{Colors.RESET}")
    results = await swarm.execute_swarm(plan)
    print(f"{Colors.GREEN}[✓] Swarm Harvest Complete:{Colors.RESET}")
    print(f"    • Sources Found:      {len(results.get('sources', []))}")
    print(f"    • Marketplace Deals:  {len(results.get('listings', []))}")
    print(f"    • Local Workshops:    {len(results.get('businesses', []))}")

    # Step 3: Synthesis
    print(f"\n{Colors.CYAN}[*] Extracting Claims, Evaluating Credibility & Synthesizing Report...{Colors.RESET}")
    report = await synth.synthesize(plan, results)

    # Print Executive Summary
    print(f"\n{Colors.GREEN}{Colors.BOLD}{'=' * 76}")
    print(f" RESEARCHOS EXECUTIVE SUMMARY")
    print(f"{'=' * 76}{Colors.RESET}")
    print(f"{Colors.BOLD}{report.executive_summary}{Colors.RESET}\n")

    print(f"{Colors.YELLOW}{Colors.BOLD}BOTTOM LINE RECOMMENDATION:{Colors.RESET}")
    print(f"{report.bottom_line}\n")

    if report.best_options:
        print(f"{Colors.CYAN}{Colors.BOLD}TOP VERIFIED OPTIONS:{Colors.RESET}")
        for opt in report.best_options:
            print(f"  ⭐ {Colors.BOLD}{opt.get('title')}{Colors.RESET} - {opt.get('price_aud')}")
            print(f"     {opt.get('pros_summary')}")

    if report.business_results:
        print(f"\n{Colors.MAGENTA}{Colors.BOLD}LOCAL QUEENSLAND SPECIALISTS / WORKSHOPS:{Colors.RESET}")
        for b in report.business_results:
            print(f"  🔧 {Colors.BOLD}{b.name}{Colors.RESET} ({b.suburb_or_city}, {b.state}) - {b.phone or 'Contact via Web'}")
            print(f"     Specialization: {b.specialization_proof}")

    if report.claims:
        print(f"\n{Colors.BLUE}{Colors.BOLD}EXTRACTED CLAIMS & VERIFIED FACTS:{Colors.RESET}")
        for c in report.claims[:5]:
            status_str = c.status.value if hasattr(c.status, "value") else str(c.status)
            print(f"  • {c.claim_text} [{status_str.upper()} - {int(c.confidence * 100)}%]")

    if report.what_you_missed:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}WHAT DID YOU MISS? (Adjacent Angles & Opportunities):{Colors.RESET}")
        for m in report.what_you_missed:
            print(f"  💡 {m}")

    print(f"\n{Colors.GREEN}============================================================")
    print(f" Report ID: {report.report_id} | Actual Spend: ${report.actual_spend_aud:.2f} AUD | Confidence: {int(report.confidence_score * 100)}%")
    print(f"============================================================{Colors.RESET}\n")


def interactive_menu():
    print_banner()
    while True:
        print(f"{Colors.BOLD}Select an Option:{Colors.RESET}")
        print("  1. 🔍 Custom Universal Research Query")
        print("  2. 🚗 Ford Barra 1000hp + GM TH400 Package Finder (Brisbane/QLD)")
        print("  3. 🤖 AI Coding Fleet & SWE-bench Top Models Catalog")
        print("  4. 🎬 AI Video & Music Video Cost Calculator (Wan 2.2 vs Kling vs Hailuo)")
        print("  5. 🎮 Used RTX 4090 Deal Hunter (Gumtree, eBay, Cashies, CeX)")
        print("  6. 🎁 Active Developer Promotions & Free Credits")
        print("  7. 📊 System Health & Provider Diagnostics")
        print("  8. 🌐 Launch Live Web Dashboard (http://localhost:8000)")
        print("  0. ❌ Exit")

        choice = input(f"\n{Colors.CYAN}Enter Choice [0-8]: {Colors.RESET}").strip()

        if choice == "1":
            q = input(f"{Colors.YELLOW}Enter your research query: {Colors.RESET}").strip()
            if q:
                asyncio.run(execute_query(q))
        elif choice == "2":
            asyncio.run(execute_query("Find a complete 1,000hp Ford Falcon XR6 Turbo TH400 setup in Queensland"))
        elif choice == "3":
            models = model_catalog.get_models(free_only=True)
            print(f"\n{Colors.GREEN}{Colors.BOLD}TOP SWE-BENCH VERIFIED CODING MODELS (100% FREE):{Colors.RESET}")
            for m in models:
                print(f"  • {Colors.BOLD}{m.name}{Colors.RESET} ({m.provider}) | SWE-Bench: {m.swe_bench_verified_percent or 'N/A'}% | Context: {m.context_window // 1024}K | VRAM: {m.vram_gb}GB")
            print()
        elif choice == "4":
            video_engine = VideoCostEngine()
            costs = video_engine.calculate_all_costs(music_video_minutes=3.5)
            print(f"\n{Colors.CYAN}{Colors.BOLD}AI VIDEO COST CALCULATOR (3.5 min Music Video = 42-46 clips):{Colors.RESET}")
            for c in costs:
                print(f"  • {Colors.BOLD}{c.provider_name}{Colors.RESET}: ${c.music_video_total_aud:.2f} AUD total (${c.cost_per_clip_aud:.2f}/clip, ${c.cost_per_minute_aud:.2f}/min) - {c.notes}")
            print()
        elif choice == "5":
            asyncio.run(execute_query("Find used RTX 4090 graphics cards in Brisbane across Gumtree, eBay, Cashies, and CeX"))
        elif choice == "6":
            promo_hunter = PromotionHunter()
            promos = promo_hunter.discover_promotions()
            print(f"\n{Colors.MAGENTA}{Colors.BOLD}ACTIVE DEVELOPER PROMOTIONS & CREDITS:{Colors.RESET}")
            for p in promos:
                print(f"  🎁 {Colors.BOLD}{p.title}{Colors.RESET} ({p.provider}) - Value: ${p.estimated_value_aud:.2f} AUD | Card Required: {p.requires_credit_card}")
                print(f"     {p.description}")
            print()
        elif choice == "7":
            import subprocess
            subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(root_dir / "scripts" / "health.ps1")])
        elif choice == "8":
            import subprocess
            subprocess.run(["powershell", "-Command", "Start-Process 'http://localhost:8000'"])
        elif choice == "0":
            print(f"{Colors.GREEN}Exiting ResearchOS. Happy researching!{Colors.RESET}")
            break
        else:
            print(f"{Colors.RED}Invalid option, please try again.{Colors.RESET}\n")


def main():
    parser = argparse.ArgumentParser(description="ResearchOS CLI Command Center")
    parser.add_argument("--query", "-q", type=str, help="Direct research query to execute")
    parser.add_argument("--mode", "-m", type=str, default="FREE_ONLY", choices=["FREE_ONLY", "FREE_FIRST", "CHEAP", "LOCAL_ONLY", "FULL"])
    parser.add_argument("--depth", "-d", type=str, default="normal", choices=["fast", "normal", "deep", "exhaustive"])
    args = parser.parse_args()

    if args.query:
        print_banner()
        mode = OperatingMode(args.mode)
        depth = ResearchDepth(args.depth)
        asyncio.run(execute_query(args.query, mode=mode, depth=depth))
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
