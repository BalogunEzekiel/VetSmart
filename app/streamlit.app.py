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
import nltk
from PIL import Image
import plotly.express as px


# ========== Centered Logo ==========

# Logo and title
# Layout: 3 columns
col1, col2, col3 = st.columns([1, 4, 1])  # Adjust ratios as needed

with col1:
    try:
        logo = Image.open("logoo.png")
        st.image(logo, width=120)
    except Exception as e:
        st.warning(f"Logo could not be loaded: {e}")

with col2:
    st.markdown("<h1 style='text-align: center;'>VetSmart</h1>", unsafe_allow_html=True)

# Optional: leave col3 empty or use it for spacing/content
# ========== Title & Subtitle ==========
st.markdown(
    """
    <div style="text-align: center; margin-top: 10px;">
        <h3 style="font-weight: normal; font-size: 20px; color: #555;">Livestock Monitoring, Disease Prevention and Diagnosis</h3>
    </div>
    """,
    unsafe_allow_html=True
)

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
            animal_type TEXT NOT NULL,
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS veterinarians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            registered_on DATETIME
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vet_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_name TEXT NOT NULL,
            animal_tag TEXT NOT NULL,
            vet_id INTEGER,
            request_reason TEXT,
            requested_on DATETIME,
            FOREIGN KEY(vet_id) REFERENCES veterinarians(id)
        )
    """)

    conn.commit()
    conn.close()

# Initialize the database and tables
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


def load_feedback():
    conn = get_sqlite_connection()
    df = pd.read_sql("SELECT * FROM feedback", conn)
    conn.close()
    return df
def save_feedback(name, feedback_text):
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (name, feedback, submitted_on)
            VALUES (?, ?, ?)
        """, (name, feedback_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    except Exception as e:
        print(f"Error saving feedback: {e}")
    finally:
        conn.close()

def load_veterinarians():
    conn = get_sqlite_connection()
    df = pd.read_sql("SELECT * FROM veterinarians", conn)
    conn.close()
    return df

def save_veterinarian(name, specialization, phone, email):
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO veterinarians (name, specialization, phone, email, registered_on)
            VALUES (?, ?, ?, ?, ?)
        """, (name, specialization, phone, email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    except Exception as e:
        print(f"Error saving veterinarian: {e}")
    finally:
        conn.close()

def load_vet_requests():
    conn = get_sqlite_connection()
    df = pd.read_sql("SELECT * FROM vet_requests", conn)
    conn.close()
    return df

def save_vet_request(farmer_name, animal_tag, vet_id, request_reason):
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO vet_requests (farmer_name, animal_tag, vet_id, request_reason, requested_on)
            VALUES (?, ?, ?, ?, ?)
        """, (farmer_name, animal_tag, vet_id, request_reason, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    except Exception as e:
        print(f"Error saving vet request: {e}")
    finally:
        conn.close()

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
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.barcode import code128
from PIL import Image
from reportlab.lib.units import inch
import datetime

def display_diagnosis(animal_data, disease, recommendation):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    styles = getSampleStyleSheet()

    # --- Custom Styles ---
    centered_title_style = ParagraphStyle(
        name='CenteredTitle',
        parent=styles['Heading2'],
        alignment=1,
        fontName='Times-Roman',
        fontSize=16,
        textColor=colors.green,
        leading=24
    )

    table_heading_style = ParagraphStyle(
        name='TableHeading',
        parent=styles['Heading3'],
        alignment=1,
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.black,
        leading=24
    )

    # --- Header with Logo and Title ---
    try:
        logo_path = "logoo.png"
        c.drawImage(logo_path, inch, height - 60, width=100, height=50)
    except Exception:
        c.setFont("Helvetica", 12)
        c.drawString(inch, height - 50, "Logo could not be loaded")

    c.setFillColor(colors.green)
    c.rect(0, height - 45, width, 45, fill=True)
    c.setFillColor(colors.white)
    c.setFont("Times-Roman", 18)
    c.drawCentredString(width / 2, height - 30, "VetSmart Diagnosis Report")

    # --- Animal Information Section ---
    p = Paragraph("<b>Animal Information</b>", table_heading_style)
    text_width, text_height = p.wrap(width - 3 * inch, height)
    x = (width - text_width) / 2
    p.drawOn(c, x, height - 90)

    animal_table_data = [
        ["Animal Tag:", animal_data["Name"]],
        ["Type:", animal_data["Type"]],
        ["Age (years):", animal_data["Age"]],
        ["Weight (kg):", animal_data["Weight"]]
    ]

    animal_table = Table(animal_table_data, colWidths=[2 * inch, 3.5 * inch], hAlign='CENTER')
    animal_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEADING', (0, 0), (-1, -1), 20),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT')
    ]))
    animal_table.wrapOn(c, width, height)
    animal_table.drawOn(c, width / 2 - 2.25 * inch, height - 250)

    # --- Diagnosis Section ---
    p2 = Paragraph("<b>Diagnosis</b>", table_heading_style)
    text_width, text_height = p2.wrap(width - 2 * inch, height)
    x = (width - text_width) / 2
    p2.drawOn(c, x, height - 290)

    diagnosis_table_data = [
        ["Predicted Diagnosis:", disease],
        ["Recommendation:", recommendation]
    ]

    diagnosis_table = Table(diagnosis_table_data, colWidths=[2 * inch, 3.5 * inch], hAlign='CENTER')
    diagnosis_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEADING', (0, 0), (-1, -1), 20),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT')
    ]))
    diagnosis_table.wrapOn(c, width, height)
    diagnosis_table.drawOn(c, width / 2 - 2.75 * inch, height - 380)

    # --- Barcode Section ---
    barcode_value = f"VS-DR-{animal_data['Name']}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    barcode = code128.Code128(barcode_value, barHeight=0.75 * inch)
    barcode_width = barcode.wrap(0, 0)[0]
    x_position = width - barcode_width - inch
    y_position = inch
    barcode.drawOn(c, x_position, y_position)
    c.setFont("Helvetica", 8)
    c.drawString(x_position, y_position - 0.2 * inch, "VetSmart Authenticated")
    c.drawString(x_position, y_position - 0.4 * inch, barcode_value)

    # --- Footer ---
    c.setFont("Helvetica", 8)
    c.drawString(inch, 0.75 * inch, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(inch, 0.6 * inch, "Powered by VetSmart")

    c.save()
    buffer.seek(0)
    return buffer

# ========== Page Functions ==========
def display_add_livestock():
    """Displays the livestock dashboard and add animal form."""
    st.subheader("📋 Register Your Livestock")

    # Form for adding livestock
    with st.form("livestock_form", clear_on_submit=True):
        name = st.text_input("Animal Tag")
        animal_types = ["-- Select Type --", "Cattle", "Goat", "Sheep"]
        animal_type = st.selectbox("Type", animal_types)
        age = st.number_input("Age (years)", 0.0, 20.0)
        weight = st.number_input("Weight (kg)", 0.0, 1000.0)
        vaccination = st.text_input("Vaccination Details")
        submitted = st.form_submit_button("Add Livestock")

        if submitted:
            if animal_type == "-- Select Type --" or not name:
                st.warning("Please fill in all required fields.")
            else:
                save_livestock_data(name, animal_type, age, weight, vaccination)
                st.success(f"{animal_type} '{name}' saved successfully!")

def display_view_livestock():
    """Displays all registered livestock with filters, sorting, and export."""
    st.subheader("🐐🐑🐄 View All Your Livestock")

    df = load_data()

    if df.empty:
        st.info("No livestock records found.")
        return

    # --- Filter section ---
    with st.expander("🔍 Filter Records"):
        animal_types = ["All"] + sorted(df["Type"].dropna().unique())
        selected_type = st.selectbox("Filter by Animal Type", animal_types)

        search_tag = st.text_input("Search by Animal Tag")

        # Sorting options
        sort_column = st.selectbox("Sort By", ["None", "Age", "Weight"])
        sort_order = st.radio("Sort Order", ["Ascending", "Descending"], horizontal=True)

    # --- Apply filters ---
    filtered_df = df.copy()

    if selected_type != "All":
        filtered_df = filtered_df[filtered_df["Type"] == selected_type]

    if search_tag:
        filtered_df = filtered_df[filtered_df["Name"].str.contains(search_tag, case=False)]

    # --- Apply sorting ---
    if sort_column != "None":
        ascending = sort_order == "Ascending"
        filtered_df = filtered_df.sort_values(by=sort_column, ascending=ascending)

    # --- Display results ---
    if filtered_df.empty:
        st.warning("No matching records found.")
    else:
        st.dataframe(filtered_df)

        # --- Export button ---
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_livestock_records.csv",
            mime="text/csv"
        )

