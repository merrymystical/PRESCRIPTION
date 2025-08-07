import streamlit as st
from io import BytesIO
from extract import extract_prescription_fields, generate_filled_card
import base64

# ——————————————————————————————
# Utility functions for background & logo
# ——————————————————————————————
def load_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_background(image_path):
    b64 = load_base64(image_path)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{b64}");
            background-size: cover;
            background-position: top left;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def inject_logo_and_contact():
    logo_b64 = load_base64("logo.png")
    st.markdown(
        f"""
        <style>
        .logo-container {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 100;
        }}
        .logo-container img {{
            width: 120px;
            height: auto;
        }}
        .contact-info {{
            position: fixed;
            bottom: 15px;
            left: 20px;
            color: white;
            font-size: 14px;
            line-height: 1.6;
            font-family: Helvetica, sans-serif;
            font-weight: normal;
            z-index: 100;
        }}
        .contact-info a {{
            color: white;
            text-decoration: none;
        }}
        .contact-info a:hover {{
            text-decoration: underline;
        }}
        </style>

        <div class="logo-container">
            <img src="data:image/png;base64,{logo_b64}" alt="Logo">
        </div>
        <div class="contact-info">
            📞 <a href="tel:920051919">920051919</a><br>
            📧 <a href="mailto:info@alsalamahospital.com">info@alsalamahospital.com</a><br>
            🌐 <a href="https://www.alsalamahospital.com" target="_blank">alsalamahospital.com</a>
        </div>
        """,
        unsafe_allow_html=True
    )

# ——————————————————————————————
# 1) Page config + Background + Logo/Footer
# ——————————————————————————————
st.set_page_config(page_title="Prescription → Card", layout="centered")
set_background("bg2.jpg")
inject_logo_and_contact()

# ——————————————————————————————
# 2) Authentication (Phase 1)
# ——————————————————————————————
VALID_USERS = {
    "thuraya.mohammed": "tmm96",
    "taqwa.taha":       "tth48",
    "maria":            "m123"
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
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")
    st.stop()

# ——————————————————————————————
# 3) Main App (post-login)
# ——————————————————————————————
st.sidebar.success(f"Logged in as: **{st.session_state.user}**")

st.title("📇 PRESCRIPTION PDF TO CARD")

TEMPLATES = {
    "thuraya.mohammed": ["Dr Thuraya"],
    "taqwa.taha":       ["Dr Taqwa"],
    "maria":            ["Dr Thuraya","Dr Taqwa"]
}
tmpl_list = TEMPLATES.get(st.session_state.user, [])

presc_file = st.file_uploader("## Upload prescription here:", type=["pdf"])
tmpl_choice = st.selectbox("## Select your card template:", tmpl_list)

if presc_file and tmpl_choice:
    file_bytes = presc_file.read()
    fields = extract_prescription_fields(file_bytes)

    if st.button("Generate Filled Card"):
        map_ = {"Dr Thuraya":"DrThuraya_Template.pdf","Dr Taqwa":"DrTaqwa_Template.pdf"}
        path = f"templates/{map_[tmpl_choice]}"
        with open(path, "rb") as f:
            tmpl_bytes = f.read()
        filled = generate_filled_card(tmpl_bytes, fields, tmpl_choice)
        safe = fields.get("patient_name","Patient").replace(" ","_")
        mrn  = fields.get("MRN","Unknown")
        fname= f"{safe}_{mrn}_card.pdf"
        st.download_button("📥 Download Filled Card PDF", filled, file_name=fname, mime="application/pdf")
