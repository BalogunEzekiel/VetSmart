import streamlit as st

# ========== Page Setup ==========
st.set_page_config(page_title="VetSmart", layout="wide")

import pandas as pd
import datetime
import random
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.graphics.barcode import code128
from io import BytesIO
from reportlab.lib import colors

# ========== Database Configuration ==========
SQLITE_DB = 'livestock_data.db'

# ========== Database Connection Functions ==========
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

# ========== PDF Generation Function ==========
def generate_diagnosis_report(animal_data, disease, recommendation):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    centered_title_style = ParagraphStyle(name='CenteredTitle', parent=styles['Heading1'], alignment=1)

    # VetSmart Report Title
    p = Paragraph("<b>Animal Information</b>", centered_title_style)
    p.wrapOn(c, letter[0] - 2 * inch, letter[1])
    p.drawOn(c, inch, letter[1] - 1.5 * inch)
    c.line(inch, letter[1] - 1.6 * inch, letter[0] - inch, letter[1] - 1.6 * inch)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, letter[1] - 2 * inch, "")
    c.setFont("Helvetica", 10)

    # Animal Information Table
    data = [
        ['Animal Tag', animal_data['Name']],
        ['Type', animal_data['Type']],
        ['Age (years)', animal_data['Age']],
        ['Weight (kg)', animal_data['Weight']],
    ]
    table = Table(data, colWidths=[letter[0] / 3.0, (2 * letter[0]) / 3.0])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    table.wrapOn(c, letter[0] - 2 * inch, letter[1])
    table.drawOn(c, inch, letter[1] - 2.5 * inch)
    c.line(inch, letter[1] - 3.1 * inch, letter[0] - inch, letter[1] - 3.1 * inch)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, letter[1] - 3.5 * inch, "Diagnosis:")
    c.setFont("Helvetica", 10)

    # Diagnosis Table
    diagnosis_data = [
        ['Predicted Disease', disease],
        ['Recommendation', recommendation],
    ]
    diagnosis_table = Table(diagnosis_data, colWidths=[letter[0] / 3.0, (2 * letter[0]) / 3.0])
    diagnosis_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    diagnosis_table.wrapOn(c, letter[0] - 2 * inch, letter[1])
    diagnosis_table.drawOn(c, inch, letter[1] - 4 * inch)

    # VetSmart Authentication Barcode (Right-Aligned)
    barcode_value = f"VS-DR-{animal_data['Name']}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    barcode = code128.Code128(barcode_value, barHeight=0.75 * inch)
    barcode_width = barcode.wrap(0, 0)[0]  # Get barcode width
    right_margin = inch
    x_position = letter[0] - barcode_width - right_margin
    y_position = inch
    barcode.drawOn(c, x_position, y_position)
    c.setFont("Helvetica", 8)
    c.drawString(x_position, y_position - 0.2 * inch, "VetSmart Authenticated")
    c.drawString(x_position, y_position - 0.4 * inch, barcode_value)

    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(inch, 0.75 * inch, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(inch, 0.6 * inch, "Powered by VetSmart")
    
    c.save()
    buffer.seek(0)
    return buffer

# ========== Page Functions ==========
def display_dashboard():
    """Displays the livestock dashboard and add animal form."""
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

def display_diagnosis():
    """Displays the symptom-based disease diagnosis section."""
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

            pdf_buffer = generate_diagnosis_report(animal_data, disease, recommendation)

            st.download_button(
                label="Download Diagnosis Report",
                data=pdf_buffer,
                file_name=f"{animal_name}_diagnosis_report.pdf",
                mime="application/pdf"
            )

def display_health_tips():
    """Displays general health tips for selected livestock."""
    st.subheader("🌿 General Health Tips for Livestock")
    animal = st.selectbox("Select Animal Type", ["Cattle", "Goat", "Sheep"])
    tips = {
        "Cattle": [
            "✅ Provide clean water daily.",
            "💉 Schedule regular vaccinations and deworming.",
            "🧼 Maintain proper hygiene in sheds.",
            "🌱 Ensure access to quality feed and pasture.",
            "📋 Monitor body condition and behavior regularly."
        ],
        "Goat": [
            "🚫 Avoid overcrowding in pens.",
            "🥗 Feed balanced diet with minerals and vitamins.",
            "🧽 Clean water containers daily.",
            "📆 Conduct routine hoof trimming.",
            "💉 Deworm and vaccinate periodically."
        ],
        "Sheep": [
            "🧴 Shear regularly to prevent overheating.",
            "💊 Monitor for signs of parasites.",
            "🌾 Provide nutritious forage.",
            "👀 Check for eye infections and foot rot.",
            "🛏️ Keep bedding dry and clean."
        ]
    }

    for tip in tips[animal]:
        st.markdown(f"- {tip}")

def handle_feedback_submission():
    """Handles the feedback submission process."""
    st.subheader("We Value Your Feedback 📝")
    with st.form("feedback_form"):
        name = st.text_input("Your Name")
        feedback_text = st.text_area("Please provide your feedback here:")
        submitted = st.form_submit_button("Submit Feedback")

        if submitted:
            if name.strip() == "" or feedback_text.strip() == "":
                st.warning("Name and Feedback cannot be empty.")
            else:
                conn = get_sqlite_connection()
                cursor = conn.cursor()
                query = """
                INSERT INTO feedback (name, feedback, submitted_on)
                VALUES (?, ?, ?)
                """
                now = datetime.datetime.now()
                cursor.execute(query, (name, feedback_text, now))
                conn.commit()
                conn.close()
                st.success("Thank you for your feedback!")

# ========== Sidebar ==========
with st.sidebar:
    st.sidebar.image("https://img.icons8.com/emoji/96/cow-emoji.png", width=80)
    st.markdown("## 🐄 About VetSmart")
    st.markdown("""
    **VetSmart** is an AI-powered livestock health monitoring, disease prevention and diagnosis app. It is designed to help farmers and veterinary experts monitor animal health, predict diseases, treatment recommendations and improve the health status of their animals in real-time.
    
    With features like livestock registration, disease prediction based on symptoms, vaccination records and downloadable diagnosis reports, VetSmart enhances the efficiency and accuracy of animal healthcare decisions.

    **Contributors:**
    - **Ezekiel BALOGUN**
    *Data Scientist/Lead*  
    - **Oluwakemi Adesanwo**
    *Data Analyst*  
    - **Damilare Abayomi**
    *Software Developer*  
    - **Boluwatife Adeagbo**
    *Veterinary Doctor*
    """)

# ========== Centered Logo ==========
st.markdown(
    """
    <div style="text-align: center;">
        <img src="Logo.png" width="150" alt="VetSmart Logo">
    </div>
    """,
    unsafe_allow_html=True
)

# ========== Title & Subtitle ==========
st.markdown(
    """
    <div style="text-align: center; margin-top: 10px;">
        <h1 style="font-size: 36px; font-weight: bold; margin-bottom: 0;">🐮 VetSmart</h1>
        <h3 style="font-weight: normal; font-size: 20px; color: #555;">Livestock Monitoring, Disease Prevention and Diagnosis</h3>
    </div>
    """,
    unsafe_allow_html=True
)
# ========== Main ==========
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🩺 Diagnosis", "💡 Health Tips", "📝 Feedback"])
with tab1:
    display_dashboard()
with tab2:
    display_diagnosis()
with tab3:
    display_health_tips()
with tab4:
    handle_feedback_submission()

# ========== SQLite Database Download ==========
st.sidebar.markdown("## Download Data")
if st.sidebar.button("Download SQLite Data as CSV"):
    conn = get_sqlite_connection()
    df = pd.read_sql("SELECT * FROM livestock", conn)
    conn.close()

    csv = df.to_csv(index=False)
    st.sidebar.download_button(
        label="📥 Download livestock_data.csv",
        data=csv,
        file_name="livestock_data.csv",
        mime="text/csv"
    )

# ================VetChat==================
import streamlit as st
from datetime import datetime

# ========== Simple Rule-Based Chatbot ==========
def chatbot_response(user_input):
    user_input = user_input.lower()
    responses = {
        "hello": "Hi there! How can I assist you with your livestock today?",
        "hi": "Hello! What would you like help with?",
        "how are you": "I'm just a bot, but I'm functioning properly!",
        "disease": "You can go to the 'Disease Prediction' tab to analyze symptoms.",
        "vaccination": "Vaccination records can be managed in the 'Livestock Records' tab.",
        "bye": "Goodbye! Stay healthy and safe!",
    }
    for key in responses:
        if key in user_input:
            return responses[key]
    return "Sorry, I didn't understand that. Please try asking something else."

# ========== Persistent Chatbot Widget ==========
def chatbot_widget():
    with st.sidebar.expander("💬 VetSmart Chatbot", expanded=True):
        st.markdown("*Ask me anything about livestock care!*")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for sender, message in st.session_state.chat_history:
            if sender == "You":
                st.markdown(f"**You:** {message}")
            else:
                st.markdown(f"🤖 **VetSmart:** {message}")

        user_input = st.text_input("You:", key="chat_input", label_visibility="collapsed")

        if user_input:
            response = chatbot_response(user_input)
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("VetSmart", response))
            st.session_state.chat_input = ""  # Clear input field


# ========== Main App ==========
st.title("VetSmart: Livestock Care Assistant")

# Sidebar Navigation
st.sidebar.title("VetSmart Navigation")
tabs = ["Home", "Disease Prediction", "Livestock Records"]
selected_tab = st.sidebar.radio("Select a Tab", tabs)

# Include chatbot in the sidebar for all tabs
chatbot_widget()

# Content for each tab
if selected_tab == "Home":
    st.header("Welcome to VetSmart!")
    st.write("This is your go-to assistant for livestock care.")

elif selected_tab == "Disease Prediction":
    st.header("Disease Prediction")
    st.write("Predict livestock diseases based on symptoms.")

elif selected_tab == "Livestock Records":
    st.header("Livestock Records")
    st.write("Manage your livestock information and vaccination history.")
