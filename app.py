import streamlit as st
from io import BytesIO
from extract import extract_prescription_fields, generate_filled_card
import base64
import smtplib
import os
import json

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users_dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users_dict, f, indent=2)

# On first load, seed session_state with our hard-coded passwords
if "user_passwords" not in st.session_state:
    st.session_state.user_passwords = {
        "thuraya.mohammed": "tmm96",
        "taqwa.taha":       "tth48",
        "maria":            "m123"
    }

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
            top: 25px;
            right: 20px;
            z-index: 100;
        }}
        .logo-container img {{
            width: 200px;
            height: auto;
        }}
        .contact-info {{
            position: fixed;
            bottom: 20px;
            left: 25px;
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
users = load_users()
if "password_reset_otp" not in st.session_state:
    st.session_state.password_reset_otp = None
if "password_reset_user" not in st.session_state:
    st.session_state.password_reset_user = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Doctor Login")
    user = st.text_input("Username")
    pw   = st.text_input("Password", type="password")
    if st.button("Login"):
        if users.get(user, {}).get("password") == pw:
            st.session_state.authenticated = True
            st.session_state.user = user
            #st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# On login page, under the Login button:
    st.markdown("---")
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    if st.button("Forgot Password?"):
        if user not in users:
            st.warning("Enter a valid username first")
        else:
            import random
            otp = f"{random.randint(0,999999):06d}"
            st.session_state.password_reset_otp = otp
            st.session_state.password_reset_user = user
    
            emails = users[user]["recovery"]
            subject = "Password Reset - Al Salama Hospital"
    
            # HTML Email body
            html_content = f"""
            <html>
              <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; padding: 20px;">
                <div style="max-width: 500px; margin: auto; background-color: white; border-radius: 8px; padding: 20px; border: 1px solid #ddd;">
                  <div style="text-align: center;">
                    <img src="https://alsalamahospital.com/wp-content/uploads/2024/02/Logo.png" alt="Al Salama Hospital" style="max-width: 200px; margin-bottom: 20px;">
                  </div>
                  <h2 style="color: #003366; text-align: center;">Password Reset Request</h2>
                  <p style="font-size: 16px;">Dear Doctor,</p>
                  <p style="font-size: 16px;">Your One-Time Password (OTP) is:</p>
                  <div style="text-align: center; font-size: 22px; font-weight: bold; background-color: #003366; color: white; padding: 10px; border-radius: 4px;">
                    {otp}
                  </div>
                  <p style="font-size: 14px; color: #666;">This OTP will expire in 10 minutes. If you did not request a password reset, please contact IT support immediately.</p>
                  <hr>
                  <p style="font-size: 14px; color: #666; text-align: center;">
                    📞 920051919 | 📧 info@alsalamahospital.com | 🌐 <a href="https://www.alsalamahospital.com" style="color: #003366;">alsalamahospital.com</a>
                  </p>
                </div>
              </body>
            </html>
            """
    
            # Build MIME email
            for addr in emails:
                msg = MIMEMultipart("alternative")
                msg["From"] = FROM_EMAIL
                msg["To"] = addr
                msg["Subject"] = subject
                msg.attach(MIMEText(html_content, "html"))
    
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
                    smtp.starttls()
                    smtp.login(SMTP_USER, SMTP_PASS)
                    smtp.sendmail(FROM_EMAIL, addr, msg.as_string())
    
            st.info("An OTP has been sent to your recovery email(s).")

# If they’ve requested a reset, show OTP & new-password fields:
    if st.session_state.password_reset_otp:
        st.subheader("Reset Password")
        entered_otp = st.text_input("Enter the 6-digit OTP sent to your email")
        new_pw1     = st.text_input("New password", type="password")
        new_pw2     = st.text_input("Confirm new password", type="password")
        if st.button("Reset"):
            if entered_otp != st.session_state.password_reset_otp:
                st.error("Incorrect OTP")
            elif not new_pw1 or new_pw1 != new_pw2:
                st.error("Passwords do not match")
            else:
                # Update password
                user = st.session_state.password_reset_user
                users[user]["password"] = new_pw1
                save_users(users)
                st.success("Password updated. Please log in with your new password.")
                # Clear reset session
                st.session_state.password_reset_otp = None
                st.session_state.password_reset_user = None
    st.stop()

# ——————————————————————————————
# 3) Main App (post-login)
# ——————————————————————————————
st.sidebar.success(f"Logged in as: **{st.session_state.user}**")

st.title("PRESCRIPTION PDF TO CARD")

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
        st.download_button("Download Filled Card PDF", filled, file_name=fname, mime="application/pdf")
