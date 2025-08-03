import re, pdfplumber
from io import BytesIO
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

def extract_prescription_fields(file_bytes):
    full = "\n".join(
        page.extract_text() or "" for page in pdfplumber.open(BytesIO(file_bytes)).pages
    )
    def grab(pattern, flags=0):
        m = re.search(pattern, full, flags)
        return m.group(1).strip() if m else ""
    fields = {
        'patient_name': grab(r"Patient Name\s*:\s*(.*?)\s*(?:\r?\n|Date Of Birth)"),
        'MRN'         : grab(r"File No\.\s*:\s*(\d+)"),
        'Gender'      : grab(r"Sex\s*:\s*(Male|Female|M|F)"),
        'age'         : grab(r"Age\s*:\s*(\d+Y-\d+M)"),
        'od_sphere'   : grab(r"Subjective\s*\(dry\)\s*OD\s*:\s*([+\-\d\.]+)"),
        'od_cylinder' : grab(r"Subjective\s*\(dry\)\s*OD\s*:.*?/\s*([+\-\d\.]+)"),
        'od_axis'     : grab(r"Subjective\s*\(dry\)\s*OD\s*:.*?X\s*(\d+)"),
        'os_sphere'   : grab(r"Subjective\s*\(dry\)\s*OS\s*:\s*([+\-\d\.]+)"),
        'os_cylinder' : grab(r"Subjective\s*\(dry\)\s*OS\s*:.*?/\s*([+\-\d\.]+)"),
        'os_axis'     : grab(r"Subjective\s*\(dry\)\s*OS\s*:.*?X\s*(\d+)"),
        'add'         : grab(r"ADD\s*:\s*([+\-\d\.]+\s*D)"),
        'va_od_sc'    : grab(r"Va\s*\(sc\)\s*OD\s*:\s*([\d\/\+\-]+)", flags=re.IGNORECASE),
        'va_os_sc'    : grab(r"Va\s*\(sc\)\s*OS\s*:\s*([\d\/\+\-]+)", flags=re.IGNORECASE),
    }
    return fields

def generate_filled_card(template_bytes, fields):
    # read template for size
    reader = PdfReader(BytesIO(template_bytes))
    w = float(reader.pages[0].mediabox.width)
    h = float(reader.pages[0].mediabox.height)

    # overlay
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(w, h))
    c.setFont("Helvetica", 10)
    # front page example coordinates:
    c.drawString(100, h-100, fields.get('patient_name',''))
    c.drawString(400, h-100, fields.get('age',''))
    c.showPage()
    # back page:
    c.drawString(100, h-100, fields.get('od_sphere',''))
    # … add the rest …
    c.save()
    packet.seek(0)

    # merge
    overlay = PdfReader(packet)
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        page.merge_page(overlay.pages[i])
        writer.add_page(page)
    out = BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue()
