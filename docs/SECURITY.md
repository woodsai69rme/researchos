# ResearchOS Security & Threat Mitigation Architecture

## 1. Zero-Spend & Budget Locking
The `FreePolicyEnforcer` acts as a central gatekeeper for all outbound network and model requests. In `FREE_ONLY` mode, any operation that incurs financial cost is blocked with a `FreePolicyViolationError`.

## 2. SSRF (Server-Side Request Forgery) Protection
The `validate_outbound_url` function intercepts all scraper and webhook URLs, validating them against blocked networks:
- RFC 1918 private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)
- Cloud metadata endpoints (`169.254.169.254`)
- Loopback addresses (`127.0.0.0/8`, `::1`)

## 3. Prompt Injection Neutralization
All external web and document text is treated as **Untrusted External Data**.
- Hostile override directives (e.g. "Ignore previous instructions", "Reveal API keys") are sanitized via `sanitize_untrusted_content()`.
- Data is safely enclosed in inert XML blocks (`<UNTRUSTED_EXTERNAL_DATA>`) before being passed to reasoning models.

## 4. Secret Redaction
All API keys (`sk-or-v1-...`, `AIzaSy...`, `ghp_...`, Bearer tokens) are masked in logging and report outputs via `redact_secrets()`.
