import streamlit as st
import pandas as pd
import datetime
import random
from fpdf import FPDF
import base64
import os
import pickle

# Google Drive API
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Page setup
st.set_page_config(page_title="🐄 VetSmart - Livestock Monitoring", layout="wide")
CSV_FILE = "livestock_data.csv"

# Load and Save Data
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=["Name", "Type", "Age", "Weight", "Vaccination", "Added On"])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

if "livestock_data" not in st.session_state:
    st.session_state["livestock_data"] = load_data()

# Custom CSS
st.markdown("""
<style>
.stApp {
    background-image: url('https://images.unsplash.com/photo-1601749111324-82e873f9f9d4');
    background-size: cover;
    background-attachment: fixed;
}
.title {
    font-size: 48px;
    font-weight: bold;
    color: #2E8B57;
    text-shadow: 1px 1px #ffffff;
}
</style>
""", unsafe_allow_html=True)

# Google Drive Authentication
def authenticate_drive():
    creds = None
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(
                "credentials.json",
                scopes=["https://www.googleapis.com/auth/drive.file"],
                redirect_uri="urn:ietf:wg:oauth:2.0:oob"
            )
            auth_url, _ = flow.authorization_url(prompt="consent")
            st.markdown(f"🔗 [Click here to authorize Google Drive access]({auth_url})")
            code = st.text_input("Paste the authorization code here:")
            if code:
                flow.fetch_token(code=code)
                creds = flow.credentials
                with open("token.pkl", "wb") as token:
                    pickle.dump(creds, token)
    return creds

def upload_file_to_drive(filepath, filename):
    creds = authenticate_drive()
    if creds:
        service = build("drive", "v3", credentials=creds)
        file_metadata = {"name": filename}
        media = MediaFileUpload(filepath, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        return file.get("id")
    return None

# Disease Prediction Logic
def predict_disease(symptoms):
    diseases = ['Foot-and-Mouth', 'Anthrax', 'PPR', 'Mastitis', 'None']
    prediction = random.choice(diseases[:-1]) if symptoms else 'None'
    treatments = {
        "Foot-and-Mouth": "Vaccinate and isolate affected livestock.",
        "Anthrax": "Antibiotic treatment and quarantine infected animals.",
        "PPR": "Supportive care and vaccines.",
        "Mastitis": "Treat with antibiotics and maintain hygiene.",
        "None": "No disease detected."
    }
    return prediction, treatments[prediction]

# PDF Report Generator
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="VetSmart Diagnosis Report", ln=1, align="C")
    pdf.ln(5)
    for key, value in data.items():
        pdf.multi_cell(0, 10, txt=f"{key}: {value}")
    file_name = "diagnosis_report.pdf"
    pdf.output(file_name)
    return file_name

# Simple Chatbot
def chatbot_response(user_input):
    if 'fever' in user_input.lower():
        return "Fever may indicate infection. Ensure proper hydration and consult a vet."
    return "🤖 I'm still learning. Please consult a veterinarian for urgent concerns."

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/emoji/96/cow-emoji.png", width=80)
st.sidebar.markdown("## VetSmart Navigation")
pages = {
    "📊 Livestock Dashboard": "dashboard",
    "🦠 Disease Diagnosis": "diagnosis",
    "💡 Health Tips": "tips",
    "📝 Feedback": "feedback"
}
selected_page = st.sidebar.radio("Go to", list(pages.keys()))
selected_page_key = pages[selected_page]

# Title
st.markdown("<div class='title'>🐮 VetSmart</div>", unsafe_allow_html=True)
st.subheader("Livestock Monitoring, Disease Prevention and Diagnosis")

# ========== PAGES ==========

