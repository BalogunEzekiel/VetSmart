import streamlit as st
import pandas as pd
import datetime
import random
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.graphics.barcode import code128
from reportlab.platypus import Image
from io import BytesIO

# ========== Page Setup ==========
st.set_page_config(page_title="🐄 VetSmart - Livestock Monitoring", layout="wide")

# ========== Database Configuration ==========
# SQLite Database Configuration
SQLITE_DB = 'livestock_data.db'

# ========== Database Connection Functions ==========
# Connect to SQLite
def get_sqlite_connection():
    return sqlite3.connect(SQLITE_DB)

# ========== Initialize Database and Tables ==========
def initialize_database():
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS livestock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            age REAL NOT NULL,
            weight REAL NOT NULL,
            vaccination TEXT,
            added_on DATETIME
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            feedback TEXT NOT NULL,
            submitted_on DATETIME
        )
    """)
    conn.commit()
    conn.close()

initialize_database()

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
    VALUES (?, ?, ?, ?, ?, ?)
    """
    conn.execute(query, (name, animal_type, age, weight, vaccination, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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
        animal_data = df[df["Name"] == animal_name].iloc[0]
        symptoms = st.multiselect("Select observed symptoms:", ["Fever", "Coughing", "Diarrhea", "Loss of appetite", "Lameness", "Swelling"])

        if st.button("🧠 Predict Disease"):
            disease, recommendation = predict_disease(symptoms)
            st.write(f"**Predicted Disease:** 🐾 {disease}")
            st.write(f"**Recommendation:** 💊 {recommendation}")

            # Generate PDF Report
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            normal_style = styles['Normal']

            # VetSmart Report Title
            p = Paragraph("<b>VetSmart Diagnosis Report</b>", title_style)
            p.wrapOn(c, letter[0] - 2 * inch, letter[1])
            p.drawOn(c, inch, letter[1] - 1.5 * inch)
            c.line(inch, letter[1] - 1.6 * inch, letter[0] - inch, letter[1] - 1.6 * inch)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(inch, letter[1] - 2 * inch, "Animal Information:")
            c.setFont("Helvetica", 10)
            c.drawString(inch + 0.2 * inch, letter[1] - 2.2 * inch, f"Animal Tag: {animal_data['Name']}")
            c.drawString(inch + 0.2 * inch, letter[1] - 2.4 * inch, f"Type: {animal_data['Type']}")
            c.drawString(inch + 0.2 * inch, letter[1] - 2.6 * inch, f"Age: {animal_data['Age']} years")
            c.drawString(inch + 0.2 * inch, letter[1] - 2.8 * inch, f"Weight: {animal_data['Weight']} kg")

            c.setFont("Helvetica-Bold", 12)
            c.drawString(inch, letter[1] - 3.2 * inch, "Diagnosis:")
            c.setFont("Helvetica", 10)
            c.drawString(inch + 0.2 * inch, letter[1] - 3.4 * inch, f"Predicted Disease: {disease}")
            c.drawString(inch + 0.2 * inch, letter[1] - 3.6 * inch, f"Recommendation: {recommendation}")

            # VetSmart Authentication Barcode
            barcode_value = f"VS-DR-{animal_data['name']}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            barcode = code128.Code128(barcode_value, barHeight=0.75 * inch)
            barcode.drawOn(c, letter[0] - 3 * inch, inch)
            c.setFont("Helvetica", 8)
            c.drawString(letter[0] - 3 * inch, inch - 0.2 * inch, "VetSmart Authenticated")
            c.drawString(letter[0] - 3 * inch, inch - 0.4 * inch, barcode_value)

            # Footer
            c.setFont("Helvetica", 8)
            c.drawRightString(letter[0] - inch, 0.75 * inch, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawRightString(letter[0] - inch, 0.6 * inch, "Powered by VetSmart")

            c.save()
            buffer.seek(0)

            st.download_button(
                label="Download Diagnosis Report",
                data=buffer,
                file_name=f"{animal_name}_diagnosis_report.pdf",
                mime="application/pdf"
            )

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
            if name.strip() == "" or feedback_text.strip() == "":
                st.warning("Name and Feedback cannot be empty.")
            else:
                # Save feedback to the database
                conn = get_sqlite_connection()
                query = """
                INSERT INTO feedback (name, feedback, submitted_on)
                VALUES (?, ?, ?)
                """
                # Use parameterized query to prevent SQL injection
                conn.execute(query, (name, feedback_text, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success("Thank you for your feedback. Hope to see you again soon!")

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
