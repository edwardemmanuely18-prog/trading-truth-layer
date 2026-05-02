from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def build_claim_pdf(schema, metrics):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = [
        Paragraph(f"Claim Report: {schema.name}", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Status: {schema.status}", styles["Normal"]),
        Paragraph(f"Trades: {metrics.get('trade_count', 0)}", styles["Normal"]),
        Paragraph(f"Net PnL: {metrics.get('net_pnl', 0)}", styles["Normal"]),
    ]

    doc.build(elements)
    buffer.seek(0)
    return buffer