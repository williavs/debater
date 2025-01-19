import streamlit as st
import os


st.set_page_config(
    page_title="AI Debate Arena",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for OpenAI API key if not already present
if "api_keys_initialized" not in st.session_state:
    st.session_state.api_keys_initialized = True
    st.session_state.openai_api_key = ""

# Title and Introduction
st.title("🤖 Welcome to AI Debate Arena")

# Main content area with gradient background
st.markdown("""
<div style='padding: 2rem; border-radius: 10px; background: linear-gradient(135deg, #f6f8fc, #e9ecef);'>
    <h2 style='color: #1e3a8a;'>Experience AI-Powered Debates</h2>
    <p style='font-size: 1.1em; color: #374151;'>
        Watch as two AI agents engage in structured, evidence-based debates on any topic you choose. 
        Our platform features:
    </p>
    <ul style='font-size: 1.1em; color: #374151;'>
        <li>🎯 Real-time AI debates with live research</li>
        <li>🔍 Integration with Google search for fact-checking</li>
        <li>⚖️ Impartial AI jury evaluation</li>
        <li>🎨 Beautiful, dynamic UI with live updates</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# API Configuration Section
st.header("🔑 API Configuration")

with st.expander("Configure OpenAI API Key", expanded=not bool(st.session_state.openai_api_key)):
    st.markdown("""
    <div style='margin-bottom: 1rem;'>
        <p style='color: #374151;'>To use the AI Debate Arena, you'll need to provide your OpenAI API key:</p>
        <ul>
            <li>The app uses GPT-4 for generating debate content</li>
            <li>Your API key is stored securely in your session</li>
            <li>The key is never saved or logged</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # OpenAI API Key input with clear button
    col1, col2 = st.columns([3, 1])
    with col1:
        openai_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.openai_api_key,
            type="password",
            help="Required for the debate agents to function",
            key="openai_key_input"
        )
    with col2:
        if st.button("Clear", key="clear_openai"):
            st.session_state.openai_api_key = ""
            st.experimental_rerun()
    
    if openai_key:
        st.session_state.openai_api_key = openai_key

# Getting Started Section
st.header("🚀 Getting Started")
st.markdown("""
<div style='padding: 1.5rem; border-radius: 10px; background: linear-gradient(135deg, #e8f5e9, #c8e6c9);'>
    <h3 style='color: #1b5e20;'>How to Use</h3>
    <ol style='color: #2e7d32;'>
        <li>Enter your OpenAI API key above</li>
        <li>Navigate to the Debate Arena using the sidebar</li>
        <li>Choose a debate topic or enter your own</li>
        <li>Watch as AI agents engage in a structured debate</li>
        <li>See the jury's final verdict</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# Check if OpenAI API key is set
if not st.session_state.openai_api_key:
    st.warning("⚠️ Please enter your OpenAI API key to get started!")
else:
    st.success("✅ You're all set! Navigate to the Debate Arena using the sidebar to start a debate.")
