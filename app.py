import streamlit as st
from io import BytesIO
from extract import extract_prescription_fields, generate_filled_card
import base64

def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: top left;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# App configuration
st.set_page_config(page_title="Prescription → Card", layout="centered")
set_background("bg2.jpg")
st.markdown(
    """
    <style>
    /* Title */
    .stApp h1 {
        color: #1b263b !important;
        #color: white !important;
        font-position: center;
        text-align: left;
    }

    /* File uploader and selectbox labels */
    label, .stMarkdown, .css-17eq0hr {
        font-weight: bold !important;
        #color: #1b263b !important;
        color: black !important;
        font-size: 28px !important;
        text-align: left !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("PRESCRIPTION PDF TO CARD")

# Upload the prescription PDF
presc_file = st.file_uploader("## Upload prescription here: ", type=["pdf"])

# Choose the doctor template
tmpl_choice = st.selectbox("## Select examiner card template: ", ["Dr Thuraya", "Dr Taqwa"])

if presc_file:
    # Read uploaded file bytes
    file_bytes = presc_file.read()

    # Extract fields from PDF
    fields = extract_prescription_fields(file_bytes)

    # Show extracted fields for verification
    #st.subheader("Extracted Fields")
    #st.json(fields)

    # Generate card on button click
    if st.button("Generate Filled Card"):
        # Map label names to actual filenames
        template_map = {
            "Dr Thuraya": "DrThuraya_Template.pdf",
            "Dr Taqwa": "DrTaqwa_Template.pdf"
        }
        tmpl_filename = template_map.get(tmpl_choice)
        tmpl_path = f"templates/{tmpl_filename}"

        # Read the selected template PDF
        with open(tmpl_path, "rb") as f:
            tmpl_bytes = f.read()

        # Generate the filled PDF
        filled_pdf = generate_filled_card(tmpl_bytes, fields, tmpl_choice)

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
        # Add floating logo and contact info
st.markdown(
    """
    <style>
    /* Bottom-right logo */
    .logo-container {
        position: fixed;
        bottom: 15px;
        right: 20px;
        z-index: 100;
    }

    .logo-container img {
        height: 60px;  /* Adjust logo size here */
        opacity: 0.8;
    }

    /* Bottom-left contact info */
    .contact-info {
        position: fixed;
        bottom: 15px;
        left: 20px;
        color: white;
        background-color: rgba(0,0,0,0.5);
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
        z-index: 100;
    }
    </style>

    <div class="logo-container">
        <img src="logo.png" alt="Logo">
    </div>

    <div class="contact-info">
        Al Salama Hospital<br>
        Email: info@alsalama.com
    </div>
    """,
    unsafe_allow_html=True
)
