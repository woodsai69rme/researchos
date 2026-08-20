# ResearchOS — Universal Deep Research & Deal Hunter OS
**Target:** Windows 11 + Docker + Local AI (Ollama) + Free-First Cloud  
**Default Localization:** Australia / Brisbane (`AUD`, `Australia/Brisbane`)  
**Version:** 1.0.0

---

## ⚡ Overview

**ResearchOS** is a universal AI-powered research, discovery, comparison, marketplace, deal-hunting, review-analysis, and continuous-monitoring platform.

You enter **ONE natural-language request**:
> *"What am I trying to find?"*

ResearchOS automatically determines the intent, normalizes variants, coordinates a parallel search swarm across web, code, marketplace, community, and business registries, deduplicates sources, checks contradictions, evaluates deal scores, and presents verified reports with continuous 12-hour/24-hour monitoring.

---

## 🛡️ Non-Negotiable Free-First Policy

ResearchOS enforces strict spending modes:

| Mode | Spend Limit | Cloud Paid Execution | Local Ollama / Free Tiers |
| :--- | :--- | :--- | :--- |
| **`FREE_ONLY`** | **$0.00 AUD (Hardcoded)** | ❌ BLOCKED | ✅ Active (DuckDuckGo, Google News, OpenRouter Free, Local Ollama) |
| **`FREE_FIRST`** | $0.00 default | ⚠️ Explicit Opt-in Only | ✅ Active |
| **`CHEAP`** | Budget Capped | ⚠️ Tracked & Budget-Limited | ✅ Active |
| **`LOCAL_ONLY`** | $0.00 | ❌ BLOCKED (Cloud Blocked) | ✅ Pure Local Ollama / Local Scrapers |
| **`FULL`** | User Configured | ✅ Allowed with confirmation | ✅ Active |

---

## 🚀 Quick Start on Windows 11

### 1. Automated Setup
```powershell
# Run the automated installer
.\scripts\install.ps1
```

### 2. Launch the Application
```powershell
.\scripts\start.ps1
```
Open **http://localhost:8000** in your browser to access the live dashboard.

### 3. Run Verification Tests
```powershell
.\scripts\test.ps1
```

---

## 🧭 Multi-Domain Specialized Profiles

1. **AI Coding Fleet**
   - Discovers SWE-Bench ranked models (`Ornith 1.0 35B` 75.6%, `Ornith 9B` 69.4%, `Gemma 4 26B Free`, `Qwen 2.5 Coder`).
   - Compares agents: Cursor, Windsurf, Claude Code, Cline, Roo Code, Aider.
2. **AI Video & Music Video Cost Calculator**
   - Compares Wan 2.2 Local (ComfyUI $0), Kling AI (66 daily free credits), Hailuo Video-01, Runway Gen-3, Luma, Veo, Sora.
   - Computes exact cost per clip, cost per minute, and clips required for full music videos.
3. **Automotive & Barra 1,000hp Drivetrains**
   - Ford Falcon XR6 Turbo BA/BF/FG/FGX Barra 4.0L DOHC Turbo + GM TH400 3-speed packages.
   - SFI bellhousings, anti-ballooning converters, crossmembers, 1350 tailshafts, Truetrac diffs, and Brisbane/QLD workshops.
4. **Marketplace Deal Hunter**
   - Aggregates Gumtree AU, eBay AU, Cash Converters AU, CeX AU, and Facebook Marketplace.
   - Deal Score (0-100) factoring in market median discount, condition, warranty, and seller trust.
5. **Continuous 12-Hour Monitoring**
   - Snapshot diffing detecting price drops, free quota shifts, new models, and promo expirations.

---

## 📁 Project Structure

```
researchos/
├── apps/
│   ├── api/                    # FastAPI server & SSE streaming
│   ├── web/                    # Next.js & HTML5 Tailwind dashboard
│   ├── scheduler/              # 12h/24h continuous monitoring scheduler
│   └── worker/                 # Background task worker
├── packages/
│   ├── core/                   # Schemas, Config, Events, Structured Logging, Redaction
│   ├── security/               # FREE_ONLY policy enforcer, SSRF protection, prompt injection guard
│   ├── providers/              # Provider Registry, Quota & Latency tracking, Failover chains
│   ├── research/               # Research Planner, "What Did I Miss?", Search Swarm, Synthesis
│   ├── evidence/               # Deduplication, Canonical URL, Credibility hierarchy, Lineage graph
│   ├── claims/                 # Claim extraction, Contradiction detection engine
│   ├── marketplace/            # Deal Score algorithm, Listing normalizer
│   ├── business/               # Workshop finder (Ford Barra / TH400 / Diffs in QLD/Brisbane)
│   ├── reviews/                # Community sentiment analyzer (Reddit, YouTube, GitHub, Forums)
│   ├── pricing/                # AUD multi-currency converter, Video & API cost calculators
│   ├── promotions/             # Promo & Free tier discovery engine
│   └── models/                 # AI model catalog, SWE-Bench benchmarks
├── connectors/
│   ├── search/                 # DuckDuckGo, Google News RSS, Brave, Tavily, Exa, Serper
│   ├── ai/                     # OpenRouter Free, Google Gemini, Ollama Local
│   ├── marketplaces/           # Gumtree AU, eBay AU, Cash Converters, CeX AU
│   ├── code/                   # GitHub API (repos, releases, issues)
│   ├── social/                 # Reddit JSON, YouTube search
│   └── business/               # OpenStreetMap Overpass & Australian Directory
├── db/                         # SQLite / PostgreSQL models and database session
├── scripts/                    # PowerShell automation: install, start, stop, health, test, backup
├── tests/                      # Unit & integration test suites
└── docs/                       # Comprehensive documentation guides
```
