import streamlit as st

# ========== Page Setup ==========
st.set_page_config(page_title="VetSmart", layout="wide")

import pandas as pd
from datetime import datetime
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
import bcrypt
import re


# ========== Database Configuration ==========
SQLITE_DB = 'livestock_data.db'

# ========== Database Connection Functions ==========
def get_sqlite_connection():
    return sqlite3.connect(SQLITE_DB)

# ========== Initialize Database and Tables ==========
def initialize_database():
    conn = get_sqlite_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL, 
            telephone TEXT NOT NULL,
            farmname TEXT NOT NULL,
            farmaddress TEXT NOT NULL,
            farmrole TEXT NOT NULL,
            registered_on DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create livestock table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS livestock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            animal_type TEXT NOT NULL,
            age REAL NOT NULL,
            weight REAL NOT NULL,
            vaccination TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            added_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Create feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            feedback TEXT NOT NULL,
            submitted_on DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create veterinarians table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS veterinarians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            registered_on DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create vet_requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vet_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_name TEXT NOT NULL,
            animal_tag TEXT NOT NULL,
            vet_id INTEGER NOT NULL,
            request_reason TEXT NOT NULL,
            requested_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(vet_id) REFERENCES veterinarians(id)
        )
    """)

    conn.commit()
    conn.close()

# Call the function to initialize the database
initialize_database()

# ========== Load & Save Data Functions ==========
# Users
def load_users():
    conn = get_sqlite_connection()
    df = pd.read_sql("SELECT * FROM users", conn)
    conn.close()
    return df

def save_users(role, firstname, lastname, email, password, telephone, farmname, farmaddress, farmrole):
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (role, firstname, lastname, email, password, telephone, farmname, farmaddress, farmrole, registered_on)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (role, firstname, lastname, email, password, telephone, farmname, farmaddress, farmrole, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    except Exception as e:
        print(f"Error saving users: {e}")
    finally:
        conn.close()

# Livestock
def load_data(user_id=None):
    try:
        conn = get_sqlite_connection()
        if user_id is not None:
            df = pd.read_sql(f"SELECT * FROM livestock WHERE user_id = ?", conn, params=(user_id,))
        else:
            df = pd.read_sql("SELECT * FROM livestock", conn)
        conn.close()

        # Rename columns for consistency
        df.rename(columns={
            "animal_type": "Type",
            "name": "Name",
            "age": "Age",
            "weight": "Weight",
            "vaccination": "Vaccination",
            "added_on": "Date Added"
        }, inplace=True)

        return df
    except FileNotFoundError:
        return pd.DataFrame()
        
def save_livestock_data(name, animal_type, age, weight, vaccination, user_id):
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO livestock (name, animal_type, age, weight, vaccination, user_id, added_on)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, animal_type, age, weight, vaccination, user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    except Exception as e:
        print(f"Error saving livestock data: {e}")
    finally:
        conn.close()

# Feedback
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

# Veterinarians
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

# Vet Requests
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

# ================================== Landing / Login Page ======================================================
# Background image
def set_background(cow_background):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("cow_background")

# Session State Init
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

# -- Database connection helper --
def get_sqlite_connection():
    return sqlite3.connect("livestock_data.db")

# -- Password strength checker --
def password_strength(pw):
    length = len(pw)
    has_upper = bool(re.search(r'[A-Z]', pw))
    has_special = bool(re.search(r'[\W_]', pw))
    score = 0
    if length >= 6:
        score += 1
    if has_upper:
        score += 1
    if has_special:
        score += 1
    return score

def password_strength_message(score):
    if score == 0:
        return "Password is too weak.", "red"
    elif score == 1:
        return "Password is weak.", "orange"
    elif score == 2:
        return "Password is moderate.", "yellow"
    else:
        return "Password is strong.", "green"

# ---------------- MAIN AUTH SECTION ----------------
if not st.session_state.logged_in:
    with st.container():
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔐 Login"):
                st.session_state.show_login = not st.session_state.show_login
                st.session_state.show_signup = False  # hide other
        with col_btn2:
            if st.button("🆕 Signup"):
                st.session_state.show_signup = not st.session_state.show_signup
                st.session_state.show_login = False  # hide other

    if st.session_state.show_login:
        with st.container():
            st.subheader("🔐 Login")
            login_user = st.text_input("Email", key="login_user")
            login_pwd = st.text_input("Password", type="password", key="login_pwd")

            if st.button("Login", key="login_btn"):
                if not login_user or not login_pwd:
                    st.warning("Please enter both email and password.")
                else:
                    try:
                        conn = get_sqlite_connection()
                        c = conn.cursor()
                        c.execute("SELECT Password, Role, Firstname, Lastname, id FROM users WHERE Email = ?", (login_user,))
                        row = c.fetchone()

                        if row and bcrypt.checkpw(login_pwd.encode('utf-8'), row[0].encode('utf-8')):
                            st.session_state['logged_in'] = True
                            st.session_state['user_role'] = row[1]
                            st.session_state['user_name'] = f"{row[2]} {row[3]}"
                            st.session_state['user_id'] = row[4] # This is the crucial line to add
                            st.success(f"Logged in as {row[2]} {row[3]} ({row[1]})")
                            st.rerun()
                        else:
                            st.error("Login failed: Invalid email or password.")
                    except Exception as e:
                        st.error(f"Database error: {e}")
                    finally:
                        conn.close()
                        
    user_id = st.session_state.get("user_id")

    if st.session_state.show_signup:
        with st.container():
            st.subheader("🆕 New User? Register")

            with st.form("signup_form", clear_on_submit=True):
                role         = st.selectbox("Role", ["-- Choose you role --", "Farmer", "Veterinarian", "Admin"])
                firstname    = st.text_input("First Name")
                lastname     = st.text_input("Last Name")
                email        = st.text_input("Email")
                password     = st.text_input("Password", type="password", key="password_input")

                if password:
                    score = password_strength(password)
                    msg, color = password_strength_message(score)
                    st.markdown(f"<span style='color:{color}; font-weight:bold'>{msg}</span>", unsafe_allow_html=True)
                    st.progress(score / 3)

                confirm      = st.text_input("Confirm Password", type="password")
                telephone    = st.text_input("Telephone")
                farm_name    = st.text_input("Farm Name")
                farm_address = st.text_input("Farm Address")
                farm_role    = st.text_input("Farm Role (e.g., owner, worker)")
                submitted    = st.form_submit_button("Register")

                if submitted:
                    try:
                        if not all([firstname, lastname, email, password, confirm, telephone, farm_name, farm_address, farm_role]):
                            st.error("All fields are required.")
                        elif password != confirm:
                            st.error("Passwords do not match.")
                        elif password_strength(password) < 3:
                            st.error("Password must be at least 6 characters, with uppercase and special character.")
                        else:
                            conn = get_sqlite_connection()
                            c = conn.cursor()
                            c.execute("SELECT * FROM users WHERE email = ?", (email,))
                            if c.fetchone():
                                st.error("Email already used.")
                            else:
                                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                                c.execute('''
                                    INSERT INTO users 
                                    (role, firstname, lastname, email, password, telephone, farmname, farmaddress, farmrole, registered_on)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (role, firstname, lastname, email, hashed.decode('utf-8'),
                                      telephone, farm_name, farm_address, farm_role,
                                      datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                                conn.commit()
                                conn.close()
                                st.success(f"User '{email}' registered successfully! You can now log in.")
                                st.session_state['show_signup'] = False
                    except Exception as e:
                        st.error(f"Registration failed: {e}")
                    
# Header
# --- NOT LOGGED IN ---
if not st.session_state.logged_in:
    col1, col2 = st.columns([1, 6])
    
    with col1:
        st.image("logoo.png", width=100)
    
    with col2:
        st.markdown("<h1 style='color:black;'>Welcome to VetSmart</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:black;'>...revolutionizing the livestock sector with AI</h4>", unsafe_allow_html=True)

    st.markdown("---")

    # About Section
    st.markdown("## About VetSmart")
    st.markdown("""
        VetSmart is an AI-driven platform that connects farmers with veterinarians, enabling predictive health monitoring,
        data-driven livestock management, and seamless veterinary services.
    """)

    # New: Three columns of text boxes
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("##### Our Vision")
        st.markdown("""
        To be the leading force in transforming animal health through innovative, tech-driven veterinary solutions that empower farmers, veterinarians and communities globally.
        """)
    
    with col2:
        st.markdown("##### Our Mission")
        st.markdown("""
        We are revolutionizing livestock care by combining medical expertise, artificial intelligence and sustainable practices – delivering smart, accessible and impactful solutions that improve animal health, productivity and livelihoods.
        """)
    
    with col3:
        st.markdown("##### Call")
        st.markdown("""
        **Our logo reflects our unique identity — inspired by livestock healthtech, powered by medical expertise and curated through advanced AI — symbolizing our commitment to innovation in agri-health technology.** Join us on this quest as we take the world by storm!
        """)
        
    # Contributors
    st.markdown("### Contributors")
    
    contributors = {
        "Balogun Ezekiel": "Data Scientist",
        "Adesanwo Oluwakemi": "Data Analyst",
        "Abayomi Damilare": "Software Developer"
    }
    
    for name, role in contributors.items():
        st.markdown(f"- **{name}** — *{role}*")
        
if not st.session_state.get('logged_in'):
    st.markdown("---")
    st.markdown("### 🤝 Supporters & Partners", unsafe_allow_html=True)

    logos = [
        "assets/Partner_FMCIDE.png",
        "assets/Partner_DSN.png",
        "assets/Partner_Google.png",
        "assets/Partner_Microsoft.png"
    ]

    # Display logos in rows of 4
    for i in range(0, len(logos), 4):
        cols = st.columns(4)
        for j, logo in enumerate(logos[i:i+4]):
            with cols[j]:
                try:
                    st.image(logo, width=120)  # Adjust width as needed
                except Exception as e:
                    st.warning(f"Could not load logo: {e}")

    st.markdown("---")

if st.session_state.get('logged_in'):
    # ========== Centered Logo ==========
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
    barcode_value = f"VS-DR-{animal_data['Name']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
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
        c.drawString(inch, 0.75 * inch, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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

        user_id = st.session_state.get("user_id")

        if submitted:
            if animal_type == "-- Select Type --" or not name:
                st.warning("Please fill in all required fields.")
            else:
                save_livestock_data(name, animal_type, age, weight, vaccination, user_id)
                st.success(f"{animal_type} '{name}' saved successfully!")

def display_view_livestock():
    """Displays all registered livestock with filters, sorting, and export."""
    st.subheader("🐐🐑🐄 View Your Livestock")
    user_id = st.session_state.get("user_id")
    df = load_data(user_id=user_id)

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

def display_dashboard():
    st.subheader("📊 Livestock Dashboard")
    user_id = st.session_state.get("user_id")
    df = load_data(user_id=user_id)

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
    df["Added_On"] = pd.to_datetime(df["Added_On"])
    added_over_time = df.groupby(df["Added_On"].dt.date).size().reset_index(name='Count')
    fig3 = px.line(added_over_time, x="Added_On", y="Count", title="Livestock Added Over Time")
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
                """, (name, specialization, phone, email, datetime.now()))
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
                """, (farmer_name, animal_tag, vet_id, request_reason, datetime.now()))
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
                now = datetime.now()
                cursor.execute(query, (name, feedback_text, now))
                conn.commit()
                conn.close()
                st.success("Thank you for your feedback!")

# =================================================== Main =======================================================
import streamlit as st

# Define your role (you can fetch this from login logic or session state)
user_role = st.session_state.get("user_role", "Select")

# Function mapping for each tab
tab_functions = {
    "🐐Add Livestock": display_add_livestock,
    "🐑🐐🐄View Livestock": display_view_livestock,
    "🩺Diagnosis": display_diagnosis,
    "💡Daily Health Tips": display_daily_health_tips,
    "👨‍⚕️Vet Doc": display_register_vet,
    "📞Request Service": request_vet_service,
    "📊Dashboard": display_dashboard,
    "📝 Feedback": handle_feedback_submission
}

# Tabs by user role
tabs_by_role = {
    "Farmer": [
        "🐐Add Livestock",
        "🐑🐐🐄View Livestock",
        "🩺Diagnosis",
        "💡Daily Health Tips",
        "📞Request Service",
        "📊Dashboard",
        "📝 Feedback"
    ],
    "Veterinarian": [
        "🩺Diagnosis",
        "💡Daily Health Tips",
        "👨‍⚕️Vet Doc",
        "📝 Feedback"
    ],
    "Admin": [
        "🐐Add Livestock",
        "🐑🐐🐄View Livestock",
        "🩺Diagnosis",
        "💡Daily Health Tips",
        "👨‍⚕️Vet Doc",
        "📞Request Service",
        "📊Dashboard",
        "📝 Feedback"
    ]
}

# Show tabs only if user is logged in
if st.session_state.get('logged_in'):
    allowed_tabs = tabs_by_role.get(user_role, [])
    tabs = st.tabs(allowed_tabs)

    for tab_name, tab in zip(allowed_tabs, tabs):
        with tab:
            tab_functions[tab_name]()  # Call the corresponding function

    # Optional: chatbot widget (must avoid recursion)
    def chatbot_widget():
        # Your chatbot implementation here
        pass

    # Show chatbot widget
    chatbot_widget()

# ========== Sidebar ==========
if st.session_state.get('logged_in'):
    with st.sidebar:
        st.markdown(f"### 👋 Welcome, **{st.session_state.get('user_name', 'User')}**")

        if st.button("Logout", key="logout_button"):
            st.session_state['logged_in'] = False
            st.session_state['user_role'] = None
            st.session_state['user_name'] = ""
            st.rerun()

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

import streamlit as st
import time
import streamlit.components.v1 as components

# Inject custom HTML, CSS, and JS for floating, draggable, resizable, and minimizable window
components.html("""
<style>
#chat-widget {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 350px;
  height: 500px;
  background: #fff;
  border: 2px solid #ccc;
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0,0,0,0.3);
  overflow: hidden;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  resize: both;
}
#chat-header {
  background-color: #00a676;
  color: white;
  padding: 8px;
  cursor: move;
  font-weight: bold;
  text-align: center;
  user-select: none;
}
#chat-body {
  flex-grow: 1;
  padding: 10px;
  overflow-y: auto;
  font-family: sans-serif;
  font-size: 14px;
}
#chat-footer {
  padding: 8px;
  border-top: 1px solid #ccc;
}
.minimized {
  height: 40px !important;
}
</style>
<script>
let widget = null;
let header = null;
let offsetX = 0, offsetY = 0;
let isDragging = false;

