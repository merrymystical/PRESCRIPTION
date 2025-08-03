import streamlit as st
from extract import extract_prescription_fields, generate_filled_card

st.title("Prescription → Filled Card")

presc_file = st.file_uploader("Upload documentation.pdf", type="pdf")
tmpl_choice = st.selectbox("Template", ["DrThuraya", "DrTaqwa"])

if presc_file:
    bytes_presc = presc_file.read()
    fields = extract_prescription_fields(bytes_presc)
    st.write("Extracted fields:", fields)

    if st.button("Generate Card"):
        with open(f"templates/{tmpl_choice}_Template.pdf", "rb") as f:
            tmpl_bytes = f.read()
        filled = generate_filled_card(tmpl_bytes, fields)
        st.download_button(
            "Download Filled Card",
            data=filled,
            file_name="filled_card.pdf",
            mime="application/pdf"
        )
