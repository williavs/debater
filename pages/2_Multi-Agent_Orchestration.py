import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Orchestration | V3 Discourse Engine",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 Multi-Agent Orchestration with LangGraph")

# Display the workflow diagram
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/graph.png", caption="V3 Discourse Engine Workflow")

st.markdown("""
### Understanding the Framework

The V3 Discourse Engine is built on LangGraph, a powerful framework for orchestrating complex multi-agent workflows. The system implements a sophisticated debate structure with three key components:

#### 🎭 Agent Roles
- **Champion Node**: Presents primary arguments supporting the topic
- **Challenger Node**: Provides counter-arguments and alternative perspectives
- **Jury Node**: Analyzes the debate and determines the outcome

#### 🔄 Workflow Process
1. Navigate to "Try out a debate!" in the sidebar
2. Choose or enter your debate topic
3. Watch as the Champion presents initial arguments with evidence
4. See the Challenger respond with counter-arguments
5. Follow the dynamic exchange between agents
6. Review the Jury's final analysis and verdict

#### 🛠️ Technical Implementation
- Built using LangGraph's StateGraph system
- Implements agent handoffs for seamless conversation flow
- Utilizes Google Search for real-time fact-checking
- Structured debate format ensures balanced discussion

### Resources
- [LangGraph Multi-Agent Network Guide](https://langchain-ai.github.io/langgraph/how-tos/multi-agent-network/)
- [LangGraph Multi-Agent Concepts](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- [LangGraph How-To Guides](https://langchain-ai.github.io/langgraph/how-tos/)
""")

# Footer
st.markdown("---")
st.markdown("© 2024 V3 AI | Created by William VanSickle III | [Visit V3 AI →](https://v3-ai.com) | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/williavs) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/willyv3/)") 