def display_dashboard(selected_type, search_tag, sort_column, sort_order):
    st.subheader("📊 Monitor Your Livestock Insights")

    # Load data
    df = load_data()

    if df.empty:
        st.info("No livestock records found. Please add livestock data to see insights.")
        return

    # --- Apply Filters ---
    filtered_df = df.copy()

    if selected_type != "All" and "type" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["type"] == selected_type]

    if search_tag and "name" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["name"].str.contains(search_tag, case=False, na=False)]

    if sort_column != "None" and sort_column in filtered_df.columns:
        ascending = sort_order == "Ascending"
        filtered_df = filtered_df.sort_values(by=sort_column, ascending=ascending)

    # --- Handle No Matching Records ---
    if filtered_df.empty:
        st.warning("No matching records found.")
        return

    # --- Display Filtered Data ---
    st.markdown("### 📋 Filtered Livestock Records")
    display_columns = ['name', 'type', 'age', 'weight', 'vaccination', 'added_on']
    available_columns = [col for col in display_columns if col in filtered_df.columns]
    st.dataframe(filtered_df[available_columns])

    # --- Charts Section ---
    if "type" in filtered_df.columns:
        type_counts = filtered_df['type'].value_counts().reset_index()
        type_counts.columns = ['Type', 'Count']

        # Bar chart
        fig_type = px.bar(
            type_counts, x='Type', y='Count', title='Livestock Count by Type', color='Type',
            labels={'Type': 'Animal Type', 'Count': 'Number of Animals'}
        )
        st.plotly_chart(fig_type, use_container_width=True)

        # Pie chart
        fig_pie = px.pie(
            type_counts, names='Type', values='Count', title='Livestock Distribution by Type'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Scatter plot - Age vs Weight
    if {'age', 'weight', 'type'}.issubset(filtered_df.columns):
        fig_scatter = px.scatter(
            filtered_df, x='age', y='weight', color='type', size='weight',
            hover_data=['name'], title='Age vs Weight of Livestock'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --- Summary Statistics ---
    st.markdown("### 📈 Summary Statistics")
    avg_age = filtered_df['age'].dropna().mean() if 'age' in filtered_df.columns else None
    avg_weight = filtered_df['weight'].dropna().mean() if 'weight' in filtered_df.columns else None
    total_livestock = filtered_df.shape[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total Livestock", total_livestock)
    col2.metric("📊 Average Age (yrs)", f"{avg_age:.2f}" if avg_age is not None else "N/A")
    col3.metric("⚖️ Average Weight (kg)", f"{avg_weight:.2f}" if avg_weight is not None else "N/A")

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

def display_register_vet():
    st.subheader("👨‍⚕️ Register as a Veterinary Doctor")
    with st.form("vet_registration", clear_on_submit=True):
        name = st.text_input("Full Name")
        specialization_options = ["-- Select Specialization --", "Cattle", "Goat", "Sheep", "General"]
        specialization = st.selectbox("Specialization", specialization_options)
        phone = st.text_input("Phone Number")
        email = st.text_input("Email Address")
        submitted = st.form_submit_button("Register")

        if submitted:
            if specialization == "-- Select Specialization --":
                st.warning("Please select a valid specialization.")
            elif not name.strip():
                st.warning("Name cannot be empty.")
            elif not phone.strip():
                st.warning("Phone number cannot be empty.")
            elif not email.strip():
                st.warning("Email cannot be empty.")
            else:
                conn = get_sqlite_connection()
                conn.execute("""
                    INSERT INTO veterinarians (name, specialization, phone, email, registered_on)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, specialization, phone, email, datetime.datetime.now()))
                conn.commit()
                conn.close()
                st.success("Veterinarian registered successfully!")

def display_daily_health_tips():
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

def request_vet_service():
    st.subheader("📞 Request Veterinary Services")
    conn = get_sqlite_connection()
    vets = pd.read_sql("SELECT * FROM veterinarians", conn)

    if vets.empty:
        st.info("No registered veterinarians available at the moment.")
        return

    vet_names = ["-- Select a Vet --"] + vets['name'].tolist()

    with st.form("vet_service_form", clear_on_submit=True):
        farmer_name = st.text_input("Your Name")
        animal_tag = st.text_input("Animal Tag (e.g., from your livestock record)")
        selected_vet = st.selectbox("Select a Vet", vet_names)
        request_reason = st.text_area("Reason for Request")
        submitted = st.form_submit_button("Submit Request")

        if submitted:
            if selected_vet == "-- Select a Vet --":
                st.warning("Please select a valid vet before submitting.")
            else:
                vet_id = vets[vets['name'] == selected_vet]['id'].values[0]
                conn.execute("""
                    INSERT INTO vet_requests (farmer_name, animal_tag, vet_id, request_reason, requested_on)
                    VALUES (?, ?, ?, ?, ?)
                """, (farmer_name, animal_tag, vet_id, request_reason, datetime.datetime.now()))
                conn.commit()
                st.success("Vet service requested successfully!")

    conn.close()

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
    
# =================================================== Main =======================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["🐐Add Livestock", "🐑🐐🐄View Livestock", "🩺Diagnosis", "💡Daily Health Tips", "👨‍⚕️Vet Doc", "📞Request Service", "📊Dashboard", "📝 Feedback"])

with tab1:
    display_add_livestock()
with tab2:
    display_view_livestock()
with tab3:
    display_diagnosis()
with tab4:
    display_daily_health_tips()
with tab5:
    display_register_vet()
with tab6:
    request_vet_service()
# with tab7:
#    display_dashboard()
with tab8:
    handle_feedback_submission()

chatbot_widget()

# ========== Sidebar ==========
with st.sidebar:
    st.image("https://img.icons8.com/emoji/96/cow-emoji.png", width=80)
    st.markdown("## Livestock Focus")
    st.markdown("""
    - **Cattle**
    - **Goat**
    - **Sheep**
    """)

    st.markdown("## About VetSmart")
    st.markdown("""
    **VetSmart** is an AI-powered livestock health monitoring, disease prevention, and diagnosis app designed to support farmers and veterinary experts.

    **Key Features:**
    - Livestock registration  
    - Disease prediction based on symptoms  
    - Vaccination records  
    - Downloadable diagnosis reports  

    These features enhance the efficiency and accuracy of animal healthcare decisions.

    ## 👥Contributors
    - **Ezekiel BALOGUN** — *Data Scientist / Lead*  
    - **Oluwakemi Adesanwo** — *Data Analyst*  
    - **Damilare Abayomi** — *Software Developer*  
    - **Boluwatife Adeagbo** — *Veterinary Doctor*
    """)

# ================VetChat==================
# ========== Simple Rule-Based Chatbot ==========
def chatbot_response(user_input):
    responses = {
        "hello": "Hi there! How can I assist you with your livestock today?",
        "hi": "Hello! What would you like help with?",
        "how are you": "I'm just AI-VetChat, your animal health assistant, but I'm well trained and functioning properly!",
        "disease": "You can go to the Diagnosis tab to analyze your animal symptoms.",
        "vaccination": "Vaccination records can be managed in the Dashboard tab.",
        "bye": "Goodbye! Monitor your animal health regularly!",
        "thank you": "You're welcome! I'm here to support your livestock needs.",
        "thanks": "Glad I could help! Let me know if you need anything else.",
        "help": "Sure! You can ask about disease, feeding, breeding or medication.",
        "what can you do": "I can help track health, feeding, vaccination, and suggest care tips for your animals.",
        "symptom checker": "Use the 'Diagnosis' tab to enter symptoms and get insights.",
        "medication": "Go to the 'Medication History' section to add or view past treatments.",
        "health tips": "Check daily health tips for your livestock on the Health Tips tab.",
        "heat detection": "Use the 'Breeding Records' to note and monitor heat cycles.",
        "track health": "Go to 'Health Monitoring' for trends and medical logs.",
        "pasture rotation": "Check the 'Feeding & Grazing' tips for best pasture practices.",
        "temperature": "The normal body temperature for a cow is between 101.5°F and 103.5°F (38.6°C - 39.7°C)",
        "not eating": "Loss of appetite may be due to heat stress, illness, pain, poor-quality feed. Diagnose your animal symptoms on the Diagnosis tab.",
        "deworm": "Generally, cattle should be dewormed 2–4 times a year, depending on local parasite load, grazing conditions.",
        "milk production in my dairy cow?": "Ensure proper nutrition (high-quality forage and supplements), regular milking, clean water access, and stress-free housing.",
        "diet for goats": "Goats thrive on a mix of good-quality hay, browse (leaves, twigs), grains, minerals, and clean water. Avoid moldy feed.",
        "goat coughing": "Common causes include respiratory infections (like pneumonia), dusty feed, or lungworms. Isolate and consult a vet.",
        "vaccinate": "Livestock should be vaccinated regularly. Goats should receive the CDT (Clostridium perfringens C & D and tetanus) vaccine initially at 6–8 weeks, with boosters annually.",
        "sign of pregnancy": "Signs include increased appetite, abdominal enlargement, and behavior change. Take proper care of your animal at this time.",
        "causes of bloating in goats": "Rapid consumption of lush legumes, overeating grain, or digestive blockage. Try gentle walking or simethicone. Severe cases need a vet.",
        "ideal temperature range for sheep": "Normal temperature is about 102.3°F (39.1°C), give or take a degree.",
        "how often should sheep be sheared": "At least once a year, typically in spring, to keep them comfortable and avoid overheating.",
        "what are common diseases in sheep": "Foot rot, pneumonia, enterotoxemia (overeating disease), and internal parasites are prevalent. Prevent with vaccines and hygiene.",
        "how do i treat foot rot in sheep": "Trim the hoof, clean the wound, and soak the foot in a zinc sulfate solution. Isolate affected animals.",
        "why is my sheep limping": "Likely causes: foot rot, injuries, or joint infections. Check the hoof for wounds or swelling.",
    }
    return responses.get(user_input.lower(), "I'm not sure how to help with that. Try asking about animal health, feeding, or vaccinations.")

def chatbot_widget():
    st.markdown("""
        <style>
        #vetchat-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #2c6d37;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            z-index: 1001;
        }

        #vetchat-container {
            position: fixed;
            bottom: 70px;
            right: 20px;
            background-color: #f0f2f6;
            border: 1px solid #ccc;
            padding: 15px;
            width: 300px;
            height: 350px;
            overflow-y: auto;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
            z-index: 1000;
        }
        </style>
    """, unsafe_allow_html=True)

    if "vetchat_open" not in st.session_state:
        st.session_state.vetchat_open = False

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    toggle = st.button("💬 VetChat", key="vetchat-toggle")

    if toggle:
        st.session_state.vetchat_open = not st.session_state.vetchat_open

    if st.session_state.vetchat_open:
        st.markdown('<div id="vetchat-container">', unsafe_allow_html=True)
        st.markdown("**🗨️ Ask me anything about livestock care!**")

        for sender, message in st.session_state.chat_history:
            if sender == "You":
                st.markdown(f"**You:** {message}")
            else:
                st.markdown(f"🤖 **VetChat:** {message}")

        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Ask VetChat:", key="chat_input", label_visibility="collapsed")
            submitted = st.form_submit_button("Send")
            if submitted and user_input:
                st.session_state.chat_history.append(("You", user_input))

                placeholder = st.empty()
                placeholder.markdown("🤖 **VetChat:** _typing..._")
                time.sleep(1.5)

                response = chatbot_response(user_input)
                placeholder.markdown(f"🤖 **VetChat:** {response}")
                st.session_state.chat_history.append(("VetChat", response))

        st.markdown("</div>", unsafe_allow_html=True)

# Run the chatbot

# ======================RasaVetChat=============================
import streamlit as st
import streamlit.components.v1 as components
import requests
import openai
import streamlit_js_eval

# Set OpenAI API Key
# openai.api_key = 'YOUR_OPENAI_API_KEY'

# Initialize session state if not already present
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to interact with OpenAI API
# def get_openai_response(user_input):
#    # Call OpenAI API to generate a response
#    response = openai.Completion.create(
#        engine="text-davinci-003",
#        prompt=user_input,
#        max_tokens=150
#    )
#    return response.choices[0].text.strip()

# Function to interact with Rasa API
def get_rasa_response(user_input):
    # Send the user input to the Rasa server for a response
    rasa_url = "http://localhost:5005/webhooks/rest/webhook"
    payload = {"message": user_input}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(rasa_url, json=payload, headers=headers)
    response_json = response.json()

    if response_json:
        return response_json[0]['text']
    else:
        return "Sorry, I didn't understand that."

# Custom HTML + JS + CSS to float the chatbot
chat_html = f"""
<style>
    #chat-container {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 300px;
        max-height: 400px;
        background-color: #f5f5f5;
        border: 1px solid #ccc;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.3);
        display: flex;
        flex-direction: column;
        z-index: 9999;
        resize: both;
        overflow: hidden;
    }}
    #chat-header {{
        background-color: #2e7bcf;
        color: white;
        padding: 10px;
        cursor: move;
        user-select: none;
        font-weight: bold;
    }}
    #chat-messages {{
        flex: 1;
        padding: 10px;
        overflow-y: auto;
        display: flex;
        flex-direction: column-reverse;
    }}
    #chat-input {{
        display: flex;
        padding: 10px;
        border-top: 1px solid #ccc;
    }}
    #chat-input input {{
        flex: 1;
        padding: 5px;
    }}
    #chat-input button {{
        margin-left: 5px;
        padding: 5px 10px;
    }}
