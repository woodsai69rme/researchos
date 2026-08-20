# ResearchOS Free-First & Zero-Spend Policy Guide

## Non-Negotiable Principle
Under `FREE_ONLY` mode, actual spending is guaranteed to be **$0.00 AUD**. Paid API execution, metered cloud calls, auto-upgrades, and unknown-cost providers are blocked centrally in the backend security layer.

## Operating Modes Comparison

| Mode | Allowed Providers | Spend Cap | Behavior on Paid API |
| :--- | :--- | :--- | :--- |
| **`FREE_ONLY`** | DuckDuckGo, Google News, OpenRouter Free Models, Ollama, LM Studio, Public Scrapers | **$0.00** | **Throws `FreePolicyViolationError` and aborts call** |
| **`FREE_FIRST`** | Free providers first, paid shown for informational comparison | $0.00 (unless unlocked) | Displays paid alternatives without executing them |
| **`CHEAP`** | Free + low-cost cloud APIs | Configurable budget cap | Executes cheap operations within budget |
| **`LOCAL_ONLY`** | Only localhost endpoints (Ollama, LM Studio, local files) | **$0.00** | Blocks all external cloud AI providers |
| **`FULL`** | All registered providers | Configurable global budget | Unrestricted execution with budget tracking |

## Security Verification
The `FreePolicyEnforcer` runs on every outbound provider request. It is impossible for frontend manipulation to bypass the spend lock because policy checks occur in Python backend execution controllers.
