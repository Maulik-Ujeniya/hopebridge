import io
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404

from donations.models import Donation

# Safely import reportlab
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


@login_required
def view_invoice(request, donation_id):
    """HTML preview of invoice with print button."""
    try:
        if request.user.is_staff:
            donation = get_object_or_404(Donation, id=donation_id)
        else:
            donation = get_object_or_404(Donation, id=donation_id, donor=request.user)
    except Http404:
        donation = get_object_or_404(Donation, id=donation_id)
        if donation.email != request.user.email:
            raise Http404("You do not have permission to view this invoice.")

    return render(request, 'invoices/invoice_detail.html', {'donation': donation})


def download_invoice(request, donation_id):
    """Download invoice as generated PDF."""
    try:
        if request.user.is_authenticated and request.user.is_staff:
            donation = get_object_or_404(Donation, id=donation_id)
        elif request.user.is_authenticated:
            donation = get_object_or_404(Donation, id=donation_id, donor=request.user)
        else:
            donation = get_object_or_404(Donation, id=donation_id)
    except Http404:
        raise Http404("Invoice not found or access denied.")

    buffer = generate_invoice_pdf_buffer(donation)
    if not buffer:
        # Fallback to HTML print if ReportLab is not installed
        return render(request, 'invoices/invoice_detail.html', {'donation': donation})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="HopeBridge_Invoice_{donation.invoice_number}.pdf"'
    response.write(buffer.getvalue())
    buffer.close()

    return response


def generate_invoice_pdf_buffer(donation):
    """Generates a PDF invoice using ReportLab and returns a BytesIO buffer."""
    if not HAS_REPORTLAB:
        return None

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#6C63FF'),
        spaceAfter=15
    )

    header_style = ParagraphStyle(
        'InvoiceHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#1F2937'),
        leading=14
    )

    text_style = ParagraphStyle(
        'InvoiceText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#4B5563'),
        leading=14
    )

    bold_text_style = ParagraphStyle(
        'InvoiceBoldText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#1F2937'),
        leading=14
    )

    ngo_info = """<b>HopeBridge NGO</b><br/>
    Rajkot, Gujarat, India - 360001<br/>
    Email: contact@hopebridge.org<br/>
    Phone: +91 98765 43210<br/>
    Reg No: HB-NGO-2026-GJ<br/>
    PAN Number: AABCD1234E<br/>
    80G Reg No: 80G/HB/2026
    """

    invoice_info = f"""<b>DONATION RECEIPT</b><br/>
    <b>Invoice No:</b> {donation.invoice_number}<br/>
    <b>Date:</b> {donation.date_donated.strftime('%d %b %Y %I:%M %p')}<br/>
    <b>Status:</b> {donation.payment_status.upper()}<br/>
    <b>Payment Method:</b> {donation.get_payment_method_display()}
    """

    header_data = [
        [Paragraph(ngo_info, text_style), Paragraph(invoice_info, text_style)]
    ]

    header_table = Table(header_data, colWidths=[270, 270])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 20))

    line_data = [['']]
    line_table = Table(line_data, colWidths=[540], rowHeights=[2])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#6C63FF')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 20))

    donor_title = "<b>DONOR DETAILS</b>"
    story.append(Paragraph(donor_title, header_style))
    story.append(Spacer(1, 5))

    donor_details = f"""<b>Name:</b> {donation.name}<br/>
    <b>Email:</b> {donation.email}<br/>
    <b>Phone:</b> {donation.phone}<br/>
    <b>Address:</b> {donation.full_address or 'N/A'}, {donation.city or ''}, {donation.country or ''} - {donation.pincode or ''}
    """
    story.append(Paragraph(donor_details, text_style))
    story.append(Spacer(1, 20))

    table_data = [
        [
            Paragraph("<b>Donation Type</b>", bold_text_style),
            Paragraph("<b>Quantity / Details</b>", bold_text_style),
            Paragraph("<b>Transaction ID</b>", bold_text_style),
            Paragraph("<b>Amount</b>", bold_text_style)
        ],
        [
            Paragraph(donation.get_donation_type_display(), text_style),
            Paragraph(f"{donation.quantity or 'N/A'}", text_style),
            Paragraph(donation.transaction_id or 'N/A', text_style),
            Paragraph(f"INR {donation.amount:,.2f}", bold_text_style)
        ]
    ]

    details_table = Table(table_data, colWidths=[135, 135, 135, 135])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F3F8')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#1F2937')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E6EF')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 30))

    total_data = [
        [Paragraph("<b>TOTAL RECEIVED</b>", bold_text_style), Paragraph(f"<b>INR {donation.amount:,.2f}</b>", ParagraphStyle('TotalText', parent=title_style, fontSize=16, leading=18, spaceAfter=0))]
    ]
    total_table = Table(total_data, colWidths=[380, 160])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8F9FC')),
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor('#6C63FF')),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 40))

    thank_you_text = """Thank you for your generous support! Your contribution makes a direct difference in our ongoing drives for food, healthcare, and education.<br/>
    <i>This is a computer-generated receipt. Valid for tax exemption under section 80G of Income Tax Act. Authorized electronically by HopeBridge Finance Dept.</i>
    """
    story.append(Paragraph(thank_you_text, ParagraphStyle('ThankYou', parent=text_style, alignment=1)))

    doc.build(story)
    return buffer
