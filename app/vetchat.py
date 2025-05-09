from streamlit_chat import message
import streamlit as st

def run_vetchat():
    # Initialize session state
    if "show_chatbot" not in st.session_state:
        st.session_state.show_chatbot = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Custom CSS for floating draggable and animated chatbox
    st.markdown("""
    <style>
        .chatbot-toggle-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #4CAF50;
            color: white;
            padding: 12px 18px;
            border: none;
            border-radius: 50px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            z-index: 9999;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.25);
        }

        #chatbot-popup {
            position: fixed;
            bottom: 80px;
            right: 30px;
            width: 320px;
            max-height: 450px;
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            overflow-y: auto;
            z-index: 9998;
            padding: 16px;
            animation: slideUp 0.4s ease;
        }

        @keyframes slideUp {
            from { transform: translateY(30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .chatbot-header {
            font-size: 16px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }

        .drag-handle {
            cursor: move;
            background: #eee;
            padding: 5px;
            text-align: center;
            border-radius: 8px;
            margin-bottom: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Toggle button
    toggle_label = "🧠 Chat with VetChat" if not st.session_state.show_chatbot else "❌ Close VetChat"
    if st.button(toggle_label, key="vetchat_toggle_btn"):
        st.session_state.show_chatbot = not st.session_state.show_chatbot

    # Chatbot popup window
    if st.session_state.show_chatbot:
        st.markdown('<div id="chatbot-popup">', unsafe_allow_html=True)
        st.markdown('<div class="drag-handle">🤖 Drag VetChat</div>', unsafe_allow_html=True)
        st.markdown('<div class="chatbot-header">VetChat Assistant</div>', unsafe_allow_html=True)

        user_input = st.text_input("Type your question:", placeholder="Ask about animal care...", key="vetchat_input")

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

for i, (speaker, text) in enumerate(st.session_state.chat_history):
    message(text, is_user=(speaker == "user"), key=f"chat_{i}")

        st.markdown('</div>', unsafe_allow_html=True)

    # JavaScript to enable dragging
    st.components.v1.html("""
    <script>
    const dragElement = (elmnt) => {
        const popup = document.getElementById("chatbot-popup");
        let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
        elmnt.onmousedown = dragMouseDown;

        function dragMouseDown(e) {
            e = e || window.event;
            e.preventDefault();
            pos3 = e.clientX;
            pos4 = e.clientY;
            document.onmouseup = closeDragElement;
            document.onmousemove = elementDrag;
        }

        function elementDrag(e) {
            e = e || window.event;
            e.preventDefault();
            pos1 = pos3 - e.clientX;
            pos2 = pos4 - e.clientY;
            pos3 = e.clientX;
            pos4 = e.clientY;
            popup.style.top = (popup.offsetTop - pos2) + "px";
            popup.style.left = (popup.offsetLeft - pos1) + "px";
        }

        function closeDragElement() {
            document.onmouseup = null;
            document.onmousemove = null;
        }
    };

    window.addEventListener("load", () => {
        const handle = document.querySelector(".drag-handle");
        if (handle) dragElement(handle);
    });
    </script>
    """, height=0)
