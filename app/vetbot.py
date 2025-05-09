# app/vetbot.py
from streamlit_chat import message
import streamlit as st

def run_vetbot():
    with st.sidebar:
        st.markdown("### 💬 VetBot Assistant")
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        # Input from the user
        user_input = st.text_input("Ask VetBot something:", key="vetbot_input", label_visibility="collapsed")

        # Generate response
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