window.onload = () => {
  widget = document.getElementById("chat-widget");
  header = document.getElementById("chat-header");

  header.ondblclick = () => {
    if (widget.classList.contains("minimized")) {
      widget.classList.remove("minimized");
    } else {
      widget.classList.add("minimized");
    }
  };

  header.onmousedown = function(e) {
    isDragging = true;
    offsetX = e.clientX - widget.getBoundingClientRect().left;
    offsetY = e.clientY - widget.getBoundingClientRect().top;

    document.onmousemove = function(e) {
      if (isDragging) {
        widget.style.left = (e.clientX - offsetX) + "px";
        widget.style.top = (e.clientY - offsetY) + "px";
        widget.style.right = "auto";
        widget.style.bottom = "auto";
      }
    };

    document.onmouseup = function() {
      isDragging = false;
    };
  };
};
</script>
<div id="chat-widget">
  <div id="chat-header">🐄 Livestock Health Chat</div>
  <div id="chat-body"><!-- Scrollable content loaded by Streamlit --></div>
</div>
""", height=0)

# Initialize messages session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Response logic
def get_livestock_response(user_input):
    user_input_lower = user_input.lower()
    if "fever" in user_input_lower:
        return "🤒 A fever in livestock can indicate an infection. Isolate the animal and consult a veterinarian."
    elif "diarrhea" in user_input_lower:
        return "💧 Diarrhea may result from parasites or poor diet. Keep the animal hydrated and call a vet."
    elif "not eating" in user_input_lower or "loss of appetite" in user_input_lower:
        return "😟 A loss of appetite could mean illness. Watch for other signs and contact an expert."
    elif "vaccination" in user_input_lower:
        return "💉 Vaccinations are essential. Ask a vet for a schedule tailored to your animals."
    elif "bloat" in user_input_lower:
        return "⚠️ Bloat is serious and life-threatening. Avoid risky feed and act fast — call your vet."
    else:
        return "🤔 Can you provide more information about your livestock’s symptoms or behavior?"

# Container for actual chat inside widget
with st.container():
    st.markdown("""
    <style>
    .chat-box { position: fixed; bottom: 90px; right: 45px; width: 320px; max-height: 370px; overflow-y: auto; background: #f8f8f8; padding: 10px; border-radius: 10px; font-size: 14px; }
    .user { font-weight: bold; color: #0072C6; margin-bottom: 4px; }
    .bot { font-weight: normal; color: #111; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

    chat_container = st.empty()

    def display_messages():
        chat_html = '<div class="chat-box">'
        for msg in st.session_state.messages:
            role_class = "user" if msg["role"] == "user" else "bot"
            chat_html += f'<div class="{role_class}">{msg["content"]}</div>'
        chat_html += "</div>"
        chat_container.markdown(chat_html, unsafe_allow_html=True)

    display_messages()

    # Chat input
    prompt = st.chat_input("Ask about livestock health...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        display_messages()

        # Simulate assistant typing
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("💭 Thinking...")
        time.sleep(1.5)

        response = get_livestock_response(prompt)
        slow_response = ""
        for char in response:
            slow_response += char
            thinking_placeholder.markdown(slow_response)
            time.sleep(0.03)

        st.session_state.messages.append({"role": "assistant", "content": response})
        thinking_placeholder.empty()
        display_messages()
