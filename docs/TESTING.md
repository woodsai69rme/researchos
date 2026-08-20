# ResearchOS Test Suite & Verification Guide

## Test Architecture
ResearchOS includes comprehensive unit, integration, security, and policy tests located in `tests/`:

- `tests/unit/test_policy.py`: Verifies $0.00 spend guarantee in `FREE_ONLY` mode and blocking of unauthorized cloud calls in `LOCAL_ONLY` mode.
- `tests/unit/test_dedup.py`: Verifies URL canonicalization and identification of syndicated press releases.
- `tests/unit/test_claims.py`: Verifies claim extraction and detection of price/quota contradictions.
- `tests/unit/test_deal_scorer.py`: Verifies Deal Score algorithm (0-100) and pricing discount calculations.
- `tests/unit/test_automotive.py`: Verifies Ford Barra 1,000hp TH400 conversion component requirements and workshop discovery.
- `tests/unit/test_security.py`: Verifies SSRF protection on private/metadata IPs, prompt injection sanitization, and secret redaction.
- `tests/integration/test_api_flow.py`: Verifies end-to-end FastAPI endpoints, models catalog, video cost calculations, and research execution flow.

## Running Tests
```powershell
.\scripts\test.ps1
```
Or via pytest:
```powershell
$env:PYTHONPATH="C:\Users\karma"; python -m pytest -c pytest.ini tests\ -v
```
