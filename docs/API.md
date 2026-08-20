# ResearchOS REST & Streaming API Reference

## Base URL: `http://localhost:8000`

### 1. Health Probe
- **`GET /api/health`**
- Returns server status, active operating mode, and default region settings.

### 2. Deep Research Execution
- **`POST /api/research/execute`**
- Request Body:
```json
{
  "query": "Find the best free AI coding setup",
  "mode": "FREE_ONLY",
  "depth": "normal",
  "location": "Brisbane, Queensland, Australia",
  "budget": 0.0,
  "monitor_interval": 12
}
```
- Returns: `FinalResearchReport` containing claims, evidence nodes, deal scores, options, and what was missed.

### 3. Server-Sent Events (SSE) Live Feed
- **`GET /api/research/stream/{run_id}`**
- Streams real-time progress events as search swarm queries execute.

### 4. AI Models & Benchmarks Catalog
- **`GET /api/models?free_only=true`**
- Returns verified models with SWE-Bench scores, context sizes, and VRAM requirements.

### 5. Video Generation Cost Calculator
- **`GET /api/video-costs?minutes=3.5`**
- Returns cost per clip, cost per min, and music video total cost estimates.

### 6. Promotions & Free Tier Hunter
- **`GET /api/promotions?query=ai`**
- Returns active promotions, credit values, card requirements, and verification states.

### 7. Automotive Spec Engine
- **`GET /api/automotive/spec?query=XR6+Turbo+TH400`**
- Returns Barra TH400 conversion checklist and Brisbane workshops.

### 8. Continuous Watchlists & Alerts
- **`GET /api/watchlists`**
- **`POST /api/watchlists`**
- **`GET /api/alerts`**
- **`GET /api/providers/health`**
