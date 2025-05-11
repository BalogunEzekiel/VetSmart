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

# ========== Centered Logo ==========

# Logo and title
try:
    logo = Image.open("logoo.png")
    col1, col2, col3 = st.columns([1, 6, 1])  # Create columns to structure the layout
    
    with col1:
        st.image(logo, width=150)  # Align logo to the left
        
    with col2:
        st.markdown("<h1 style='text-align: center;'>VetSmart</h1>", unsafe_allow_html=True)  # Centralized title
    
except Exception as e:
    st.warning(f"Logo could not be loaded: {e}")
    
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
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.graphics.barcode import code128
from PIL import Image
from reportlab.lib.units import inch
import datetime

def generate_diagnosis_report(animal_data, disease, recommendation):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    centered_title_style = ParagraphStyle(
        name='CenteredTitle',
        parent=styles['Heading1'],
        alignment=1,
        fontName='Times-Roman',
        fontSize=20,
        textColor=colors.green
    )

    # Header Customization (Logo + Title)
    try:
        logo = Image.open("logoo.png")
        c.drawImage("logoo.png", inch, letter[1] - 50, width=100, height=30)
    except Exception as e:
        c.setFont("Helvetica", 12)
        c.drawString(inch, letter[1] - 50, "Logo could not be loaded")

    # Title Header
    c.setFillColor(colors.green)
    c.rect(0, letter[1] - 45, letter[0], 45, fill=True)
    c.setFont("Times-Roman", 30)
    c.setFillColor(colors.white)
    c.drawString(150, letter[1] - 20, "VetSmart Diagnosis Report")

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.line(inch, letter[1] - 60, letter[0] - inch, letter[1] - 60)

    # Animal Info Section
    p = Paragraph("<b>Animal Information</b>", centered_title_style)
    p.wrapOn(c, letter[0] - 2 * inch, [1])
    p.drawOn(c, inch, letter[1] - 1.5 * inch)
    c.line(inch, letter[1] - 1.6 * inch, letter[0] - inch, letter[1] - 1.6 * inch)

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

    # Barcode
    barcode_value = f"VS-DR-{animal_data['Name']}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    barcode = code128.Code128(barcode_value, barHeight=0.75 * inch)
    barcode_width = barcode.wrap(0, 0)[0]
    x_position = letter[0] - barcode_width - inch
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

def register_vet():
    st.subheader("👨‍⚕️ Register as a Veterinary Doctor")
    with st.form("vet_registration"):
        name = st.text_input("Full Name")
        specialization = st.selectbox("Specialization", ["Cattle", "Goat", "Sheep", "General"])
        phone = st.text_input("Phone Number")
        email = st.text_input("Email Address")
        submitted = st.form_submit_button("Register")

        if submitted:
            conn = get_sqlite_connection()
            conn.execute("""
                INSERT INTO veterinarians (name, specialization, phone, email, registered_on)
                VALUES (?, ?, ?, ?, ?)
            """, (name, specialization, phone, email, datetime.datetime.now()))
            conn.commit()
            conn.close()
            st.success("Veterinarian registered successfully!")

def request_vet_service():
    st.subheader("📞 Request Veterinary Services")
    conn = get_sqlite_connection()
    vets = pd.read_sql("SELECT * FROM veterinarians", conn)

    if vets.empty:
        st.info("No registered veterinarians available at the moment.")
        return

    farmer_name = st.text_input("Your Name")
    animal_tag = st.text_input("Animal Tag (e.g., from your livestock record)")
    selected_vet = st.selectbox("Select a Vet", vets['name'].tolist())
    request_reason = st.text_area("Reason for Request")

    if st.button("Submit Request"):
        vet_id = vets[vets['name'] == selected_vet]['id'].values[0]
        conn.execute("""
            INSERT INTO vet_requests (farmer_name, animal_tag, vet_id, request_reason, requested_on)
            VALUES (?, ?, ?, ?, ?)
        """, (farmer_name, animal_tag, vet_id, request_reason, datetime.datetime.now()))
        conn.commit()
        st.success("Vet service requested successfully!")
    conn.close()

# ========================= Main =====================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Dashboard", "🩺 Diagnosis", "💡 Health Tips", "📝 Feedback", "Vet Doc", "Request Service"])
with tab1:
    display_dashboard()