</style>

<div id="chat-container">
    <div id="chat-header" onclick="toggleChat()">💬 VetChat</div>
    <div id="chat-body">
        <div id="chat-messages">
            {"".join([f"<div><b>{s}:</b> {m}</div>" for s, m in reversed(st.session_state.chat_history)])}
        </div>
        <div id="chat-input">
            <input type="text" id="user-input" placeholder="Ask VetChat..." />
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>
</div>

<script>
    let dragging = false;
    let offset = [0, 0];
    const chatBox = document.getElementById("chat-container");
    const header = document.getElementById("chat-header");

    header.addEventListener("mousedown", function(e) {{
        dragging = true;
        offset = [
            chatBox.offsetLeft - e.clientX,
            chatBox.offsetTop - e.clientY
        ];
    }});

    document.addEventListener("mouseup", function() {{
        dragging = false;
    }});

    document.addEventListener("mousemove", function(e) {{
        e.preventDefault();
        if (dragging) {{
            chatBox.style.left = (e.clientX + offset[0]) + "px";
            chatBox.style.top = (e.clientY + offset[1]) + "px";
        }}
    }});

    function toggleChat() {{
        const body = document.getElementById("chat-body");
        body.style.display = body.style.display === "none" ? "block" : "none";
    }}

    function sendMessage() {{
        const input = document.getElementById("user-input");
        const msg = input.value;
        if (msg) {{
            window.parent.postMessage({{type: "chatMessage", message: msg}}, "*");
            input.value = "";
        }}
    }}

    window.addEventListener("message", (event) => {{
        if (event.data.type === "updateChat") {{
            const chatDiv = document.getElementById("chat-messages");
            chatDiv.innerHTML = event.data.html;
        }}
    }});
</script>
"""

# Display the chat HTML
components.html(chat_html, height=500, width=0)

# Handling the user input and response
event = streamlit_js_eval.streamlit_js_eval(js_expressions="parent.postMessage({ type: 'ready' }, '*')", key="chat_eval")

if event and event.get("type") == "chatMessage":
    user_input = event.get("message", "")
    if user_input:
        # Use Rasa or OpenAI to get a response
        # Uncomment the next line to use Rasa
        # response = get_rasa_response(user_input)
        
        # Use OpenAI for response generation
        response = get_openai_response(user_input)

        # Store the user input and response in the chat history
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("VetChat", response))

        # Trigger JS to update the chat window dynamically
        chat_update = "".join([f"<div><b>{s}:</b> {m}</div>" for s, m in reversed(st.session_state.chat_history)])
        st.components.v1.html(f"<script>window.parent.postMessage({{type: 'updateChat', html: `{chat_update}`}}, '*');</script>", height=0)
