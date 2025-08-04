import streamlit as st
from io import BytesIO
from extract import extract_prescription_fields, generate_filled_card

# App configuration
st.set_page_config(page_title="Prescription → Card", layout="centered")
st.markdown(
    """
    <style>
    /* Title */
    .stApp h1 {
        color: black !important;
    }

    /* File uploader and selectbox labels */
    label, .stMarkdown, .css-17eq0hr {
        font-weight: bold !important;
        color: black !important;
        font-size: 19px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <style>
    .stApp {
        #background-image: url("https://alsalamahospital.com/wp-content/uploads/2024/04/DSC_5555-1-1-1-1.jpg");
        background-image: url("https://media.licdn.com/dms/image/v2/D4D22AQHdEsYAb7Lkhw/feedshare-shrink_800/feedshare-shrink_800/0/1705580533339?e=1756944000&v=beta&t=zuX1L2vYlddscLLBr4FSzSOp2n4ZW877Oh-grS0uSRc");
        background-size: cover;
        background-position: up;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.title("PRESCRIPTION PDF TO CARD")

# Upload the prescription PDF
presc_file = st.file_uploader("#### Upload prescription here: ", type=["pdf"])

# Choose the doctor template
tmpl_choice = st.selectbox("Select examiner card template:", ["Dr Thuraya", "Dr Taqwa"])

# Styled heading for uploader
#st.markdown("### Upload Prescription Here")
#presc_file = st.file_uploader("", type=["pdf"])

# Styled heading for template selector
#st.markdown("### Select Examiner Card Template")
#tmpl_choice = st.selectbox("", ["Dr Thuraya", "Dr Taqwa"])


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
