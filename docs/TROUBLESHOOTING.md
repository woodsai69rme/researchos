# ResearchOS Troubleshooting & Diagnostic Guide

## Common Scenarios & Resolutions

### 1. Port 8000 Already in Use
**Symptoms:** `uvicorn` fails to bind or script shows port conflict.  
**Resolution:** Run `.\scripts\stop.ps1` or run:
```powershell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force
```

### 2. Local AI / Ollama Not Detected
**Symptoms:** Ollama health check shows OFFLINE.  
**Resolution:**
- Start Ollama in PowerShell: `ollama serve`
- Pull essential models: `ollama pull ornith-1.0-9b:q4_k_m`
- If running in Docker, ensure `OLLAMA_BASE_URL=http://host.docker.internal:11434`.

### 3. Rate Limiting on Free Search
**Symptoms:** Status indicator shows `RATE_LIMITED` on certain search engines.  
**Resolution:** ResearchOS automatically fails over across DuckDuckGo, Google News RSS, Reddit, GitHub, and local stores. You can also configure optional free API keys (Brave, Tavily, Exa) in `.env`.

### 4. Database File Permission / SQLite Locked
**Symptoms:** `sqlite3.OperationalError: database is locked`.  
**Resolution:** The database engine is configured with `check_same_thread=False` and async pooling. If a background process holds a lock, run `.\scripts\stop.ps1` and restart.
