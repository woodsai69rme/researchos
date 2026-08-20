# ResearchOS System Architecture

## Architecture Diagram

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                         RESEARCHOS WEB DASHBOARD                            │
 │         (HTML5 / Tailwind CSS / Lucide / Next.js on Port 8000/3000)         │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │ REST & Server-Sent Events (SSE)
                                        ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                     FASTAPI ASYNC APPLICATION SERVER                        │
 │    Endpoints: /api/research/execute, /api/models, /api/video-costs, etc.    │
 └──────────────────────┬───────────────────────────────┬──────────────────────┘
                        │                               │
                        ▼                               ▼
 ┌──────────────────────────────┐              ┌───────────────────────────────┐
 │   FREE POLICY ENFORCER       │              │       RESEARCH PLANNER        │
 │  - FREE_ONLY Mode ($0 spend) │              │  - Intent & Entity Normalizer │
 │  - Budget Gate & SSRF Guard  │              │  - Query Expansion Generator  │
 └──────────────┬───────────────┘              └───────────────┬───────────────┘
                │                                              │
                ▼                                              ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                       PARALLEL SEARCH SWARM ENGINE                          │
 │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
 │  │ DuckDuckGo  │ │ GoogleNews  │ │   GitHub    │ │   Reddit    │ │YouTube │ │
 │  │ Free Search │ │  Free RSS   │ │  API Repos  │ │ Discussions │ │ Videos │ │
 │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
 │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
 │  │ Gumtree AU  │ │   eBay AU   │ │Cashies / CeX│ │  OSM Places │ │ Ollama │ │
 │  │ Marketplace │ │ Marketplace │ │ Used Deals  │ │  Workshops  │ │ Local  │ │
 │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                       INTELLIGENCE & SYNTHESIS STACK                        │
 │  1. Canonical Deduplication & Syndicated PR Detection (10 copies -> 1 root) │
 │  2. Evidence Graph & Credibility Tiering (Primary > Secondary > Community)  │
 │  3. Factual Claim Extraction & Contradiction Detection (Price, Quotas, Fit) │
 │  4. Deal Scorer (0-100 score vs market median, condition & warranty)        │
 │  5. "What Did I Miss?" Adjacent Category Discovery Feedback Loop            │
 │  6. Review Sentiment Analysis (Praise, Complaints, Bug Tracker)             │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │             PERSISTENCE, CONTINUOUS 12H MONITORING & ALERTS                 │
 │  - SQLite / PostgreSQL Database with historical runs and snapshots          │
 │  - 12h/24h Background Scheduler diffing price drops & quota changes         │
 └─────────────────────────────────────────────────────────────────────────────┘
```

## Core Subsystems
1. **Security & Free-First Enforcer:** Guarantees zero billing under `FREE_ONLY` mode.
2. **Search Swarm:** Dispatches queries in parallel across search engines, social feeds, and Australian marketplaces.
3. **Evidence Graph:** Tracks source lineage and calculates true source independence.
4. **Contradiction Engine:** Flags conflicting pricing or capability claims.
5. **Continuous Scheduler:** Periodically executes watchlists and fires alerts upon meaningful state changes.
