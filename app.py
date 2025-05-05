# streamlit_app.py
import streamlit as st
import webbrowser
import urllib.parse
# 360dialog Partner Info
PARTNER_ID = "MalHtRPA"  # <-- your actual Partner ID
REDIRECT_URL = "https://solasolution.ecomtask.de/app3/redirect"  # <-- your redirect URL


# Building the onboarding URL manually (like ConnectButton does)
base_url = f"https://hub.360dialog.com/dashboard/app/{PARTNER_ID}/permissions"

# Additional query parameters
query_params = {
    "redirect_url": REDIRECT_URL,
    "plan_selection": "regular"  # Same as your queryParameters in ConnectButton
}

# Final onboarding URL
onboarding_url = f"{base_url}?{urllib.parse.urlencode(query_params)}"

# Streamlit UI
st.title("🚀 WhatsApp Business Onboarding")

st.write("Click the button below to create your WhatsApp Business Account:")

if st.button("Create your WhatsApp Business Account"):
    st.write("Opening onboarding window...")
    js = f"window.open('{onboarding_url}')"  # opens in a new tab
    st.components.v1.html(f"<script>{js}</script>")
