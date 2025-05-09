from streamlit_chat import message
import streamlit as st

def run_vetchat():
    # Initialize toggle state
    if "show_chatbot" not in st.session_state:
        st.session_state.show_chatbot = True
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Floating toggle button
    st.markdown("""
    <style>
        .toggle-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #4CAF50;
            color: white;
            padding: 10px 16px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            z-index: 10000;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
        }
    </style>
    """, unsafe_allow_html=True)

    toggle_label = "Hide VetChat 💬" if st.session_state.show_chatbot else "Show VetChat 💬"
    if st.button(toggle_label, key="toggle_btn"):
        st.session_state.show_chatbot = not st.session_state.show_chatbot

    if st.session_state.show_chatbot:
        st.markdown("""
        <style>
            .chatbot-container {
                position: fixed;
                bottom: 70px;
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
            st.markdown('<div class="chatbot-header">💬 VetChat Assistant</div>', unsafe_allow_html=True)

            user_input = st.text_input("", placeholder="Ask something...", key="vetchat_input")

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
