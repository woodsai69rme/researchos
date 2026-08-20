# ResearchOS Provider Registry & Adapters Reference

## Search Providers

| Provider | Type | Free Status | Requirements | Quota / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **DuckDuckGo** | Native Scraper | 100% Free | None | Unlimited public web search with AU regional support |
| **Google News RSS** | RSS Feed | 100% Free | None | Real-time news articles with Australian localization |
| **Brave Search** | REST API | Free Allowance | `BRAVE_API_KEY` | 2,000 queries/month free tier |
| **Tavily AI Search** | REST API | Free Allowance | `TAVILY_API_KEY` | 1,000 queries/month free credits |
| **Exa Search** | REST API | Free Allowance | `EXA_API_KEY` | Neural similarity & auto-prompting |
| **Serper.dev** | REST API | Free Credits | `SERPER_API_KEY` | Google search wrapper with free startup credits |

## AI Reasoning & Generation Providers

| Provider | Type | Free Status | Local / Cloud | Default Model |
| :--- | :--- | :--- | :--- | :--- |
| **Local Ollama** | HTTP API | 100% Free | Local (RTX 4060) | `ornith-1.0-9b:q4_k_m`, `deepseek-r1:8b` |
| **OpenRouter Free** | REST API | 100% Free | Cloud | `google/gemma-4-26b-a4b-it:free` |
| **Google Gemini** | REST API | Free Tier | Cloud | `gemini-1.5-flash` (15 RPM free) |
| **LM Studio** | OpenAI API | 100% Free | Local | `localhost:1234/v1` |

## Marketplaces & Directories
- **Gumtree AU & eBay AU:** Standard Australian listings.
- **Cash Converters & CeX AU:** Second-hand hardware with warranty tracking.
- **OpenStreetMap Overpass:** Australian mechanical and performance workshops.
