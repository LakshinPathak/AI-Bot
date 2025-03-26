import streamlit as st
from groq import Groq
import textwrap

# Page Configuration
st.set_page_config(
    page_title="Code Assistant",
    page_icon="💻",
    layout="wide"
)

# System Prompt for Code Optimization
SYSTEM_PROMPT = """
You are an expert Python code optimization mentor with the following capabilities:
- Provide constructive, detailed code analysis
- Offer actionable improvement suggestions
- Explain complex concepts in a beginner-friendly manner
- Highlight potential performance, security, and design issues
- Suggest idiomatic Python solutions and best practices

Your communication style should be:
- Clear and concise
- Supportive and educational
- Provide code examples
- Break down complex concepts
- Offer step-by-step guidance

Optimization Focus Areas:
1. Performance optimization
2. Code readability
3. Error handling
4. Security considerations
5. Pythonic coding techniques
"""

# LLM Model Configurations
LLM_MODELS = {
    "Llama 3 (70B)": "llama3-70b-8192",
    "DeepSeek R1 Distill Llama (70B)": "deepseek-r1-distill-llama-70b",
    "Qwen Coder (2.5-32B)": "qwen-2.5-coder-32b"
}

# Environment Variable for API Key (replace with your actual method of key management)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", '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')


# Initialize Groq Client
@st.cache_resource
def init_groq_client():
    try:
        return Groq(api_key=GROQ_API_KEY)
    except KeyError:
        st.error("API key not found. Please configure Streamlit secrets.")
        return None

# Chat History Management
def initialize_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi there! I'm your Code Assistant. Paste your Python code, and I'll help you optimize and improve it."}
        ]

# Generate LLM Response
def get_ai_response(user_input, chat_history, selected_model):
    client = init_groq_client()
    if not client:
        return "Sorry, I'm having trouble connecting to the AI service."

    try:
        # Prepare messages for context
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        # Add chat history context
        messages.extend([
            {"role": "user" if msg["role"] == "user" else "assistant", "content": msg["content"]} 
            for msg in chat_history[-5:]  # Limit context to last 5 messages
        ])
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=LLM_MODELS[selected_model],
            messages=messages,
            max_tokens=1500,
            temperature=0.4,
            top_p=0.9
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

# Main Streamlit App
def main():
    # Initialize chat history
    initialize_chat_history()

    # App Title and Description
    st.title(" AI Code Assistant: Your AI Code Optimization Companion")
    st.markdown("*Transform your Python code with intelligent insights and suggestions*")

    # Sidebar for Additional Context and Model Selection
    with st.sidebar:
        st.header("🛠 Optimization Tips")
        st.markdown("""
        - Share complete code snippets
        - Be specific about optimization goals
        - Provide context about your use case
        - Ask follow-up questions
        """)
        
        # LLM Model Selector
        selected_model = st.selectbox(
            "Select AI Model",
            list(LLM_MODELS.keys()),
            index=0  # Default to first model
        )
        
        # Optimization Focus Selector
        optimization_focus = st.selectbox(
            "Optimization Priority",
            [
                "Balanced Optimization", 
                "Performance", 
                "Readability", 
                "Memory Efficiency"
            ]
        )

    # Chat Interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input
    if user_input := st.chat_input("Paste your Python code or ask a code optimization question"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate AI Response
        with st.chat_message("assistant"):
            with st.spinner(f"Analyzing your code using {selected_model}..."):
                ai_response = get_ai_response(user_input, st.session_state.messages, selected_model)
                st.markdown(ai_response)

        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

# Run the application
if __name__ == "__main__":
    main()
