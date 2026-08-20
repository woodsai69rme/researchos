# ResearchOS Quickstart Guide

## 1. Prerequisites
- **Operating System:** Windows 11 (or Docker / Linux)
- **Python:** 3.10+ (tested on Python 3.13)
- **Optional Local AI:** Ollama with models (`ornith-1.0-9b:q4_k_m`, `deepseek-r1:8b`)

## 2. Launch in 60 Seconds
```powershell
cd C:\Users\karma\researchos
.\scripts\start.ps1
```
The server will boot and open **http://localhost:8000** in your browser.

## 3. Trying Example Queries

### Example 1: Free AI Coding Fleet
```text
"Find every free AI coding model, agent, API, IDE, CLI tool, trial and promo"
```
- **What ResearchOS does:** Searches OpenRouter Free, Ollama local catalog, GitHub releases, and Reddit discussions. Returns SWE-Bench rankings, context windows, and zero-cost installation instructions.

### Example 2: Automotive 1,000hp Barra Setup
```text
"Find a complete 1,000hp Ford Falcon XR6 Turbo TH400 setup in Queensland"
```
- **What ResearchOS does:** Parses fitment compatibility for Ford Barra DOHC 4.0L + GM TH400. Checks SFI bellhousing, high-stall converter, crossmember, 1350 tailshaft, and locates top-rated Brisbane builders (Monsta Torque, Al's Race Glides, Hard Drive Diffs).

### Example 3: AI Video Cost Calculator
```text
"Find the best AI video generation tools for music videos, including free tiers"
```
- **What ResearchOS does:** Evaluates Wan 2.2 local ComfyUI, Kling AI, Hailuo, Runway Gen-3, Luma, and Sora. Calculates clips required, cost per minute, and monthly free allowances.

### Example 4: Used RTX 4090 Deal Hunter
```text
"Find used RTX 4090 graphics cards in Brisbane across Gumtree, eBay, Cashies, and CeX"
```
- **What ResearchOS does:** Scrapes Australian marketplace listings, scores each deal (0-100) vs market median, highlights CeX 24-month warranties, and flags high-value options.
