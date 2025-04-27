# streamlit_app.py
import streamlit as st
import webbrowser

# 360dialog Partner Info
PARTNER_ID = "MalHtRPA"  # <-- your actual Partner ID
REDIRECT_URL = "https://yourbackend.com/your_redirect_handler"  # <-- your redirect URL

# Build onboarding URL
onboarding_url = f"https://hub.360dialog.com/dashboard/app/{PARTNER_ID}/permissions?redirect_url={REDIRECT_URL}"

st.title("360dialog WhatsApp Onboarding")

st.write("Click below to onboard your business to WhatsApp API:")

if st.button("Start WhatsApp Onboarding"):
    webbrowser.open_new_tab(onboarding_url)
    st.success("Onboarding window opened! Please complete the steps there.")
