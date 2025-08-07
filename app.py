import streamlit as st
from io import BytesIO
from extract import extract_prescription_fields, generate_filled_card
import base64

#log-in page section
VALID_USERS = {
    "thuraya.mohammed": "tmm96",
    "taqwa.taha":   "tth48",
    "maria": "m123"
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Doctor Login")
    user = st.text_input("Username")
    pw   = st.text_input("Password", type="password")
    if st.button("Login"):
        if VALID_USERS.get(user) == pw:
            st.session_state.authenticated = True
            st.session_state.user = user
            #st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")
    st.stop()

#main ftn section
st.sidebar.success(f"Logged in as: **{st.session_state.user}**")

def load_logo_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

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

#app config.
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
        text-align: center;
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

# Per-user template options
TEMPLATES = {
    "thuraya.mohammed": ["Dr Thuraya"],
    "taqwa.taha":   ["Dr Taqwa"],
    "maria": ["DrTaqwa"]
}
tmpl_list = TEMPLATES.get(st.session_state.user, [])

presc_file = st.file_uploader("## Upload prescription here: ", type=["pdf"])
#choosing template
tmpl_choice = st.selectbox("## Select your card template:", tmpl_list)

if presc_file and tmpl_choice:
    file_bytes = presc_file.read()
    fields = extract_prescription_fields(file_bytes)

    # Show extracted fields for verification
    #st.subheader("Extracted Fields")
    #st.json(fields)

    if st.button("Generate Filled Card"):
        #mapping label names to actual filenames
        tmpl_map = {
            "Dr Thuraya": "DrThuraya_Template.pdf",
            "Dr Taqwa":   "DrTaqwa_Template.pdf"
        }
        path = f"templates/{tmpl_map[tmpl_choice]}"
        #tmpl_filename = template_map.get(tmpl_choice)
        #tmpl_path = f"templates/{tmpl_filename}"

        with open(path, "rb") as f:
            tmpl_bytes = f.read()

        filled_pdf = generate_filled_card(tmpl_bytes, fields, tmpl_choice)

        #saving filename using patient name and MRN
        safe_name = fields.get("patient_name", "Patient").replace(" ", "_").replace("/", "-")
        file_no = fields.get("MRN", "Unknown")
        file_name = f"{safe_name}_{file_no}_card.pdf"

        st.download_button(
            label="Download Filled Card PDF",
            data=filled_pdf,
            file_name=file_name,
            mime="application/pdf"
        )

logo_base64 = load_logo_base64("logo.png")

st.markdown(
    f"""
    <style>
    .logo-container {{
        position: fixed;
        top: 25px;
        right: 20px;
        z-index: 100;
    }}
    .logo-container img {{
        width: 200px;
        height: auto;
    }}
    </style>
    <div class="logo-container">
        <img src="data:image/png;base64,{logo_base64}" alt="Logo">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .contact-info {
        position: fixed;
        bottom: 20px;
        left: 25px;
        color: white;
        font-size: 14px;
        line-height: 1.6;
        font-family: Helvetica, sans-serif;
        font-weight: normal;
        z-index: 100;
    }
    .contact-info a {
        color: white;
        text-decoration: none;
    }
    .contact-info a:hover {
        text-decoration: underline;
    }
    </style>

    <div class="contact-info">
        📞 <a href="tel:920051919">920051919</a><br>
        📧 <a href="mailto:info@alsalamahospital.com">info@alsalamahospital.com</a><br>
        🌐 <a href="https://www.alsalamahospital.com" target="_blank">alsalamahospital.com</a>
    </div>
    """,
    unsafe_allow_html=True
)
