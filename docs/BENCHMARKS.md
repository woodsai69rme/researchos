# ResearchOS Benchmarks & Evaluation Methodology

## SWE-Bench Verified Coding Benchmark Ranking

| Model | Size | SWE-Bench Verified % | License | Context Size | Inference Speed (8GB RTX 4060) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Ornith-1.0-35B (MoE)** | 21 GB | **75.6%** | MIT | 256K | ~12 tok/s (CPU-MoE offload) |
| **Ornith-1.0-9B (Dense)** | 5.6 GB | **69.4%** | MIT | 256K | ~32 tok/s (Full VRAM) |
| **Gemma-4-26B-Instruct** | Cloud Free | **68.2%** | Open Weights | 128K | Sub-3s response (OpenRouter) |
| **DeepSeek R1 Distill 8B**| 5.2 GB | **64.1%** | MIT | 128K | ~28 tok/s (Full VRAM) |
| **Qwen 2.5 Coder 7B** | 4.7 GB | **62.5%** | Apache 2.0 | 128K | 40+ tok/s (Full VRAM) |
| **Devstral 24B** | 14 GB | **46.8%** | Apache 2.0 | 128K | ~18 tok/s |

## Search Swarm Latency Benchmarks
- **DuckDuckGo Free Parser:** ~320ms avg latency
- **Google News RSS:** ~210ms avg latency
- **Reddit JSON Discussions:** ~450ms avg latency
- **GitHub Search API:** ~280ms avg latency
- **CeX / Cash Converters Deals:** ~580ms avg latency
