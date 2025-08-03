import streamlit as st
from io import BytesIO
from extract import extract_prescription_fields, generate_filled_card

st.set_page_config(page_title="Prescription → Card", layout="centered")
st.title("📇 Prescription → Filled Card")

presc_file = st.file_uploader("Upload documentation.pdf", type=["pdf"])
tmpl_choice = st.selectbox("Select template:", ["DrThuraya", "DrTaqwa"])

if presc_file:
    file_bytes = presc_file.read()
    fields = extract_prescription_fields(file_bytes)
    st.subheader("Extracted Fields")
    st.json(fields)

    if st.button("Generate Filled Card"):
        tmpl_path = f"templates/{tmpl_choice}_Template.pdf"
        with open(tmpl_path, "rb") as f:
            tmpl_bytes = f.read()
        filled_pdf = generate_filled_card(tmpl_bytes, fields)
        # Clean name for filename (avoid spaces/slashes/etc.)
safe_name = fields.get("patient_name", "Patient").replace(" ", "_").replace("/", "-")
file_no   = fields.get("MRN", "Unknown")
file_name = f"{safe_name}_{file_no}_card.pdf"

st.download_button(
    "Download Filled Card PDF",
    data=filled_pdf,
    file_name=file_name,
    mime="application/pdf"
)

