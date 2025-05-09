# app/vetbot.py
from streamlit_chat import message
import streamlit as st

def run_vetbot():
    # Inject custom CSS for floating chat box
    st.markdown("""
    <style>
        .chatbot-container {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 320px;
            max-height: 400px;
            background-color: #ffffff;
            border: 2px solid #ccc;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            padding: 15px;
            z-index: 9999;
            overflow-y: auto;
        }
        .chatbot-header {
            font-weight: bold;
            margin-bottom: 10px;
            color: #0e1117;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="chatbot-container">', unsafe_allow_html=True)
        st.markdown('<div class="chatbot-header">💬 VetBot Assistant</div>', unsafe_allow_html=True)

        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        # Input from user
        user_input = st.text_input("", placeholder="Ask something...", key="vetbot_input")

        # Generate bot response
        def generate_response(prompt):
            if "sick" in prompt.lower():
                return "Please bring the animal for a checkup. What symptoms have you observed?"
            elif "vaccination" in prompt.lower():
                return "You can schedule vaccinations from the animal's health page."
            else:
                return "I'm here to help you with animal health, appointments, or reports. Ask me anything!"

        if user_input:
            st.session_state.chat_history.append(("user", user_input))
            response = generate_response(user_input)
            st.session_state.chat_history.append(("bot", response))

        for speaker, text in st.session_state.chat_history:
            message(text, is_user=(speaker == "user"))

        st.markdown('</div>', unsafe_allow_html=True)
