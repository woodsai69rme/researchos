"""
ResearchOS Dedicated Entry Point Server Runner
"""
import os
import sys
from pathlib import Path

# Ensure root workspace is in sys.path
root_dir = Path(__file__).resolve().parent
parent_dir = root_dir.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(parent_dir))
os.environ["PYTHONPATH"] = str(parent_dir)

import uvicorn

if __name__ == "__main__":
    uvicorn.run("researchos.apps.api.main:app", host="0.0.0.0", port=8000, reload=False)
