
import streamlit as st
import os
import time
from dotenv import load_dotenv
from google import genai

# Load API Key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Page Configuration
st.set_page_config(
    page_title="Smart AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Modern UI Design
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e1b4b);
    color: white;
}

h1 {
    color: #a78bfa;
    text-align: center;
    font-weight: bold;
}

[data-testid="stChatMessage"] {
    background-color: #252442;
    border-radius: 15px;
    padding: 15px;
    border: 1px solid #48416e;
}

[data-testid="stChatInput"] {
    border: 2px solid #8b5cf6;
    border-radius: 15px;
}

section[data-testid="stSidebar"] {
    background-color: #17152e;
}

</style>
""", unsafe_allow_html=True)

# Application Heading
st.title("🤖 My Smart AI Chatbot")
st.caption("Your Personal AI Assistant | Powered by Gemini")

# API Key Check
if not API_KEY:
    st.error("Gemini API key not found!")
    st.info("Please add your API key inside the .env file.")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=API_KEY)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    st.write("Welcome to Smart AI Chatbot!")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.write("Features:")
    st.write(" AI Answers")
    st.write(" Chat History")
    st.write("Automatic Retry")
    st.write("Modern Interface")

# Display Previous Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to Generate AI Response
def get_ai_response(messages):

    # Convert conversation into Gemini format
    contents = []

    for message in messages:
        role = "user" if message["role"] == "user" else "model"

        contents.append({
            "role": role,
            "parts": [{"text": message["content"]}]
        })

    # Retry on temporary errors
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=contents,
                config={
                    "system_instruction": (
                        "You are a helpful and friendly AI assistant. "
                        "Answer questions clearly and accurately. "
                        "Use simple English when explaining technical topics."
                    ),
                    "temperature": 0.7,
                    "max_output_tokens": 2048
                }
            )

            if response.text:
                return response.text

            return "Sorry, I could not generate an answer. Please try again."

        except Exception as error:

            error_message = str(error)

            # Retry only for temporary server or rate-limit errors
            temporary_error = (
                "503" in error_message
                or "429" in error_message
                or "UNAVAILABLE" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
            )

            if temporary_error and attempt < 2:
                time.sleep(2 ** (attempt + 1))
                continue

            raise error

# Chat Input
user_input = st.chat_input("💬 Ask me anything...")

if user_input:

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate AI Answer
    with st.chat_message("assistant"):

        with st.spinner("🤖 AI is thinking..."):

            try:
                answer = get_ai_response(
                    st.session_state.messages
                )

                st.markdown(answer)

                # Save AI response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:

                error_message = str(error)

                if "503" in error_message or "UNAVAILABLE" in error_message:
                    st.error(
                        "Gemini server is temporarily busy. "
                        "Please try again after some time."
                    )

                elif "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
                    st.error(
                        "API request limit reached. "
                        "Please check your Gemini API quota."
                    )

                elif "404" in error_message or "NOT_FOUND" in error_message:
                    st.error("Gemini API returned a 404 error:")
                    st.code(error_message)
                
                else:
                    st.error("Something went wrong with the AI request.")
                    st.caption(error_message)
