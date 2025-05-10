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
import streamlit as st

def display_dashboard():
    """Displays the livestock dashboard and add animal form."""
    st.subheader("📋 Add and Monitor Your Livestock")

    # Initialize session state for inputs
    for key in ["name", "animal_type", "age", "weight", "vaccination"]:
        if key not in st.session_state:
            if key == "animal_type":
                st.session_state[key] = "Cattle"
            elif key in ["age", "weight"]:
                st.session_state[key] = 0.0
            else:
                st.session_state[key] = ""

    def reset_form():
        st.session_state["name"] = ""
        st.session_state["animal_type"] = "Cattle"
        st.session_state["age"] = 0.0
        st.session_state["weight"] = 0.0
        st.session_state["vaccination"] = ""
        st.experimental_rerun()

    with st.form("livestock_form"):
        st.text_input("Animal Tag", key="name")
        st.selectbox("Type", ["Cattle", "Goat", "Sheep"], key="animal_type")
        st.number_input("Age (years)", 0.0, 20.0, step=0.1, key="age")
        st.number_input("Weight (kg)", 0.0, 500.0, step=1.0, key="weight")
        st.text_area("Vaccination History", key="vaccination")
        submit = st.form_submit_button("💾 Save")

        if submit:
            if st.session_state.name.strip() == "":
                st.warning("Animal Tag cannot be empty.")
            else:
                save_livestock_data(
                    st.session_state.name,
                    st.session_state.animal_type,
                    st.session_state.age,
                    st.session_state.weight,
                    st.session_state.vaccination
                )
                reset_form()
                st.success(f"{st.session_state.animal_type} '{st.session_state.name}' saved successfully!")

# Don't forget to call the function to run it
display_dashboard()

# ============================ Diagnosis ==================================
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
    st.markdown("## 🐄Livestock Focus:")
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

    for key in responses:
        if key in user_input.lower():
            return responses[key]
    return "Sorry, I didn't understand that. Please try asking something else."

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def chatbot_widget():
    with st.sidebar.expander("💬 VetChat", expanded=True):
        st.markdown("*Ask me anything about livestock care!*")

        # Display chat history
        for sender, message in st.session_state.chat_history:
            if sender == "You":
                st.markdown(f"**You:** {message}")
            else:
                st.markdown(f"🤖 **VetChat:** {message}")

        # Input form to avoid st.experimental_rerun() bug
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Ask VetChat:", key="chat_input")
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
