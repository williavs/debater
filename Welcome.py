import streamlit as st
import os


st.set_page_config(
    page_title="Welcome | V3 Discourse Engine",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for OpenAI API key if not already present
if "api_keys_initialized" not in st.session_state:
    st.session_state.api_keys_initialized = True
    st.session_state.openai_api_key = ""

st.sidebar.image("assets/v3.jpeg", width=400)



# Centered logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("assets/logo3.png", width=400)
    except:
        st.title("V3 Discourse Engine")

# Main content in two columns
left_col, right_col = st.columns([3, 2])

with left_col:
    st.header("Explore Multiple Perspectives")
    st.write("""
    V3 Discourse Engine helps you analyze topics from different angles through structured debate. 
    Whether you're exploring complex decisions, understanding various viewpoints, or researching topics, 
    our platform facilitates evidence-based discussions on any subject you choose.
    """)

    st.markdown("""
    - 🎯 Analyze any topic through structured debate
    - 🔍 Research-backed arguments with live web search
    - ⚖️ Balanced perspective from both sides
    - 💡 Useful for decision-making, research, and understanding
    """)

    st.subheader("Common Use Cases")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - Explore complex topics
        - Research arguments
        - Analyze decisions
        """)
    with col2:
        st.markdown("""
        - Understand viewpoints
        - Study debate techniques
        - Academic discussions
        """)

with right_col:
    st.header("Get Started")
    
    with st.expander("1. Configure OpenAI API Key", expanded=not bool(st.session_state.openai_api_key)):
        st.write("Provide your OpenAI API key to use the engine:")
        st.markdown("""
        - Uses GPT-4 for arguments
        - Secure session storage
        - Never saved or logged
        """)
        
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

    st.subheader("2. Quick Start Guide")
    st.markdown("""
    1. Enter API key above
    2. Open "Try out a debate!"
    3. Choose your topic
    4. Watch the debate
    5. Review analysis
    """)

    # Check if OpenAI API key is set
    if not st.session_state.openai_api_key:
        st.warning("⚠️ Enter your OpenAI API key to begin!")
    else:
        st.success("✅ Ready! Open 'Try out a debate!' to start.")

# Footer
st.markdown("---")
st.markdown("© 2024 V3 AI | Created by William VanSickle III | [Visit V3 AI →](https://v3-ai.com) | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/williavs) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/willyv3/)")
