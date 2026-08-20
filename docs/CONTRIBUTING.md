# Contributing to ResearchOS

## Development Workflow
1. Clone or navigate to the repository: `cd C:\Users\karma\researchos`
2. Install dependencies: `.\scripts\install.ps1`
3. Run test suite: `.\scripts\test.ps1`
4. Follow code guidelines:
   - Ensure all providers implement `BaseSearchProvider` or `BaseAIProvider`.
   - Never bypass `FreePolicyEnforcer`.
   - All external content must pass through `sanitize_untrusted_content()` and `redact_secrets()`.
   - Add unit tests under `tests/unit/` for new connectors or algorithms.
