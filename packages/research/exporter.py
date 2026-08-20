"""
ResearchOS Multi-Format Report Exporter
Generates Markdown, HTML, CSV, and JSON exports of research reports
"""
import json
import csv
import io
from pathlib import Path
from typing import Dict, Any
from researchos.packages.core.schemas import FinalResearchReport


class ReportExporter:
    def __init__(self, output_dir: Path = Path("reports")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_to_markdown(self, report: FinalResearchReport, filename: str = None) -> str:
        filename = filename or f"ResearchOS_Report_{report.report_id}.md"
        filepath = self.output_dir / filename

        md = [
            f"# ResearchOS Deep Research Report",
            f"**Report ID:** `{report.report_id}` | **Date:** {report.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
            f"**Actual Spend:** `${report.actual_spend_aud:.2f} AUD` | **Confidence Score:** `{int(report.confidence_score * 100)}%`\n",
            f"---",
            f"## 📋 Executive Summary\n",
            report.executive_summary,
            f"\n### 🎯 Bottom Line Recommendation\n",
            report.bottom_line,
            f"\n---",
            f"## 🏆 Top Recommended Options\n",
        ]

        for opt in report.best_options:
            md.append(f"### {opt.get('title')}")
            md.append(f"- **Price:** {opt.get('price_aud', 'N/A')}")
            md.append(f"- **Summary:** {opt.get('pros_summary', 'N/A')}\n")

        if report.marketplace_results:
            md.append(f"\n---")
            md.append(f"## 🛒 Australian Marketplace Deals & Deal Scores\n")
            md.append(f"| Item | Price (AUD) | Deal Score | Source | Location | Warranty |")
            md.append(f"| :--- | :--- | :--- | :--- | :--- | :--- |")
            for item in report.marketplace_results:
                md.append(f"| [{item.title[:40]}]({item.url}) | ${item.price_aud:.2f} | **{item.deal_score}/100** | {item.source_platform} | {item.location} | {item.warranty_months} mo |")

        if report.business_results:
            md.append(f"\n---")
            md.append(f"## 🔧 Local Queensland Workshops & Specialists\n")
            for b in report.business_results:
                md.append(f"### {b.name}")
                md.append(f"- **Location:** {b.suburb_or_city}, {b.state}")
                md.append(f"- **Phone:** {b.phone or 'Contact via Web'}")
                md.append(f"- **Specialization Proof:** {b.specialization_proof}")
                md.append(f"- **Website:** [{b.website or 'Directory Listing'}]({b.website or '#'})\n")

        if report.claims:
            md.append(f"\n---")
            md.append(f"## 🔍 Extracted Facts & Evidence\n")
            for c in report.claims:
                status_str = c.status.value if hasattr(c.status, "value") else str(c.status)
                md.append(f"- **{c.claim_text}** `[{status_str.upper()}]` (Confidence: {int(c.confidence * 100)}%)")

        if report.what_you_missed:
            md.append(f"\n---")
            md.append(f"## 💡 What Did You Miss? (Unsearched Adjacent Angles)\n")
            for m in report.what_you_missed:
                md.append(f"- {m}")

        content = "\n".join(md)
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)

    def export_to_json(self, report: FinalResearchReport, filename: str = None) -> str:
        filename = filename or f"ResearchOS_Report_{report.report_id}.json"
        filepath = self.output_dir / filename
        filepath.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        return str(filepath)

    def export_to_csv(self, report: FinalResearchReport, filename: str = None) -> str:
        filename = filename or f"ResearchOS_Deals_{report.report_id}.csv"
        filepath = self.output_dir / filename

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Price_AUD", "Deal_Score", "Source_Platform", "Condition", "Warranty_Months", "Location", "URL"])
            for item in report.marketplace_results:
                writer.writerow([
                    item.title,
                    item.price_aud,
                    item.deal_score,
                    item.source_platform,
                    item.condition.value if hasattr(item.condition, "value") else str(item.condition),
                    item.warranty_months,
                    item.location,
                    item.url,
                ])
        return str(filepath)


report_exporter = ReportExporter()
