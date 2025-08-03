import re
import pdfplumber
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pypdf import PdfReader, PdfWriter


def extract_prescription_fields(file_bytes):
    """
    Extract prescription fields from a PDF provided as bytes.
    Returns a dict with keys:
      - patient_name, MRN, Gender, Age, Print Date
      - od_sphere, od_cylinder, od_axis
      - os_sphere, os_cylinder, os_axis
      - add, va_od_sc, va_os_sc
    """
    # Read PDF text
    text_pages = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            text_pages.append(txt)
    full = "\n".join(text_pages)

    def grab(pattern, flags=0):
        m = re.search(pattern, full, flags)
        return m.group(1).strip() if m else ""

    fields = {}
    fields['patient_name'] = grab(r"Patient Name\s*:\s*(.*?)\s*(?:\r?\n|Date Of Birth)")
    fields['MRN']          = grab(r"File No\.\s*:\s*(\d+)")
    fields['Gender']       = grab(r"Sex\s*:\s*(Male|Female|M|F)\b", flags=re.IGNORECASE).capitalize()
    fields['Age']          = grab(r"Age\s*:\s*(\d+Y-\d+M)")
    fields['Print Date']   = grab(r"Print Date\s*:\s*(\d{2}/\d{2}/\d{4})")

    # OD/OS refraction
    od = re.search(r"OD\s*:\s*([+\-\d\.]+)\s*/\s*([+\-\d\.]+)\s*X\s*(\d+)", full)
    os_ = re.search(r"OS\s*:\s*([+\-\d\.]+)\s*/\s*([+\-\d\.]+)\s*X\s*(\d+)", full)
    if od:
        fields['od_sphere'], fields['od_cylinder'], fields['od_axis'] = od.groups()
    else:
        fields['od_sphere'] = fields['od_cylinder'] = fields['od_axis'] = ""
    if os_:
        fields['os_sphere'], fields['os_cylinder'], fields['os_axis'] = os_.groups()
    else:
        fields['os_sphere'] = fields['os_cylinder'] = fields['os_axis'] = ""

    # ADD and VA
    fields['add']      = grab(r"ADD\s*:\s*([+\-\d\.]+\s*D)")
    # Visual Acuity — Sc (Va (sc) OD & OS)
    od_sc = re.search(r"Va\s*\(sc\s*\)\s*OD:\s*([\d\/\+\-]+)", full, re.IGNORECASE)
    os_sc = re.search(r"Va\s*\(sc\s*\)[\s\S]*?OS:\s*([\d\/\+\-]+)", full, re.IGNORECASE)
    fields['va_od_sc'] = od_sc.group(1) if od_sc else ""
    fields['va_os_sc'] = os_sc.group(1) if os_sc else ""

    return fields


def generate_filled_card(template_bytes, fields):
    """
    Overlay prescription fields onto the two-page template PDF (as bytes), returning the merged PDF bytes.
    """
    reader = PdfReader(BytesIO(template_bytes))
    w = float(reader.pages[0].mediabox.width)
    h = float(reader.pages[0].mediabox.height)

    # Create overlay PDF in memory
    overlay_buf = BytesIO()
    c = canvas.Canvas(overlay_buf, pagesize=(w, h))
    # Front side
    c.setFont("Helvetica-Bold", 8)
    c.drawString(90, 70, fields.get('patient_name', ''))
    c.drawString(90, 60, fields.get('MRN', ''))
    c.drawString(90, 50, fields.get('Gender', ''))
    c.drawString(90, 40, fields.get('Age', ''))
    c.showPage()
    # Back side
    c.setFont("Helvetica-Bold", 6)
    c.drawString(45, 85, fields.get('od_sphere', ''))
    c.drawString(77, 85, fields.get('od_cylinder', ''))
    c.drawString(115, 85, fields.get('od_axis', ''))
    c.drawString(45, 75, fields.get('os_sphere', ''))
    c.drawString(77, 75, fields.get('os_cylinder', ''))
    c.drawString(115, 75, fields.get('os_axis', ''))
    c.drawString(132, 85, fields.get('va_od_sc', ''))
    c.drawString(132, 75, fields.get('va_os_sc', ''))
    c.drawString(153, 85, fields.get('add', ''))
    c.drawString(153, 75, fields.get('add', ''))
    c.drawString(177, 18, fields.get('Print Date', ''))
    c.save()
    overlay_buf.seek(0)

    # Merge and output
    overlay_pdf = PdfReader(overlay_buf)
    writer = PdfWriter()
    for idx, page in enumerate(reader.pages):
        page.merge_page(overlay_pdf.pages[idx])
        writer.add_page(page)
    out_buf = BytesIO()
    writer.write(out_buf)
    return out_buf.getvalue()
