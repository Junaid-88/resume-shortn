import io
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception:
        return ""

def create_pdf_from_text(text):
    """Create a single-page, modern-styled resume PDF from text."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,  # 0.5 inch
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    # Define styles
    styles = getSampleStyleSheet()
    name_style = ParagraphStyle(
        'Name',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=8,
        textColor='#222222'
    )
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor='#003366',
        spaceBefore=10,
        spaceAfter=4,
        alignment=TA_LEFT,
        uppercase=True
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        spaceAfter=2,
        alignment=TA_LEFT,
        textColor='#222222'
    )
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=12,
        bulletIndent=0,
        bulletFontName='Helvetica-Bold',
        bulletFontSize=9,
    )

    story = []
    lines = text.split('\n')
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 4))
            continue
        # Name (first line)
        if idx == 0:
            story.append(Paragraph(line, name_style))
        # Section headers (all caps, not too short)
        elif line.isupper() and len(line) > 3:
            story.append(Paragraph(line, header_style))
        # Bullet points
        elif line.startswith('•') or line.startswith('-'):
            story.append(Paragraph(line, bullet_style, bulletText='•'))
        else:
            story.append(Paragraph(line, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
