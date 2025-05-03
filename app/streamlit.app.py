# VetSmart - Livestock Monitoring, Disease Prevention and Predictive Diagnosis App

import streamlit as st
import pandas as pd
import datetime
import random
from fpdf import FPDF
import base64
import os
import joblib

# Load or simulate ML model (placeholder logic)
def predict_disease(symptoms):
    # Simulated prediction
    diseases = ['Foot-and-Mouth', 'Anthrax', 'PPR', 'Mastitis', 'None']
    prediction = random.choice(diseases[:-1]) if symptoms else 'None'
    return prediction, f"Recommended treatment and care tips for {prediction}"

# PDF generation function
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
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">Download Report</a>'

# Chatbot placeholder
def chatbot_response(user_input):
    # Simple hardcoded logic
    if 'fever' in user_input.lower():
        return "Fever may indicate infection. Ensure proper hydration and consult a vet."
    return "Sorry, I'm still learning. Please consult a veterinarian for critical concerns."

# Main App
st.set_page_config(page_title="VetSmart - Livestock Monitoring", layout="wide")
st.title("VetSmart - Livestock Monitoring and Diagnosis App")

# Sidebar Navigation
menu = st.sidebar.selectbox("Navigate", ["Livestock Dashboard", "Disease Diagnosis", "Health Tips", "Feedback", "VetBot AI"])

# Livestock Dashboard
if menu == "Livestock Dashboard":
    st.subheader("Add and Monitor Livestock")
    with st.form("livestock_form"):
        name = st.text_input("Animal Name")
        animal_type = st.selectbox("Type", ["Cattle", "Goat", "Sheep"])
        age = st.number_input("Age (years)", 0.0, 20.0, step=0.1)
        weight = st.number_input("Weight (kg)", 0.0, 500.0, step=1.0)
        vaccination = st.text_area("Vaccination History")
        submit = st.form_submit_button("Save")
    if submit:
        st.success(f"{animal_type} '{name}' saved successfully!")

# Disease Diagnosis
elif menu == "Disease Diagnosis":
    st.subheader("Symptom-based Disease Diagnosis")
    st.write("Select symptoms observed in the animal:")
    symptoms = st.multiselect("Symptoms", ["Fever", "Coughing", "Diarrhea", "Loss of appetite", "Lameness", "Swelling"])
    if st.button("Predict Disease"):
        disease, recommendation = predict_disease(symptoms)
        st.write(f"*Predicted Disease*: {disease}")
        st.write(f"*Recommendation*: {recommendation}")
        pdf_data = {
            "Symptoms": ", ".join(symptoms),
            "Predicted Disease": disease,
            "Recommendation": recommendation,
            "Date": str(datetime.date.today())
        }
        st.markdown(generate_pdf(pdf_data), unsafe_allow_html=True)

# Health Tips
elif menu == "Health Tips":
    st.subheader("General Health Tips for Livestock")
    animal = st.selectbox("Select Animal Type", ["Cattle", "Goat", "Sheep"])
    tips = {
        "Cattle": ["Provide clean water", "Regular deworming", "Maintain hygiene in sheds"],
        "Goat": ["Avoid overcrowding", "Feed balanced diet", "Trim hooves regularly"],
        "Sheep": ["Shear fleece annually", "Prevent foot rot", "Use mineral supplements"]
    }
    st.write("Here are some tips:")
    for tip in tips[animal]:
        st.write(f"- {tip}")

# Feedback
elif menu == "Feedback":
    st.subheader("Farmer Feedback & Suggestions")
    with st.form("feedback_form"):
        name = st.text_input("Your Name")
        comments = st.text_area("Suggestions or Comments")
        rating = st.slider("Rate the App", 1, 5)
        submitted = st.form_submit_button("Submit")
    if submitted:
        st.success("Thank you for your feedback!")
        st.write(f"Name: {name}")
        st.write(f"Rating: {rating}/5")
        st.write(f"Comments: {comments}")

# VetBot Chat
elif menu == "VetBot AI":
    st.subheader("Chat with VetBot")
    user_input = st.text_input("Ask VetBot your livestock-related questions")
    if user_input:
        response = chatbot_response(user_input)
        st.write(response)
