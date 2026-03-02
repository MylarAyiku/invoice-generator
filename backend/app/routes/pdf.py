from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Invoice
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
import io

router = APIRouter()

@router.get("/{invoice_id}")
def download_pdf(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    right_align = ParagraphStyle('right', alignment=TA_RIGHT, parent=styles['Normal'])
    story = []

    # Header
    story.append(Paragraph(f"<b>INVOICE</b>", styles['Title']))
    story.append(Paragraph(f"Invoice #: {invoice.invoice_number}", styles['Normal']))
    story.append(Paragraph(f"Date: {invoice.created_at.strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 10*mm))

    # From / To
    from_to_data = [
        [Paragraph("<b>From:</b>", styles['Normal']), Paragraph("<b>To:</b>", styles['Normal'])],
        [invoice.sender_name, invoice.client_name],
        [invoice.sender_email, invoice.client_email],
        [invoice.sender_address, invoice.client_address],
    ]
    from_to_table = Table(from_to_data, colWidths=[85*mm, 85*mm])
    from_to_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(from_to_table)
    story.append(Spacer(1, 10*mm))

    # Items table
    item_data = [["Description", "Qty", "Unit Price", "Amount"]]
    for item in invoice.items:
        amount = item['quantity'] * item['unit_price']
        item_data.append([
            item['description'],
            str(item['quantity']),
            f"${item['unit_price']:.2f}",
            f"${amount:.2f}"
        ])

    item_data.append(["", "", "Subtotal", f"${invoice.subtotal:.2f}"])
    if invoice.tax_rate > 0:
        item_data.append(["", "", f"Tax ({invoice.tax_rate}%)", f"${invoice.tax_amount:.2f}"])
    item_data.append(["", "", Paragraph("<b>Total</b>", styles['Normal']), Paragraph(f"<b>${invoice.total:.2f}</b>", styles['Normal'])])

    items_table = Table(item_data, colWidths=[90*mm, 20*mm, 35*mm, 30*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-4), [colors.HexColor('#f8fafc'), colors.white]),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor('#2563eb')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(items_table)

    # Notes
    if invoice.notes:
        story.append(Spacer(1, 10*mm))
        story.append(Paragraph("<b>Notes:</b>", styles['Normal']))
        story.append(Paragraph(invoice.notes, styles['Normal']))

    doc.build(story)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={invoice.invoice_number}.pdf"}
    )