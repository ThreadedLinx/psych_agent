"""
Streamlit Chat Interface for Agentic Psychological Diagnostics & Treatment Planning System
"""

import streamlit as st
import sys
import os

# Load Streamlit secrets and set environment variables
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
os.environ['SERPER_API_KEY'] = st.secrets['SERPER_API_KEY']
os.environ['CREWAI_STORAGE_DIR'] = st.secrets['CREWAI_STORAGE_DIR']

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agentic_rag_psychological_diagnostics_treatment_planning_system.message_handler import (
    process_message, 
    initialize_session, 
    get_conversation_history, 
    is_assessment_complete,
    get_current_step
)

# Set page config
st.set_page_config(
    page_title="AI Psychological Assessment", 
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'conversation_state' not in st.session_state:
    st.session_state.conversation_state = initialize_session()
    st.session_state.messages = []

# Sidebar with session info
with st.sidebar:
    st.header("🧠 AI Psychological Assessment")
    st.markdown("---")
    
    # Current step indicator
    current_step = get_current_step(st.session_state.conversation_state)
    step_descriptions = {
        1: "🔍 Symptom Assessment",
        2: "⏰ Duration & Patterns", 
        3: "🏠 Functional Impact",
        4: "🩺 Clinical Diagnosis",
        5: "💊 Treatment Options",
        6: "📋 Treatment Plan"
    }
    
    st.subheader("Current Step:")
    st.info(f"**Step {current_step}**: {step_descriptions.get(current_step, 'Assessment')}")
    
    # Progress indicator
    progress = current_step / 6
    st.progress(progress)
    
    # Session info
    st.markdown("---")
    st.subheader("Session Info:")
    st.write(f"**Messages**: {len(st.session_state.messages)}")
    st.write(f"**Assessment Complete**: {'✅' if is_assessment_complete(st.session_state.conversation_state) else '⏳'}")
    
    # Reset button
    if st.button("🔄 New Assessment", type="secondary"):
        st.session_state.conversation_state = initialize_session()
        st.session_state.messages = []
        st.experimental_rerun()

# Main chat interface
st.title("🧠 AI Psychological Assessment & Treatment Planning")
st.markdown("Welcome! I'm here to conduct a comprehensive psychological assessment through our conversation.")

# Display chat messages
if not st.session_state.messages:
    # Welcome message
    welcome_msg = """
    Hello! I'm your AI psychological assessment coordinator. I'll be guiding you through a comprehensive 6-step diagnostic process:
    
    1. **Symptom Assessment** - Understanding your concerns
    2. **Duration & Patterns** - Timeline and patterns  
    3. **Functional Impact** - How symptoms affect daily life
    4. **Clinical Diagnosis** - Professional assessment
    5. **Treatment Options** - Evidence-based treatment choices
    6. **Treatment Plan** - Comprehensive plan development
    
    To get started, please share your name and describe what brings you here today.
    """
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Processing your message..."):
            try:
                # Process message through CrewAI agent
                response = process_message(prompt, st.session_state.conversation_state)
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_message = f"I apologize, but I encountered an error processing your message. Please try again.\n\nError: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# Footer
st.markdown("---")
st.markdown("**Note**: This AI assessment tool is for educational and informational purposes. Always consult with qualified mental health professionals for actual diagnosis and treatment.")

# Download treatment plan button (if assessment is complete)
if is_assessment_complete(st.session_state.conversation_state):
    st.success("🎉 Assessment Complete! Your treatment plan has been generated.")
    
    # Extract treatment plan from conversation
    treatment_plan_content = ""
    for msg in st.session_state.messages:
        if msg["role"] == "assistant" and "treatment plan" in msg["content"].lower():
            treatment_plan_content = msg["content"]
            break
    
    if treatment_plan_content:
        st.download_button(
            label="📄 Download Treatment Plan",
            data=treatment_plan_content,
            file_name="psychological_treatment_plan.md",
            mime="text/markdown",
            type="primary"
        )