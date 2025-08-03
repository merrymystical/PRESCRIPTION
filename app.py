import streamlit as st
from extract import extract_prescription_fields, generate_filled_card

st.title("Prescription → Filled Card")

# 1. Upload prescription PDF
presc_file = st.file_uploader("Upload documentation.pdf", type="pdf")
# 2. Choose template
tmpl_choice = st.selectbox("Template", ["DrThuraya", "DrTaqwa"])
if presc_file:
    bytes_presc = presc_file.read()
    fields = extract_prescription_fields(bytes_presc)
    st.write("Extracted fields:", fields)

    if st.button("Generate Card"):
        # load chosen template
        tmpl_path = f"{tmpl_choice}_Template.pdf"
        with open(tmpl_path, "rb") as f:
            tmpl_bytes = f.read()
        filled_bytes = generate_filled_card(tmpl_bytes, fields)
        st.download_button(
            "Download Filled Card",
            data=filled_bytes,
            file_name="filled_card.pdf",
            mime="application/pdf"
        )