# Dashboard
if selected_page_key == "dashboard":
    st.subheader("📋 Add and Monitor Your Livestock")
    with st.form("livestock_form"):
        name = st.text_input("Animal Tag")
        animal_type = st.selectbox("Type", ["Cattle", "Goat", "Sheep"])
        age = st.number_input("Age (years)", 0.0, 20.0, step=0.1)
        weight = st.number_input("Weight (kg)", 0.0, 500.0, step=1.0)
        vaccination = st.text_area("Vaccination History")
        submit = st.form_submit_button("💾 Save")

    if submit:
        if name.strip() == "":
            st.warning("Animal Tag cannot be empty.")
        else:
            new_entry = pd.DataFrame([{
                "Name": name,
                "Type": animal_type,
                "Age": age,
                "Weight": weight,
                "Vaccination": vaccination,
                "Added On": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            st.session_state["livestock_data"] = pd.concat(
                [st.session_state["livestock_data"], new_entry], ignore_index=True
            )
            save_data(st.session_state["livestock_data"])
            st.success(f"{animal_type} '{name}' saved successfully!")

    if not st.session_state["livestock_data"].empty:
        st.dataframe(st.session_state["livestock_data"])
        csv = st.session_state["livestock_data"].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "livestock_data.csv", "text/csv")

        if st.button("🧹 Clear All Livestock Records"):
            st.session_state["livestock_data"] = pd.DataFrame(
                columns=["Name", "Type", "Age", "Weight", "Vaccination", "Added On"]
            )
            save_data(st.session_state["livestock_data"])
            st.success("All records cleared.")

# Diagnosis
elif selected_page_key == "diagnosis":
    st.subheader("🩺 Symptom-based Disease Diagnosis")
    if st.session_state["livestock_data"].empty:
        st.warning("No livestock registered yet. Please add animals to the dashboard first.")
    else:
        animal_name = st.selectbox("Select Registered Animal", st.session_state["livestock_data"]["Name"])
        symptoms = st.multiselect("Select observed symptoms:", ["Fever", "Coughing", "Diarrhea", "Loss of appetite", "Lameness", "Swelling"])

        if st.button("🧠 Predict Disease"):
            disease, recommendation = predict_disease(symptoms)
            st.write(f"**Predicted Disease:** 🐾 {disease}")
            st.write(f"**Recommendation:** 💊 {recommendation}")

            pdf_data = {
                "Animal Name": animal_name,
                "Symptoms": ", ".join(symptoms),
                "Predicted Disease": disease,
                "Recommendation": recommendation,
                "Date": str(datetime.date.today())
            }
            file_path = generate_pdf(pdf_data)
            with open(file_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
            st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="{file_path}">📄 Download Diagnosis Report</a>', unsafe_allow_html=True)

            drive_file_id = upload_file_to_drive(file_path, file_path)
            if drive_file_id:
                st.success(f"📁 Uploaded to Google Drive! [Open File](https://drive.google.com/file/d/{drive_file_id})")
            os.remove(file_path)

# Tips
elif selected_page_key == "tips":
    st.subheader("🌿 General Health Tips for Livestock")
    animal = st.selectbox("Select Animal Type", ["Cattle", "Goat", "Sheep"])
    tips = {
        "Cattle": ["✅ Provide clean water", "💉 Regular deworming", "🧼 Maintain hygiene in sheds"],
        "Goat": ["🚫 Avoid overcrowding", "🥗 Feed balanced diet", "✂️ Trim hooves regularly"],
        "Sheep": ["✂️ Shear fleece annually", "🧼 Prevent foot rot", "🧪 Use mineral supplements"]
    }
    st.write("🐾 Here are some expert tips:")
    for tip in tips[animal]:
        st.markdown(f"- {tip}")

# Feedback
elif selected_page_key == "feedback":
    st.subheader("🗣️ Farmer Feedback & Suggestions")
    with st.form("feedback_form"):
        name = st.text_input("👤 Your Name")
        comments = st.text_area("💬 Suggestions or Comments")
        rating = st.radio("⭐ Rate the App", [1, 2, 3, 4, 5], horizontal=True)
        submitted = st.form_submit_button("🚀 Submit Feedback")
    if submitted:
        st.success("🎉 Thank you for your feedback!")
        st.write(f"👤 Name: {name}")
        st.write(f"⭐ Rating: {rating}/5")
        st.write(f"💬 Comments: {comments}")

# VetBot
with st.container():
    with st.expander("🤖 Ask VetBot", expanded=False):
        user_input = st.text_input("💬 Ask a question")
        if user_input:
            response = chatbot_response(user_input)
            st.markdown(f"💡 **VetBot**: {response}")
