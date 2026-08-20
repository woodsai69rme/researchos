# ResearchOS AI Coding Fleet & SWE-Bench Rankings

## Top Coding Models for Local 8GB GPU & Free Cloud

| Model | SWE-Bench Score | Context Window | VRAM / Host | Cost | Best Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Ornith-1.0-35B (MoE)** | **75.6%** | 256K | Local Ollama (`--n-cpu-moe`) | **$0.00** | Top coding benchmark, refactoring, large context |
| **Ornith-1.0-9B (Dense)** | **69.4%** | 256K | Local 5.6 GB VRAM (RTX 4060) | **$0.00** | Daily driver, zero offload needed, fast tokens |
| **Gemma 4 26B Instruct** | **68.2%** | 128K | OpenRouter Free Cloud | **$0.00** | Sub-3s response time, zero GPU load |
| **DeepSeek R1 Distill 8B** | **64.1%** | 128K | Local 5.2 GB VRAM | **$0.00** | Chain-of-Thought architecture & deep debugging |
| **Qwen 2.5 Coder 7B** | **62.5%** | 128K | Local 4.7 GB VRAM | **$0.00** | 40+ tok/s high speed autocompletion |

## Agent & Tool Ecosystems Discovered
- **Cursor / Windsurf:** Native IDE agent workflows with indexing and cascade generation.
- **Claude Code:** Terminal agent with multi-file refactoring and subagent capabilities.
- **Cline & Roo Code:** Open-source VS Code extensions supporting local Ollama and OpenRouter Free API endpoints.
- **Aider:** Lightweight Git-native CLI pair programming agent.
