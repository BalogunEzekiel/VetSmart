import streamlit as st
import pandas as pd
import datetime
import random
import sqlite3
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.barcode import code128
from reportlab.lib.units import inch

# ========== Page Setup ==========
st.set_page_config(page_title="🐄 VetSmart - Livestock Monitoring", layout="wide")

# ========== Database Configuration ==========
SQLITE_DB = 'livestock_data.db'

# ========== Database Functions ==========
def get_sqlite_connection():
    return sqlite3.connect(SQLITE_DB)

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
    conn.commit()
    conn.close()

initialize_database()

# ========== Data Functions ==========
def load_data():
    conn = get_sqlite_connection()
    df = pd.read_sql("SELECT * FROM livestock", conn)
    conn.close()
    return df

def save_livestock_data(name, animal_type, age, weight, vaccination):
    conn = get_sqlite_connection()
    query = """
    INSERT INTO livestock (name, type, age, weight, vaccination, added_on)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    conn.execute(query, (name, animal_type, age, weight, vaccination, datetime.datetime.now()))
    conn.commit()
    conn.close()

# ========== Disease Prediction ==========
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

# ========== PDF Report ==========
def generate_diagnosis_report(animal_data, disease, recommendation):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    styles = getSampleStyleSheet()

    header_height = 1.5 * inch
    c.setFillColor(colors.lightblue)
    c.rect(0, height - header_height, width, header_height, fill=1, stroke=0)

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.white)
    title = "VetSmart Diagnosis Report"
    title_width = c.stringWidth(title, "Helvetica-Bold", 16)
    c.drawString((width - title_width) / 2, height - header_height / 2 + 10, title)

    y_position = height - header_height - inch

    # Animal Information
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(inch, y_position, "Animal Information:")
    y_position -= 0.3 * inch

    data = [
        ['Animal Tag', animal_data['name']],
        ['Type', animal_data['type']],
        ['Age (years)', animal_data['age']],
        ['Weight (kg)', animal_data['weight']],
    ]

    table = Table(data, colWidths=[2.5 * inch, 3.5 * inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    table.wrapOn(c, width, height)
    table.drawOn(c, inch, y_position - table._height)
    y_position -= table._height + 0.5 * inch

    # Diagnosis
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y_position, "Diagnosis:")
    y_position -= 0.3 * inch

    diagnosis_data = [
        ['Predicted Disease', disease],
        ['Recommendation', recommendation],
    ]
    diagnosis_table = Table(diagnosis_data, colWidths=[2.5 * inch, 3.5 * inch])
    diagnosis_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    diagnosis_table.wrapOn(c, width, height)
    diagnosis_table.drawOn(c, inch, y_position - diagnosis_table._height)
    y_position -= diagnosis_table._height + 0.5 * inch

    # Barcode
    barcode_value = f"VS-{animal_data['name']}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    barcode = code128.Code128(barcode_value, barHeight=0.5 * inch)
    barcode_width = barcode.wrap(0, 0)[0]
    x_position = width - barcode_width - inch
    barcode.drawOn(c, x_position, inch)
    c.setFont("Helvetica", 8)
    c.drawString(x_position, inch - 0.2 * inch, "VetSmart Authenticated")

    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(inch, 0.75 * inch, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(inch, 0.6 * inch, "Powered by VetSmart")

    c.save()
    buffer.seek(0)
    return buffer

# ========== Dashboard ==========
def display_dashboard():
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
            save_livestock_data(name, animal_type, age, weight, vaccination)
            st.success(f"{animal_type} '{name}' saved successfully!")

# ========== Diagnosis ==========
def display_diagnosis():
    st.subheader("🩺 Symptom-based Disease Diagnosis")
    df = load_data()
    if df.empty:
        st.warning("No livestock registered yet. Please add animals first.")
        return

    animal_name = st.selectbox("Select Animal", df["name"].unique())
    symptoms = st.text_area("Enter Observed Symptoms (comma-separated)")

    if st.button("🔍 Predict Disease"):
        if animal_name and symptoms.strip():
            selected_animal = df[df['name'] == animal_name].iloc[0].to_dict()
            disease, recommendation = predict_disease(symptoms)

            st.success(f"🦠 Predicted Disease: **{disease}**")
            st.info(f"💊 Recommendation: {recommendation}")

            pdf_buffer = generate_diagnosis_report(selected_animal, disease, recommendation)

            st.download_button(
                label="📄 Download Diagnosis Report (PDF)",
                data=pdf_buffer,
                file_name=f"{animal_name}_diagnosis_report.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("Please enter symptoms to predict disease.")

# ========== Main ==========
st.title("🐄 VetSmart - Livestock Health Monitoring")
tab1, tab2 = st.tabs(["📊 Dashboard", "🩺 Diagnosis"])
with tab1:
    display_dashboard()
with tab2:
    display_diagnosis()
