# ResearchOS Developer Specification & Data Contracts

## Core Schemas (`packages/core/schemas.py`)

### 1. `ResearchPlan`
- `plan_id`: Unique run identifier (UUID)
- `original_query`: Raw user string
- `domain_category`: `automotive`, `ai_coding`, `ai_video`, `electronics_deals`, `general`
- `search_queries`: Expanded list of synonyms and regional phrases
- `free_only`: Boolean spend restriction

### 2. `FinalResearchReport`
- `report_id`: Unique report ID
- `actual_spend_aud`: Verified financial spend incurred ($0.00 in `FREE_ONLY`)
- `executive_summary`: Concise findings
- `bottom_line`: Final actionable advice
- `best_options`, `free_options`, `cheap_options`: Categorized recommendations
- `what_you_missed`: Unsearched adjacent topics
- `marketplace_results`: Scored listings (`deal_score: 0-100`)
- `business_results`: Local Australian workshops & proof of specialization
- `claims` & `contradictions`: Extracted facts and resolved disputes
- `confidence_score`: 0.0 - 1.0 credibility rating
