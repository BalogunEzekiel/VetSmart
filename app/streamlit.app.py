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

# ========================PDF Report ===========================
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.barcode import code128
import datetime
from reportlab.lib.units import inch


def generate_diagnosis_report(animal_data, disease, recommendation):
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

    # --- Header with Title Only (Logo removed) ---
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
        ('ALIGN', (0, 0), (-1, -1), 'CENTRE')
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
        ('ALIGN', (0, 0), (-1, -1), 'CENTRE')
    ]))
    diagnosis_table.wrapOn(c, width, height)
    diagnosis_table.drawOn(c, width / 2 - 2.75 * inch, height - 380)

    # --- Place Logo on Top-Right Corner ---
    try:
        logo_path = "logoo.png"
        c.drawImage(logo_path, width - inch - 100, height - 60, width=100, height=50)
    except Exception:
        c.setFont("Helvetica", 12)
        c.drawString(width - inch - 100, height - 50, "Logo could not be loaded")

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

    # --- Footer (Permanent across pages) ---
    def draw_footer():
        c.setFont("Helvetica", 8)
        c.drawString(inch, 0.75 * inch, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(inch, 0.6 * inch, "Powered by VetSmart")

    # Draw footer
    draw_footer()

    # Save and return PDF
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
    st.subheader("🐐🐑🐄 View Your Livestock")

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

# ========== Dashboard Function ==========
def display_dashboard():
    st.subheader("📊 Livestock Dashboard")

    df = load_data()

    if df.empty:
        st.info("No livestock records found. Please add livestock data.")
        return

    # Rename columns if needed
    df.rename(columns={"animal_type": "Type", "age": "Age", "weight": "Weight", "vaccination": "Vaccination", "name": "Name", "added_on": "Date Added"}, inplace=True)

    # Show raw data
    with st.expander("View Raw Data"):
        st.dataframe(df)

    # Summary statistics
    st.markdown("### Summary Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Animals", len(df))
    with col2:
        st.metric("Average Age", round(df["Age"].mean(), 1))
    with col3:
        st.metric("Average Weight (kg)", round(df["Weight"].mean(), 1))

    # Animal Type Distribution
    st.markdown("### Animal Type Distribution")
    fig1 = px.pie(df, names="Type", title="Distribution by Animal Type")
    st.plotly_chart(fig1, use_container_width=True)

    # Age vs Weight Scatter Plot
    st.markdown("### Age vs. Weight")
    fig2 = px.scatter(df, x="Age", y="Weight", color="Type", hover_data=["Name", "Vaccination"])
    st.plotly_chart(fig2, use_container_width=True)

    # Vaccination Count
    st.markdown("### Vaccination Overview")
    vaccinated = df[df["Vaccination"].notnull()]
    fig3 = px.histogram(vaccinated, x="Vaccination", color="Type", title="Vaccination Count by Type", barmode="group")
    st.plotly_chart(fig3, use_container_width=True)

    # Bar chart for average weight by type
    weight_by_type = df.groupby("Type")["Weight"].mean().reset_index()
    fig2 = px.bar(weight_by_type, x="Type", y="Weight", color="Type", title="Average Weight by Animal Type")
    st.plotly_chart(fig2, use_container_width=True)

    # Line chart for livestock added over time
    df["Added On"] = pd.to_datetime(df["Added On"])
    added_over_time = df.groupby(df["Added On"].dt.date).size().reset_index(name='Count')
    fig3 = px.line(added_over_time, x="Added On", y="Count", title="Livestock Added Over Time")
    st.plotly_chart(fig3, use_container_width=True)

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
    with st.form("feedback_form", clear_on_submit=True):
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
with tab7:
    display_dashboard()
with tab8:
    handle_feedback_submission()
# Run the chatbot widget
def chatbot_widget():
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
# ========== Simple Ru]le-Based Chatbot ==========
