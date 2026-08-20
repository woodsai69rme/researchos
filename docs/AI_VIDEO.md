# ResearchOS AI Video & Music Video Cost Calculator

## Video Generation Cost Matrix (Music Video: ~3.5 minutes = 42-46 clips)

| Generator | Free Tier Allowance | Resolution & Quality | Cost / Clip | Cost / Min | Est. Music Video Total |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Wan 2.2 Mega (Local ComfyUI)** | **Unlimited Local Generations** | 512x512 / 720p (4-step Lightning) | **$0.00 AUD** | **$0.00 AUD** | **$0.00 AUD (100% Free)** |
| **Kling AI (Kuaishou)** | 66 credits daily (~180 clips/mo) | 720p / 1080p | $0.23 AUD | $2.76 AUD | $10.58 AUD |
| **Minimax Hailuo AI** | 5 daily generations (~150 clips/mo) | 720p | $0.31 AUD | $3.10 AUD | $14.26 AUD |
| **Google Veo (Vertex AI)** | 3 daily free generations | 1080p | $0.54 AUD | $5.40 AUD | $24.84 AUD |
| **Runway Gen-3 Alpha** | 25 clips one-time trial | 720p / 1080p | $0.77 AUD | $4.62 AUD | $35.42 AUD |
| **Luma Dream Machine** | 30 clips/mo (watermarked) | 720p | $0.92 AUD | $11.04 AUD | $42.32 AUD |

## Best Practices for RTX 4060 8GB VRAM
- Use Wan 2.2 TI2V-5B checkpoint with GGUF Q4 quantization.
- Add `--lowvram --force-fp16` startup flags in ComfyUI.
- Utilize 4-step Lightning scheduler for 150s generation time at 512x512 resolution.
