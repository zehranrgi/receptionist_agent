"""
Streamlit Web Interface for Barber Appointment Agent
A beautiful web-based chat interface for the barber appointment system.
"""

import streamlit as st
import os
from datetime import datetime
from agent import BarberAppointmentAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Elite Barber Shop - AI Receptionist",
    page_icon="🪒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    
    .user-message {
        background-color: #007bff;
        color: white;
        margin-left: auto;
        text-align: right;
    }
    
    .agent-message {
        background-color: #f8f9fa;
        color: #333;
        border: 1px solid #dee2e6;
    }
    
    .service-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .appointment-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False

def create_agent():
    """Create and initialize the agent"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error(" OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        st.stop()
    
    return BarberAppointmentAgent(api_key)

def display_welcome():
    """Display welcome message and business info"""
    st.markdown("""
    <div class="main-header">
        <h1>🪒 Elite Barber Shop</h1>
        <h3>AI-Powered Receptionist</h3>
        <p>Book your appointment with our intelligent assistant in Los Angeles</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Business info sidebar
    with st.sidebar:
        st.markdown("### 🏪 Business Information")
        st.markdown("**Address:** 123 Sunset Boulevard, West Hollywood, CA 90069")
        st.markdown("**Phone:** +1 (323) 555-0123")
        st.markdown("**Hours:** 09:00-19:00 (Mon-Fri), 09:00-18:00 (Sat)")
        
        st.markdown("### 🛠️ Available Services")
        services = [
            ("✂️ Haircut", "$45", "30 min"),  #add emoji 
            ("🧔 Beard Trim", "$25", "15 min"),
            ("💧 Hair Wash", "$15", "10 min"),
            ("✨ Facial Treatment", "$60", "45 min"),
            ("🎯 Haircut + Beard Trim", "$65", "45 min")
        ]
        
        for service, price, duration in services:
            st.markdown(f"**{service}** - {price} ({duration})")

def display_chat_messages():
    """Display chat messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_user_input():
    """Handle user input and generate response"""
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if st.session_state.agent is None:
                    st.session_state.agent = create_agent()
                
                response = st.session_state.agent.chat(prompt)
                st.markdown(response)
        
        # Add agent response to messages
        st.session_state.messages.append({"role": "assistant", "content": response})

def display_quick_actions():
    """Display quick action buttons"""
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 View Services", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "What services do you offer?"})
            st.rerun()
    
    with col2:
        if st.button("📅 Check Availability", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "I want to book an appointment for tomorrow"})
            st.rerun()
    
    with col3:
        if st.button("📞 Contact Info", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "What are your contact details?"})
            st.rerun()

def display_recent_appointments():
    """Display recent appointments if any"""
    try:
        import json
        with open('appointments.json', 'r', encoding='utf-8') as f:
            appointments = json.load(f)
        
        if appointments:
            st.markdown("### 📅 Recent Appointments")
            for appointment in appointments[-3:]:  # Show last 3
                with st.expander(f"Appointment {appointment['id']}"):
                    st.markdown(f"**Customer:** {appointment['customer']['name']}")
                    st.markdown(f"**Date:** {appointment['appointment']['date']}")
                    st.markdown(f"**Time:** {appointment['appointment']['time']}")
                    st.markdown(f"**Services:** {', '.join(appointment['appointment']['services'])}")
                    st.markdown(f"**Total:** {appointment['appointment']['total_price']} TL")
    except FileNotFoundError:
        pass

def main():
    """Main Streamlit app"""
    initialize_session_state()
    
    # Header
    display_welcome()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Chat with our AI Receptionist")
        
        # Display chat messages
        display_chat_messages()
        
        # Handle user input
        handle_user_input()
        
        # Quick actions
        if not st.session_state.messages:
            display_quick_actions()
    
    with col2:
        # Recent appointments
        display_recent_appointments()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.agent:
                st.session_state.agent.reset_conversation()
            st.rerun()
        
        # Instructions
        st.markdown("### 💡 How to use")
        st.markdown("""
        1. **Ask about services** - "What services do you offer?"
        2. **Check availability** - "I want to book for tomorrow"
        3. **Book appointment** - Provide your details when asked
        4. **Get information** - Ask about hours, contact, etc.
        """)

if __name__ == "__main__":
    main()
