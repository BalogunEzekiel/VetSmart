import time
import streamlit as st

# Define the chatbot response logic
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

# Define the chatbot widget for Streamlit
def chatbot_widget():
    # Styling for the chatbot window
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

    # Initialize session states for chatbot
    if "vetchat_open" not in st.session_state:
        st.session_state.vetchat_open = False

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Button to toggle the chatbot window
    toggle = st.button("💬 VetChat", key="vetchat-toggle")

    if toggle:
        st.session_state.vetchat_open = not st.session_state.vetchat_open

    if st.session_state.vetchat_open:
        # Show the chatbot container
        st.markdown('<div id="vetchat-container">', unsafe_allow_html=True)
        st.markdown("**🗨️ Ask me anything about livestock care!**")

        # Display the chat history
        for sender, message in st.session_state.chat_history:
            if sender == "You":
                st.markdown(f"**You:** {message}")
            else:
                st.markdown(f"🤖 **VetChat:** {message}")

        # Text input form for user to ask a question
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Ask VetChat:", key="chat_input", label_visibility="collapsed")
            submitted = st.form_submit_button("Send")

            if submitted and user_input:
                # Store the user's question in chat history
                st.session_state.chat_history.append(("You", user_input))

                # Simulate typing delay
                placeholder = st.empty()
                placeholder.markdown("🤖 **VetChat:** _typing..._")
                time.sleep(1.5)

                # Get the chatbot's response
                response = chatbot_response(user_input)

                # Show the chatbot's response
                placeholder.markdown(f"🤖 **VetChat:** {response}")
                st.session_state.chat_history.append(("VetChat", response))

        # Close the chatbot container
        st.markdown("</div>", unsafe_allow_html=True)

# Run the chatbot widget
chatbot_widget()