with tab2:
    display_diagnosis()
with tab3:
    display_health_tips()
with tab4:
    handle_feedback_submission()
with tab5:
    register_vet()
with tab6:
    request_vet_service()

# ========== Sidebar ==========
with st.sidebar:
    st.sidebar.image("https://img.icons8.com/emoji/96/cow-emoji.png", width=80)
    st.markdown("## Livestock Focus:")
    st.markdown("""
    
👉 *Cattle*
    
👉 *Goat*
    
👉 *Sheep*
    """)    
    st.markdown("## About VetSmart")
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

import streamlit as st
import streamlit.components.v1 as components

# ========== Chatbot Response Logic ==========
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

    for key in responses:
        if key in user_input.lower():
            return responses[key]
    return "Sorry, I didn't understand that. Please try asking something else."

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ========== Collapsible Floating Chatbox ==========
def chatbot_widget():
    st.markdown("""
        <style>
        #chat-toggle-btn {
            position: fixed;
            bottom: 20px;
            right: 30px;
            background-color: #4CAF50;
            color: white;
            padding: 10px 16px;
            border: none;
            border-radius: 30px;
            font-size: 16px;
            cursor: pointer;
            z-index: 10000;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        #chatbox {
            display: none;
            position: fixed;
            bottom: 70px;
            right: 30px;
            width: 320px;
            max-height: 500px;
            background-color: white;
            border: 2px solid #4CAF50;
            border-radius: 12px;
            padding: 12px;
            z-index: 9999;
            box-shadow: 0 0 12px rgba(0,0,0,0.15);
            overflow-y: auto;
            resize: both;
            cursor: move;
        }

        #chat-messages {
            max-height: 280px;
            overflow-y: auto;
            font-size: 14px;
        }

        #chatbox input[type="text"] {
            width: 100%;
            padding: 6px;
            margin-top: 8px;
            font-size: 14px;
        }

        #chatbox input[type="submit"] {
            margin-top: 5px;
            background-color: #4CAF50;
            color: white;
            padding: 6px;
            border: none;
            width: 100%;
            cursor: pointer;
            border-radius: 5px;
        }
        </style>

        <button id="chat-toggle-btn" onclick="toggleChat()">💬 VetChat</button>
        <div id="chatbox">
            <strong>💬 VetChat</strong>
            <div id="chat-messages">
                <!-- Chat messages will be filled by Streamlit -->
            </div>
            <form action="" method="POST">
                <input name="user_input" type="text" placeholder="Ask something..." />
                <input type="submit" value="Send" />
            </form>
        </div>

        <script>
        function toggleChat() {
            var box = document.getElementById("chatbox");
            if (box.style.display === "none" || box.style.display === "") {
                box.style.display = "block";
            } else {
                box.style.display = "none";
            }
        }

        dragElement(document.getElementById("chatbox"));
        function dragElement(elmnt) {
          var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
          elmnt.onmousedown = dragMouseDown;
          function dragMouseDown(e) {
            e.preventDefault();
            pos3 = e.clientX;
            pos4 = e.clientY;
            document.onmouseup = closeDragElement;
            document.onmousemove = elementDrag;
          }
          function elementDrag(e) {
            e.preventDefault();
            pos1 = pos3 - e.clientX;
            pos2 = pos4 - e.clientY;
            pos3 = e.clientX;
            pos4 = e.clientY;
            elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
            elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
          }
          function closeDragElement() {
            document.onmouseup = null;
            document.onmousemove = null;
          }
        }
        </script>
    """, unsafe_allow_html=True)

    # Render chat content dynamically using Streamlit
    chat_html = "".join([
        f"<p><b>{sender}:</b> {message}</p>"
        for sender, message in st.session_state.chat_history
    ])
    components.html(f"""
        <script>
        document.getElementById("chat-messages").innerHTML = `{chat_html}`;
        </script>
    """, height=0)

    # Input form (actual processing logic)
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Ask VetChat", key="chat_input")
        submitted = st.form_submit_button("Send")
        if submitted and user_input:
            response = chatbot_response(user_input)
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("VetChat", response))

chatbot_widget()

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
