import streamlit as st
import pandas as pd
import datetime
import random
from fpdf import FPDF
import base64
import os

# Page setup
st.set_page_config(page_title="🐄 VetSmart - Livestock Monitoring", layout="wide")

# Load livestock background
st.markdown(
    """
    <style>
        .stApp {
            background-image: url('https://images.unsplash.com/photo-1601749111324-82e873f9f9d4'); 
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        .title {
            font-size: 48px;
            font-weight: bold;
            color: #2E8B57;
            text-shadow: 1px 1px #ffffff;
        }
        .sidebar .sidebar-content {
            background-color: rgba(255,255,255,0.85);
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Prediction placeholder
def predict_disease(symptoms):
    diseases = ['Foot-and-Mouth', 'Anthrax', 'PPR', 'Mastitis', 'None']
    prediction = random.choice(diseases[:-1]) if symptoms else 'None'
    return prediction, f"Recommended treatment and care tips for {prediction}"

# PDF generation
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="VetSmart Diagnosis Report", ln=1, align="C")
    for key, value in data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=1)
    file_name = "diagnosis_report.pdf"
    pdf.output(file_name)
    with open(file_name, "rb") as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    os.remove(file_name)
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">📄 Download Diagnosis Report</a>'

# Chatbot
def chatbot_response(user_input):
    if 'fever' in user_input.lower():
        return "Fever may indicate infection. Ensure proper hydration and consult a vet."
    return "🤖 I'm still learning. Please consult a veterinarian for urgent concerns."

# Title
st.markdown("<div class='title'>🐮 VetSmart - Livestock Monitoring & Diagnosis</div>", unsafe_allow_html=True)

# Sidebar Navigation
menu = st.sidebar.radio("🐐 Navigate", ["📊 Livestock Dashboard", "🦠 Disease Diagnosis", "💡 Health Tips", "📝 Feedback", "🤖 VetBot AI"])

# Livestock Dashboard
if menu == "📊 Livestock Dashboard":
    st.subheader("📋 Add and Monitor Your Livestock")
    with st.form("livestock_form"):
        name = st.text_input("Animal Name")
        animal_type = st.selectbox("Type", ["Cattle", "Goat", "Sheep"])
        age = st.number_input("Age (years)", 0.0, 20.0, step=0.1)
        weight = st.number_input("Weight (kg)", 0.0, 500.0, step=1.0)
        vaccination = st.text_area("Vaccination History")
        submit = st.form_submit_button("💾 Save")
    if submit:
        st.success(f"{animal_type} '{name}' saved successfully!")

# Disease Diagnosis
elif menu == "🦠 Disease Diagnosis":
    st.subheader("🩺 Symptom-based Disease Diagnosis")
    symptoms = st.multiselect("Select observed symptoms:", ["Fever", "Coughing", "Diarrhea", "Loss of appetite", "Lameness", "Swelling"])
    if st.button("🧠 Predict Disease"):
        disease, recommendation = predict_disease(symptoms)
        st.write(f"**Predicted Disease:** 🐾 {disease}")
        st.write(f"**Recommendation:** 💊 {recommendation}")
        pdf_data = {
            "Symptoms": ", ".join(symptoms),
            "Predicted Disease": disease,
            "Recommendation": recommendation,
            "Date": str(datetime.date.today())
        }
        st.markdown(generate_pdf(pdf_data), unsafe_allow_html=True)

# Health Tips
elif menu == "💡 Health Tips":
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

# Feedback with 5-star rating
elif menu == "📝 Feedback":
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

# VetBot AI
elif menu == "🤖 VetBot AI":
    st.subheader("💬 Ask VetBot - Your Virtual Vet Assistant")
    user_input = st.text_input("❓ Ask a question about livestock health")
    if user_input:
        response = chatbot_response(user_input)
        st.markdown(f"💡 **VetBot**: {response}")
