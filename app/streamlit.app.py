import streamlit as st
import pandas as pd
import datetime
import random
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ========== Page Setup ==========
st.set_page_config(page_title="🐄 VetSmart - Livestock Monitoring", layout="wide")

# ========== Database Configuration ==========
# SQLite Database Configuration
SQLITE_DB = 'livestock_data.db'

# ========== Database Connection Functions ==========
# Connect to SQLite
def get_sqlite_connection():
    return sqlite3.connect(SQLITE_DB)

# ========== Load & Save Data Functions ==========
# Load data from SQLite
def load_data():
    conn = get_sqlite_connection()
    df = pd.read_sql("SELECT * FROM livestock", conn)
    conn.close()
    return df

# Save data to SQLite
def save_data(name, animal_type, age, weight, vaccination):
    conn = get_sqlite_connection()
    query = f"""
    INSERT INTO livestock (name, type, age, weight, vaccination, added_on)
    VALUES ('{name}', '{animal_type}', {age}, {weight}, '{vaccination}', '{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    """
    conn.execute(query)
    conn.commit()
    conn.close()

# ========== Custom CSS ==========
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

# ========== Disease Prediction Function ==========
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

# ========== Sidebar ==========
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

# ========== Title ==========
st.markdown("<div class='title'>🐮 VetSmart</div>", unsafe_allow_html=True)
st.markdown("<h3 style='font-weight: normal; font-size: 20px;'>Livestock Monitoring, Disease Prevention and Diagnosis</h3>", unsafe_allow_html=True)

# ========== Pages ==========
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
            save_data(name, animal_type, age, weight, vaccination)
            st.success(f"{animal_type} '{name}' saved successfully!")

elif selected_page_key == "diagnosis":
    st.subheader("🩺 Symptom-based Disease Diagnosis")
    df = load_data()
    if df.empty:
        st.warning("No livestock registered yet. Please add animals to the dashboard first.")
    else:
        animal_name = st.selectbox("Select Registered Animal", df["Name"])
        symptoms = st.multiselect("Select observed symptoms:", ["Fever", "Coughing", "Diarrhea", "Loss of appetite", "Lameness", "Swelling"])

        if st.button("🧠 Predict Disease"):
            disease, recommendation = predict_disease(symptoms)
            st.write(f"**Predicted Disease:** 🐾 {disease}")
            st.write(f"**Recommendation:** 💊 {recommendation}")
            
            # Generate PDF Report
            c = canvas.Canvas(f"{animal_name}_diagnosis_report.pdf", pagesize=letter)
            c.setFont("Helvetica", 12)
            c.drawString(100, 750, f"Animal Tag: {animal_name}")
            c.drawString(100, 730, f"Predicted Disease: {disease}")
            c.drawString(100, 710, f"Recommendation: {recommendation}")
            c.save()
            st.download_button(label="Download Diagnosis Report", data=open(f"{animal_name}_diagnosis_report.pdf", "rb").read(), file_name=f"{animal_name}_diagnosis_report.pdf", mime="application/pdf")

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

elif selected_page_key == "feedback":
    st.subheader("📝 We value your feedback!")
    with st.form("feedback_form"):
        name = st.text_input("Your Name")
        feedback_text = st.text_area("Please provide your feedback here:")
        submitted = st.form_submit_button("Submit Feedback")
        if submitted:
            # Here you can define how to handle the feedback, e.g., save to a database or send an email
            st.success("Thank you for your feedback!")

# ========== SQLite Database Download ==========
st.sidebar.markdown("## Download Data")
if st.sidebar.button("Download SQLite Data as CSV"):
    conn = get_sqlite_connection()
    df = pd.read_sql("SELECT * FROM livestock", conn)
    conn.close()

    # Convert to CSV in memory
    csv = df.to_csv(index=False)
    st.sidebar.download_button(
        label="📥 Download livestock_data.csv",
        data=csv,
        file_name="livestock_data.csv",
        mime="text/csv"
    )
