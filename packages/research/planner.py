"""
ResearchOS Research Planner & Query Expansion Engine
"""
import re
from typing import List
from researchos.packages.core.schemas import ResearchPlan
from researchos.packages.core.config import settings, OperatingMode, ResearchDepth


class ResearchPlanner:
    def create_plan(
        self,
        user_query: str,
        mode: OperatingMode = OperatingMode.FREE_ONLY,
        depth: ResearchDepth = ResearchDepth.NORMAL,
        location: str = "Brisbane, Queensland, Australia",
        budget: float = 0.0,
    ) -> ResearchPlan:
        q_lower = user_query.lower()

        # Domain classification
        domain = "general"
        entities = []
        synonyms = []
        variants = []
        search_queries = [user_query]
        required_evidence = ["Official specifications", "Direct pricing", "Community feedback"]

        # 1. Automotive XR6T / TH400 domain
        if any(k in q_lower for k in ["xr6", "falcon", "th400", "barra", "gearbox", "tailshaft", "diff"]):
            domain = "automotive"
            entities.extend(["Ford Falcon XR6 Turbo", "GM TH400 Transmission", "Barra 4.0L DOHC Turbo"])
            synonyms.extend(["XR6T", "Falcon Turbo", "BA Turbo", "BF Turbo", "FG Turbo", "FGX Turbo", "Barra 1000hp", "Turbo 400", "Turbo Hydramatic 400"])
            variants.extend(["TH400 conversion package", "TH400 SFI bellhousing", "Barra flexplate", "TH400 1350 tailshaft", "Falcon Truetrac diff"])
            search_queries.extend([
                f"{user_query} Brisbane Queensland",
                "Ford Falcon XR6 Turbo TH400 conversion kit package Australia",
                "Barra to TH400 gearbox workshop dyno Brisbane",
                "Built 1000hp TH400 transmission Barra bellhousing converter",
            ])
            required_evidence.extend(["SFI certification", "Horsepower rating proof", "Workshop build history"])

        # 2. AI Coding & Free Tier Tools
        elif any(k in q_lower for k in ["coding", "coder", "ide", "agent", "cursor", "windsurf", "claude code", "aider", "cline"]):
            domain = "ai_coding"
            entities.extend(["OpenRouter Free Models", "Ollama Local Models", "Cursor", "Windsurf", "Claude Code", "Cline", "Aider"])
            synonyms.extend(["Free AI coding assistant", "SWE-Bench verified models", "Open-source coding LLM", "Free API tokens", "CLI coding agent"])
            variants.extend(["Gemma 4 26B Free", "Ornith 1.0 35B MoE", "Qwen 2.5 Coder 32B", "DeepSeek R1"])
            search_queries.extend([
                "best free AI coding models agents CLI tools 2026",
                "OpenRouter free coding tier limits Gemma 4 Nemotron",
                "local AI coding setup 8GB VRAM RTX 4060 Ollama",
                "Claude Code Cursor Windsurf free alternatives open source",
            ])

        # 3. AI Video Tools & Music Videos
        elif any(k in q_lower for k in ["video", "clip", "music video", "kling", "hailuo", "wan", "runway", "luma", "sora", "veo"]):
            domain = "ai_video"
            entities.extend(["Wan 2.2 Local", "Kling AI", "Hailuo Video-01", "Runway Gen-3", "Luma Dream Machine", "Google Veo"])
            synonyms.extend(["Text to video", "Image to video", "AI music video generation", "Free video credits", "Local video model"])
            search_queries.extend([
                "best free AI video generators for music videos",
                "Wan 2.2 local ComfyUI 8GB VRAM workflow",
                "Kling Hailuo Runway free generation daily credits comparison",
                "AI video cost per minute music video production",
            ])

        # 4. Electronics & Second-Hand Deals (e.g. RTX 4090)
        elif any(k in q_lower for k in ["rtx", "4090", "gpu", "graphics card", "cash converters", "cex", "gumtree", "ebay"]):
            domain = "electronics_deals"
            entities.extend(["NVIDIA GeForce RTX 4090", "Gumtree AU", "eBay AU", "Cash Converters AU", "CeX Australia"])
            synonyms.extend(["RTX 4090 24GB", "RTX 4090 FE", "ASUS TUF 4090", "Used graphics card Brisbane"])
            search_queries.extend([
                f"{user_query} Brisbane Gumtree eBay Cash Converters",
                "RTX 4090 used price Brisbane Queensland marketplace",
                "NVIDIA RTX 4090 CeX Australia warranty price",
            ])

        # General expansion
        else:
            search_queries.extend([
                f"{user_query} Australia pricing reviews",
                f"{user_query} free tier open source alternatives",
            ])

        return ResearchPlan(
            original_query=user_query,
            normalized_query=user_query.strip(),
            intent=f"Deep research, deal hunting and evidence verification for: {user_query}",
            domain_category=domain,
            entities=entities,
            synonyms=synonyms,
            model_variants=variants,
            geographic_scope=location,
            source_classes=["Web", "Marketplace", "GitHub", "Reddit", "YouTube", "Workshops", "Official"],
            search_queries=list(dict.fromkeys(search_queries)), # deduplicate list
            required_evidence=required_evidence,
            budget=budget,
            currency="AUD",
            free_only=(mode == OperatingMode.FREE_ONLY),
            operating_mode=mode.value,
        )
