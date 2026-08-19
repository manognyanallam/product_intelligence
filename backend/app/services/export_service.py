"""
Export Service — Generates JSON and PDF exports of product intelligence.

Reference: architecture_final.md §8.2 (Export Endpoints)
"""
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem,
)

from app.schemas.response import ProductResponse


class ExportService:
    """
    Service for exporting product intelligence as PDF files.
    """

    async def generate_pdf(self, product: ProductResponse) -> bytes:
        """
        Generate a professional PDF report for a product.

        The PDF includes:
        - Header with product title and MPN
        - Overall confidence score
        - Specifications table
        - Features and applications
        - SEO keywords
        - Validation report
        - Source attributions
        - Footer with timestamp

        Args:
            product: The product intelligence data to export.

        Returns:
            bytes: PDF file content.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch,
            title=f"Product Intelligence Report — {product.enriched_data.mpn}",
            author="AI Product Intelligence Platform",
        )

        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        heading_style = styles["Heading2"]
        body_style = ParagraphStyle(
            "BodyCompact",
            parent=styles["BodyText"],
            spaceAfter=6,
        )
        small_style = ParagraphStyle(
            "SmallMuted",
            parent=styles["BodyText"],
            fontSize=9,
            textColor=colors.grey,
        )

        story = []
        enriched = product.enriched_data

        # --- Header ---------------------------------------------------------
        story.append(Paragraph("AI Product Intelligence Report", title_style))
        story.append(Spacer(1, 6))
        story.append(
            Paragraph(
                f"<b>Product:</b> {enriched.title or enriched.mpn}<br/>"
                f"<b>MPN:</b> {enriched.mpn} &nbsp;|&nbsp; "
                f"<b>Brand:</b> {enriched.brand} &nbsp;|&nbsp; "
                f"<b>Category:</b> {enriched.category or 'N/A'}"
            )
        )
        story.append(Spacer(1, 12))

        # --- Confidence -------------------------------------------------------
        overall = product.confidence.overall
        story.append(Paragraph(f"Overall Confidence: {overall * 100:.0f}%", heading_style))
        story.append(Spacer(1, 8))

        # --- Specifications Table ----------------------------------------------
        story.append(Paragraph("Specifications", heading_style))
        spec_rows = [["Attribute", "Value", "Confidence"]]
        for attr, value in enriched.specifications.items():
            conf = product.confidence.attributes.get(attr, 0.0)
            spec_rows.append([attr, str(value), f"{conf * 100:.0f}%"])
        spec_table = Table(spec_rows, colWidths=[2.2 * inch, 3.0 * inch, 1.2 * inch])
        spec_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565c0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(spec_table)
        story.append(Spacer(1, 12))

        # --- Description ------------------------------------------------------
        story.append(Paragraph("Description", heading_style))
        story.append(Paragraph(enriched.long_description or enriched.description, body_style))
        story.append(Spacer(1, 12))

        # --- Features ---------------------------------------------------------
        if enriched.features:
            story.append(Paragraph("Features", heading_style))
            story.append(ListFlowable(
                [ListItem(Paragraph(f, body_style)) for f in enriched.features],
                bulletType="bullet",
            ))
            story.append(Spacer(1, 12))

        # --- Applications -----------------------------------------------------
        if enriched.applications:
            story.append(Paragraph("Applications", heading_style))
            story.append(ListFlowable(
                [ListItem(Paragraph(a, body_style)) for a in enriched.applications],
                bulletType="bullet",
            ))
            story.append(Spacer(1, 12))

        # --- SEO Keywords -----------------------------------------------------
        if enriched.seo_keywords:
            story.append(Paragraph("SEO Keywords", heading_style))
            story.append(Paragraph(", ".join(f"#{k}" for k in enriched.seo_keywords), body_style))
            story.append(Spacer(1, 12))

        # --- Validation Report --------------------------------------------------
        story.append(Paragraph("Validation Report", heading_style))
        for check in product.validation.checks:
            icon = {
                "verified": "✓",
                "partial": "⚠",
                "unverified": "✗",
                "contradicted": "✗",
            }.get(check.status, "•")
            story.append(
                Paragraph(
                    f"{icon} <b>{check.attribute}</b>: {check.status.capitalize()} — {check.message}",
                    body_style,
                )
            )
        if product.validation.issues:
            story.append(Spacer(1, 6))
            for issue in product.validation.issues:
                story.append(Paragraph(f"⚠ {issue}", small_style))
        story.append(Spacer(1, 12))

        # --- Sources ------------------------------------------------------------
        story.append(Paragraph("Sources", heading_style))
        for source in product.sources:
            story.append(
                Paragraph(
                    f"• <b>{source.name}</b> "
                    f"(relevance: {source.relevance_score * 100:.0f}%) — {source.type}",
                    body_style,
                )
            )
        story.append(Spacer(1, 16))

        # --- Footer ---------------------------------------------------------------
        story.append(
            Paragraph(
                f"Generated by AI Product Intelligence Platform | Product ID: {product.product_id} | "
                f"Created: {product.created_at}",
                small_style,
            )
        )

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

