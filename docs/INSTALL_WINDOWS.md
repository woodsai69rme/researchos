# ResearchOS Windows 11 Installation & Setup Guide

## 1. Native Windows 11 Installation
ResearchOS is fully optimized for Windows 11 without requiring WSL2 or Docker for standard operation.

### Step 1: Open PowerShell as Administrator / User
Navigate to the ResearchOS project folder:
```powershell
cd C:\Users\karma\researchos
```

### Step 2: Run the Automated Installer
```powershell
.\scripts\install.ps1
```
This script will:
1. Verify Python 3.10+ installation.
2. Create `.env` from `.env.example`.
3. Install required Python packages (`fastapi`, `uvicorn`, `pydantic`, `httpx`, `sqlalchemy`, `aiosqlite`, `bs4`, `structlog`).
4. Initialize the local SQLite database in `data/researchos.db`.
5. Verify Local Ollama connectivity.

### Step 3: Start the Application
```powershell
.\scripts\start.ps1
```
Access the dashboard at **http://localhost:8000**.

---

## 2. Docker Compose Deployment (Optional)
If running via Docker Desktop on Windows:

```powershell
docker-compose up -d --build
```
This starts:
- `researchos-api` (Port 8000)
- `researchos-scheduler`
- `researchos-redis` (Port 6379)
- `researchos-qdrant` (Port 6333)

---

## 3. Useful PowerShell Scripts
- **Start:** `.\scripts\start.ps1`
- **Stop:** `.\scripts\stop.ps1`
- **Health:** `.\scripts\health.ps1`
- **Tests:** `.\scripts\test.ps1`
- **Backup:** `.\scripts\backup.ps1`
- **Update:** `.\scripts\update.ps1`
