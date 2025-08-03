import streamlit as st
from io import BytesIO
from extract import extract_prescription_fields, generate_filled_card

# App configuration
st.set_page_config(page_title="Prescription → Card", layout="centered")
st.title("📇 Prescription → Filled Card")

# Upload the prescription PDF
presc_file = st.file_uploader("Upload documentation.pdf", type=["pdf"])

# Choose the doctor template
tmpl_choice = st.selectbox("Select template:", ["DrThuraya", "DrTaqwa"])

if presc_file:
    # Read uploaded file bytes
    file_bytes = presc_file.read()

    # Extract fields from PDF
    fields = extract_prescription_fields(file_bytes)

    # Show extracted fields for verification
    st.subheader("Extracted Fields")
    st.json(fields)

    # Generate card on button click
    if st.button("Generate Filled Card"):
        # Read the selected template PDF
        tmpl_path = f"templates/{tmpl_choice}_Template.pdf"
        with open(tmpl_path, "rb") as f:
            tmpl_bytes = f.read()

        # Generate the filled PDF
        filled_pdf = generate_filled_card(tmpl_bytes, fields)

        # Create a safe filename using patient name and MRN
        safe_name = fields.get("patient_name", "Patient").replace(" ", "_").replace("/", "-")
        file_no = fields.get("MRN", "Unknown")
        file_name = f"{safe_name}_{file_no}_card.pdf"

        # Provide download button
        st.download_button(
            label="Download Filled Card PDF",
            data=filled_pdf,
            file_name=file_name,
            mime="application/pdf"
        )
