import streamlit as st
from io import BytesIO
from extract import extract_prescription_fields, generate_filled_card
import base64
import smtplib

SMTP_HOST = st.secrets["SMTP_HOST"]
SMTP_PORT = int(st.secrets["SMTP_PORT"])
SMTP_USER = st.secrets["SMTP_USER"]
SMTP_PASS = st.secrets["SMTP_PASS"]
FROM_EMAIL = st.secrets["FROM_EMAIL"]

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
#recovery emails per user
RECOVERY_EMAILS = {
    "thuraya.mohammed": ["thuraya.mohammed@alsalamahospital.com"],
    "taqwa.taha":       ["taqwa.taha@alsalamahospital.com"],
    "maria":            ["sammz2003@gmail.com"]
}

if "password_reset_otp" not in st.session_state:
    st.session_state.password_reset_otp = None
if "password_reset_user" not in st.session_state:
    st.session_state.password_reset_user = None
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

# On login page, under the Login button:
    st.markdown("---")
    if st.button("Forgot Password?"):
    # Ensure they entered a username
        if not user or user not in VALID_USERS:
            st.warning("Enter a valid username first")
        else:
            # Generate OTP
            import random
            otp = f"{random.randint(0,999999):06d}"
            st.session_state.password_reset_otp  = otp
            st.session_state.password_reset_user = user
    
            # Send email
            emails = RECOVERY_EMAILS[user]
            message = f"Subject: Your OTP\n\nYour password reset code is: {otp}"
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(SMTP_USER, SMTP_PASS)
                for addr in emails:
                    smtp.sendmail(FROM_EMAIL, addr, message)

            st.info("An OTP has been sent to your recovery email(s).")
# If they’ve requested a reset, show OTP & new-password fields:
    if st.session_state.password_reset_otp:
        st.subheader("🔑 Reset Password")
        entered_otp = st.text_input("Enter the 6-digit OTP sent to your email")
        new_pw1     = st.text_input("New password", type="password")
        new_pw2     = st.text_input("Confirm new password", type="password")
        if st.button("Confirm Reset"):
            if entered_otp != st.session_state.password_reset_otp:
                st.error("❌ Incorrect OTP")
            elif not new_pw1 or new_pw1 != new_pw2:
                st.error("❌ Passwords do not match")
            else:
                # Update password
                user = st.session_state.password_reset_user
                VALID_USERS[user] = new_pw1
                st.success("✅ Password updated. Please log in with your new password.")
                # Clear reset session
                st.session_state.password_reset_otp = None
                st.session_state.password_reset_user = None
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
