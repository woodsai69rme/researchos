# ResearchOS - Latest Enhancements & Resource Discovery
**Compiled: August 2026** | **Source: GitHub Awesome Lists, Reddit, YouTube, Social Media, Official Docs**

---

## 📚 **Curated Awesome Lists for ResearchOS Enhancement**

### **Core AI/ML Awesome Lists**

| Repository | Stars | Description | Relevance |
|------------|-------|-------------|-----------|
| [sindresorhus/awesome](https://github.com/sindresorhus/awesome) | 498k | Master awesome list - 2000+ curated lists | Meta-reference |
| [TalEliyahu/Awesome-AI-Security](https://github.com/TalEliyahu/Awesome-AI-Security) | 853 | AI security resources & tools | Security hardening |
| [scadastrangelove/awesome-ai-security-tools](https://github.com/scadastrangelove/awesome-ai-security-tools) | 1068 | Public-source & commercial AI security tools | Security tools |
| [Astrosp/Awesome-OSINT-List](https://github.com/Astrosp/Awesome-OSINT-List) | 4210 | Comprehensive OSINT for cybersecurity | Marketplace/business search |
| [medtorch/awesome-healthcare-ai](https://github.com/medtorch/awesome-healthcare-ai) | 353 | Open source healthcare AI, datasets, papers | Domain-specific research |

### **LLM & AI Agent Specific Lists**

| Repository | Focus | Key Resources |
|------------|-------|---------------|
| [awesome-llm](https://github.com/Hannibal046/Awesome-LLM) | LLMs, fine-tuning, serving | Model catalog, benchmarks, inference |
| [awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) | LLM applications | RAG, agents, tools, frameworks |
| [awesome-ai-agents](https://github.com/e2b-dev/awesome-ai-agents) | Autonomous agents | Agent frameworks, benchmarks |
| [awesome-local-llm](https://github.com/llmware-ai/awesome-local-llm) | Local LLM deployment | Ollama, LM Studio, llama.cpp, quantization |
| [awesome-rag](https://github.com/Shubhamsaboo/awesome-rag) | RAG systems | Vector DBs, embeddings, retrieval |
| [awesome-computer-use](https://github.com/OSINT/awesome-computer-use) | Computer use agents | Browser automation, OS control |

### **Research & Search Specific**

| Repository | Focus | Key Resources |
|------------|-------|---------------|
| [awesome-search](https://github.com/awesome-search/awesome-search) | Search engines & APIs | Brave, Tavily, Exa, Serper, SearXNG |
| [awesome-web-scraping](https://github.com/lorien/awesome-web-scraping) | Scraping tools | Playwright, Selenium, Scrapy, anti-bot |
| [awesome-osint](https://github.com/jivoi/awesome-osint) | Open source intelligence | Data sources, tools, frameworks |
| [awesome-research-tools](https://github.com/emptycrown/awesome-research-tools) | Academic/research tools | Paper search, citation, note-taking |

### **Video Generation & AI Creative**

| Repository | Focus | Key Resources |
|------------|-------|---------------|
| [awesome-generative-video](https://github.com/victordibia/awesome-generative-video) | Text-to-video, I2V, V2V | Sora, Veo, Kling, Runway, Pika, Wan |
| [awesome-ai-video](https://github.com/ltdrdata/awesome-ai-video) | Video AI tools | Editing, upscaling, avatars, lip-sync |
| [awesome-comfyui](https://github.com/comfyanonymous/awesome-comfyui) | ComfyUI workflows | Nodes, models, custom workflows |

### **Coding & Development AI**

| Repository | Focus | Key Resources |
|------------|-------|---------------|
| [awesome-ai-coding](https://github.com/hesreallyhim/awesome-ai-coding) | AI coding assistants | Cursor, Windsurf, Cline, Aider, Continue |
| [awesome-llm-code](https://github.com/tortuml/awesome-llm-code) | Code generation models | CodeLlama, StarCoder, DeepSeek-Coder, Qwen |
| [awesome-dev-tools](https://github.com/learn-anything/awesome-dev-tools) | Developer productivity | IDEs, CLI tools, debugging, testing |

---

## 🔬 **Latest Research & Enhancements (2024-2026)**

### **1. AI Research Agents - Major Advances**

#### **Deep Research Agents**
- **OpenAI Deep Research** (Feb 2025) - Multi-step reasoning, citation tracking, 30-min research runs
- **Google Deep Research** (Dec 2024) - Gemini 1.5 Pro, 1M context, iterative search
- **Perplexity Deep Research** - Free tier available, structured reports
- **LangChain Deep Research** - Open-source agent with tool use

#### **Autonomous Research Frameworks**
- **GPT-Researcher** (v0.7+) - Autonomous research agent with configurable depth
- **AutoGPT-Research** - Multi-agent research with planning/execution separation
- **BabyAGI-Research** - Task decomposition for research workflows
- **MetaGPT-Research** - Software company simulation for research projects

### **2. Search Provider Updates (2024-2026)**

| Provider | Free Tier | Key Changes 2024-2026 |
|----------|-----------|----------------------|
| **Brave Search API** | 2000 req/mo | Added AI summaries, "Goggles" custom ranking |
| **Tavily** | 1000 req/mo | Deep research mode, citation extraction |
| **Exa** | 1000 req/mo | Neural search, highlights, similar pages |
| **Serper** | 2500 req/mo | Google Maps, Shopping, News endpoints |
| **SearXNG** | Self-hosted | New engines, JSON API, rate limiting |
| **DuckDuckGo HTML** | Unlimited | Lite.duckduckgo.com for lighter scraping |
| **You.com API** | 1000 req/mo | AI chat + search combined |
| **Perplexity API** | 5 req/min | Sonar models, citations, follow-ups |

### **3. Free AI Model Access (2026)**

#### **OpenRouter Free Models (Updated Aug 2026)**
```
google/gemma-4-26b-a4b-it:free          # 26B MoE, best free reasoning
nvidia/nemotron-nano-12b-v2-vl:free     # 12B vision-language
nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free  # 30B MoE reasoning
meta-llama/llama-3.1-8b-instruct:free   # 8B instruction tuned
microsoft/phi-3.5-mini-instruct:free    # 3.8B, 128K context
qwen/qwen2.5-7b-instruct:free           # 7B multilingual
deepseek/deepseek-r1-distill-qwen-7b:free  # Reasoning distilled
```

#### **Local Models (Ollama/LM Studio) - RTX 4060 8GB Optimized**
| Model | Size (Q4) | VRAM | Best For |
|-------|-----------|------|----------|
| **Ornith-1.0-9B** | 5.6 GB | 5.6 GB | **Daily coding** - 69.4% SWE-Bench |
| **Ornith-1.0-35B** | 21 GB | 21 GB sys RAM | **Heavy coding** - 75.6% SWE-Bench + `--n-cpu-moe` |
| **Qwythos-9B** | 5.3 GB | 5.3 GB | Reasoning/creative - 1M context, uncensored |
| **Phi-4-mini** | 2.5 GB | 2.5 GB | STEM/fast - 30s responses |
| **Qwen2.5-Coder-7B** | 4.7 GB | 4 GB | Coding fallback - 40+ tok/s |
| **DeepSeek-R1-8B** | 5.2 GB | 5.2 GB | CoT reasoning/debugging |
| **Nemotron-3-Ultra** | ~30 GB | Offload | Best local reasoning |

#### **New Free Video Generation (2024-2026)**
| Tool | Free Tier | Resolution | Duration | Notes |
|------|-----------|------------|----------|-------|
| **Kling AI** | 66 credits/day | 1080p | 5-10s | Best quality free |
| **Hailuo (Minimax)** | 30 credits/day | 720p | 6s | Good motion |
| **Runway Gen-3** | 125 credits/mo | 720p | 5-10s | Professional |
| **Pika 1.5** | 30 credits/day | 720p | 5s | Effects, templates |
| **Luma Dream Machine** | 30 gens/mo | 720p | 5s | Fast generation |
| **Wan 2.2 (Local)** | Unlimited | 480p-720p | 5-10s | **RTX 4060 8GB compatible** |
| **Sora** | Waitlist | 1080p | 20s | Not publicly free |

### **4. Marketplace & Business Search Enhancements**

#### **New APIs & Sources (2024-2026)**
- **Facebook Graph API v20** - Marketplace search (requires approval)
- **Gumtree API** - Unofficial Python wrappers available
- **Cars.com API** - Dealer/private listings
- **AutoTrader API** - UK/AU vehicle data
- **eBay Browse API** - 5000 calls/day free
- **Google Places API** - Business search, $200/mo free credit
- **Yelp Fusion API** - 5000 req/day free
- **OpenCorporates** - Company data, free tier

#### **Automotive Specific (AU Focus)**
- **Pickles Auctions API** - Fleet/vehicle auctions
- **Grays Online** - Industrial/vehicle auctions
- **Manheim API** - Dealer auctions (partner only)
- **RedBook/Glass's Guide** - Vehicle valuations
- **CarHistory/PPSR** - Vehicle history reports

### **5. Monitoring & Alerting Advances**

#### **Change Detection Tools**
- **Changedetection.io** - Self-hosted, 100+ notification channels
- **Visualping** - Visual change detection, free tier
- **Distill.io** - Browser extension + cloud
- **PageMonitor** - Lightweight self-hosted
- **FeedWatcher** - RSS/Atom + web page monitoring

#### **AI-Specific Monitoring**
- **LLM Monitor** - Track model performance, pricing, availability
- **OpenRouter Status** - Real-time model availability
- **Hugging Face Hub API** - New model releases, trending
- **Papers with Code API** - Latest benchmarks, SOTA

---

## 🛠 **ResearchOS Integration Recommendations**

### **Priority 1: Core Enhancements (Immediate)**

```yaml
# Add to .env.example - New free providers
YOU_COM_API_KEY=              # You.com search + chat
PERPLEXITY_API_KEY=           # Perplexity Sonar models
SEARXNG_INSTANCE_URL=         # Self-hosted SearXNG
CHANGEDETECTION_URL=          # Self-hosted change detection
```

```python
# packages/providers/search.py - Add new providers
class YouComSearchProvider(SearchProvider):
    """You.com AI Search - combines search + LLM"""
    # Free: 1000 req/mo
    
class PerplexitySearchProvider(SearchProvider):
    """Perplexity API - citations + follow-ups"""
    # Free: 5 req/min
```

### **Priority 2: Deep Research Agent (Week 1-2)**

```python
# agents/research/deep_researcher.py
class DeepResearchAgent:
    """Multi-step research with planning, execution, verification"""
    
    async def research(self, query: str, depth: ResearchDepth) -> ResearchReport:
        # 1. Plan: Decompose into sub-questions
        # 2. Search: Parallel multi-provider search
        # 3. Extract: Claim extraction + verification
        # 4. Synthesize: Cross-reference + contradiction resolution
        # 5. Report: Structured output with evidence
```

### **Priority 3: Local-First Video Generation (Week 2-3)**

```python
# packages/models/video_local.py
class LocalVideoGenerator:
    """Wan 2.2 / LTX-Video / HunyuanVideo on RTX 4060"""
    
    SUPPORTED_MODELS = {
        "wan2.2-ti2v-5b": {"vram": "6-8GB", "quant": "Q4_K_M"},
        "ltx-video-2b": {"vram": "4-6GB", "quant": "Q4_K_M"},
        "hunyuanvideo-2b": {"vram": "6-8GB", "quant": "Q4_K_M"},
    }
```

### **Priority 4: Awesome List Integration (Week 3-4)**

```python
# connectors/github/awesome_list_parser.py
class AwesomeListParser:
    """Parse awesome lists for tool discovery"""
    
    TARGET_LISTS = [
        "awesome-llm", "awesome-ai-agents", "awesome-rag",
        "awesome-ai-coding", "awesome-generative-video",
        "awesome-local-llm", "awesome-computer-use",
        "awesome-search", "awesome-osint"
    ]
    
    async def discover_tools(self, category: str) -> List[ToolMetadata]:
        # Fetch README, parse sections, extract tool metadata
        # Return structured data for AI model catalogue
```

---

## 📊 **Reddit & Community Intelligence (2024-2026)**

### **Key Subreddits to Monitor**
| Subreddit | Focus | Monitoring Keywords |
|-----------|-------|---------------------|
| r/LocalLLaMA | Local LLMs | quantization, GGUF, llama.cpp, Ollama |
| r/StableDiffusion | Image/video gen | ComfyUI, Flux, SDXL, video models |
| r/Singularity | AI news | model releases, benchmarks, AGI |
| r/MachineLearning | Research papers | arXiv, benchmarks, SOTA |
| r/AI_Agents | Autonomous agents | AutoGPT, BabyAGI, LangGraph |
| r/selfhosted | Self-hosting | SearXNG, changedetection, Ollama |
| r/DataHoarder | Data archival | datasets, scraping, storage |
| r/aussie | AU-specific | Gumtree, Carsales, FB Marketplace AU |

### **Current Community Consensus (Aug 2026)**

#### **Best Free Coding Setup**
```
1. Primary: Ornith-1.0-9B (local, 5.6GB VRAM) - 69.4% SWE-Bench
2. Heavy: Ornith-1.0-35B + --n-cpu-moe (21GB sys RAM) - 75.6% SWE-Bench
3. Cloud fallback: Gemini 1.5 Flash (free tier, 1M context)
4. Agent: Cline + Ornith-9B or Continue + local
```

#### **Best Free Video Generation**
```
1. Local: Wan 2.2 TI2V-5B GGUF Q4 (RTX 4060 8GB compatible)
2. Cloud: Kling AI (66 credits/day, best quality)
3. Cloud: Hailuo/Minimax (30 credits/day, good motion)
4. Local: LTX-Video 2B (lower VRAM, faster)
```

#### **Best Search Strategy**
```
1. Parallel: Brave + Tavily + Exa (all have free tiers)
2. Fallback: DuckDuckGo HTML + SearXNG (unlimited)
3. Specialized: GitHub API (code), YouTube API (video), Reddit API (discussions)
4. Verification: Cross-reference 3+ sources, check dates, detect copied content
```

---

## 🎬 **Latest YouTube Channels for ResearchOS**

### **Technical Deep Dives**
| Channel | Focus | Key Playlists |
|---------|-------|---------------|
| **AI Explained** | Model analysis | LLM benchmarks, architecture |
| **Yannic Kilcher** | Paper reviews | ICML, NeurIPS, ICLR |
| **Machine Learning Street Talk** | Interviews | Researchers, founders |
| **Sebastian Raschka** | ML engineering | Local LLMs, fine-tuning |
| **Andrej Karpathy** | LLM training | Zero to Hero, tokenization |

### **Practical Tutorials**
| Channel | Focus | Key Content |
|---------|-------|-------------|
| **NetworkChuck** | Self-hosting | Ollama, SearXNG, Docker |
| **Tech With Tim** | Python/ML | RAG, agents, LangChain |
| **Cole Medin** | AI agents | AutoGPT, CrewAI, LangGraph |
| **All About AI** | No-code AI | n8n, Flowise, automation |
| **Matt Wolfe** | AI tools | Weekly tool reviews, free tiers |

### **Australian Tech**
| Channel | Focus |
|---------|-------|
| **Dave Lee Down Under** | Hardware, local AI |
| **Hardware Unboxed** | GPU benchmarks |
| **Gamers Nexus** | Hardware testing |

---

## 🔗 **Integration Checklist for ResearchOS**

### **Search Providers to Add**
- [ ] You.com API (search + chat combined)
- [ ] Perplexity API (citations, follow-ups)
- [ ] SearXNG self-hosted instance
- [ ] GitHub Search API (code, repos, issues)
- [ ] Reddit API (discussions, sentiment)
- [ ] YouTube Data API v3 (transcripts, metadata)
- [ ] ArXiv API (academic papers)
- [ ] Crossref API (citations, DOIs)

### **AI Providers to Add**
- [ ] Groq API (ultra-fast inference, free tier)
- [ ] Cerebras API (fast inference)
- [ ] Together AI (open models, free credits)
- [ ] Replicate API (model hosting, pay-per-use)
- [ ] Fireworks AI (fast open models)
- [ ] Local: vLLM server (OpenAI-compatible)
- [ ] Local: TGI (text generation inference)

### **Marketplace Sources (AU)**
- [ ] Facebook Marketplace (Graph API - needs approval)
- [ ] Gumtree (unofficial scrapers)
- [ ] Carsales.com.au (dealer API)
- [ ] CarGurus Australia
- [ ] Pickles Auctions
- [ ] Grays Online
- [ ] eBay Australia Browse API
- [ ] Facebook Groups (public - car parts, tech)

### **Monitoring & Alerting**
- [ ] Changedetection.io self-hosted
- [ ] RSS/Atom feed monitoring (blogwatcher)
- [ ] GitHub releases webhook
- [ ] Reddit keyword monitoring (Pushshift)
- [ ] Price tracking (CamelCamelCamel, Keepa APIs)
- [ ] Model availability (OpenRouter, HuggingFace APIs)

---

## 📈 **Implementation Roadmap**

| Phase | Timeline | Deliverables |
|-------|----------|--------------|
| **Phase 1** | Week 1 | Core search providers (You.com, Perplexity, SearXNG) |
| **Phase 2** | Week 2 | Deep research agent + multi-step planning |
| **Phase 3** | Week 3 | Local video generation (Wan 2.2, LTX) |
| **Phase 4** | Week 4 | Awesome list parser + auto-discovery |
| **Phase 5** | Week 5 | Marketplace AU sources + automotive |
| **Phase 6** | Week 6 | Monitoring dashboard + change detection |
| **Phase 7** | Week 7 | Reddit/social sentiment + community intelligence |
| **Phase 8** | Week 8 | Benchmark integration + model leaderboard |

---

## 💡 **Key Insights for ResearchOS Differentiation**

1. **Free-First Architecture** - Unique selling point; no other tool enforces this centrally
2. **Local-First Video** - RTX 4060 8GB compatible Wan 2.2 is a killer feature
3. **Australian Market Focus** - Gumtree, Carsales, FB Marketplace AU, local workshops
4. **Automotive Domain Expertise** - TH400, XR6, Barra specialists - niche but high value
4. **Evidence Graph** - Source lineage tracking prevents false consensus from copied content
5. **Contradiction Engine** - Automatically detects and explains conflicts
6. **Community Intelligence** - Reddit/YouTube sentiment weighted by recency and independence

---

*This document should be updated monthly. Next review: September 2026.*