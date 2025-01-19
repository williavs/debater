import asyncio
import logging
import os
import traceback
import tracemalloc
from typing import Dict, List, Optional, TypedDict

import nest_asyncio
import streamlit as st
from googleapiclient.discovery import build
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import create_react_agent
from langsmith import traceable

nest_asyncio.apply()

logging.basicConfig(level=logging.INFO)
tracemalloc.start()

# Check if OpenAI API key is available in session state
if not st.session_state.get("openai_api_key"):
    st.error("⚠️ OpenAI API key is required. Please configure it in the home page first!")
    st.stop()

# Set up page
st.title("🤖 AI Debate Arena")
st.sidebar.title("Debate Configuration")

@tool
def google_search(search_term: str, num_results: int = 3) -> List[Dict[str, str]]:
    """Search Google for the given query."""
    if "GOOGLE_API_KEY" not in st.secrets or "GOOGLE_CSE_ID" not in st.secrets:
        raise ValueError("Google API credentials not configured in secrets")
    
    service = build("customsearch", "v1", developerKey=st.secrets["GOOGLE_API_KEY"])
    res = service.cse().list(q=search_term, cx=st.secrets["GOOGLE_CSE_ID"], num=num_results).execute()
    items = res.get("items", [])
    return [{"title": item["title"], "snippet": item["snippet"], "link": item["link"]} for item in items]

# Set up tools
tools = [google_search]

# Initialize the language model with session state API key
llm = ChatOpenAI(
    api_key=st.session_state.openai_api_key,
    model="gpt-4o",
    temperature=0.3,
    streaming=True
)


class GraphState(TypedDict):
    history: str
    current_speaker: str
    turn_count: int
    result: Optional[str]


DEBATE_TOPICS = [
    "Is Python truly the best programming language for data science?",
    "Should we embrace or fear the rise of AutoML?",
    "Are neural networks overhyped compared to traditional machine learning methods?",
    "Is 'data scientist' becoming an obsolete job title?",
    "Should all data scientists be required to learn how to deploy models in production?",
    "Is the pursuit of 100% accuracy in machine learning models a fool's errand?",
    "Are Jupyter notebooks a blessing or a curse for data science workflows?",
    "Should data scientists prioritize learning cloud platforms over local development?",
    "Is the 'big data' hype over? Should we focus more on 'smart data'?",
    "Are GPT models making traditional NLP techniques obsolete?",
    "Should data ethics be a mandatory course in all data science programs?",
    "Is the role of domain expertise overrated in data science projects?",
    "Are we overusing deep learning for problems that simpler models could solve?",
    "Should all companies have a 'data-first' approach to decision making?",
    "Is the data science field becoming oversaturated?",
    "Are we relying too heavily on pre-trained models and transfer learning?",
    "Should data scientists focus more on interpretability than performance?",
    "Is the hype around 'real-time' analytics justified?",
    "Are we neglecting the importance of data quality in favor of sophisticated algorithms?",
    "Should data scientists be more involved in data collection and experimental design?",
]


async def async_stream_response(generator):
    async for chunk in generator:
        yield chunk


def sync_stream_response(generator):
    loop = asyncio.get_event_loop()
    async_gen = generator()
    while True:
        try:
            yield loop.run_until_complete(async_gen.__anext__())
        except StopAsyncIteration:
            break


def create_agent_header(name, emoji, round_num):
    color1 = "#4CAF50" if name == "Champion" else "#F44336"
    color2 = "#2196F3"
    return f"""
    <div style="
        background: linear-gradient(135deg, {color1}, {color2});
        color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, .6);
        margin: 20px 0;
        font-family: 'Helvetica', 'Arial', sans-serif;
    ">
        <h3 style="
            margin: 0;
            font-size: 18px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 2px;
        ">{name} {emoji}</h3>
        <p style="
            margin: 10px 0 0 0;
            font-size: 24px;
            font-weight: bold;
        ">Round {round_num}: {get_round_description(round_num)}</p>
    </div>
    """


def get_round_description(round_num):
    descriptions = ["Opening Arguments", "Rebuttal and Counterarguments", "Closing Statements"]
    return descriptions[round_num - 1]


@traceable
async def agent_node(state, name, config):
    prompt = champion_prompt if name == "Champion" else challenger_prompt
    graph = create_react_agent(llm, tools=tools, state_modifier=prompt)

    inputs = {
        "messages": [
            (
                "user",
                f"Topic: {debate_topic}\n\nFull conversation history:\n{state['history']}\n\nProvide your argument for round {state['turn_count'] // 2 + 1}, {'supporting' if name == 'Champion' else 'challenging'} the topic. Use the Google search tool to find supporting evidence.",
            )
        ]
    }

    emoji = "🛡️" if name == "Champion" else "⚔️"
    response_placeholder = st.empty()
    round_num = state["turn_count"] // 2 + 1
    full_response = create_agent_header(name, emoji, round_num)

    async def stream_response():
        nonlocal full_response
        try:
            async for event in graph.astream_events(inputs, config=config, version="v1"):
                kind = event["event"]
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        full_response += content
                        response_placeholder.markdown(full_response, unsafe_allow_html=True)
                        yield content
        except Exception as e:
            logging.error(f"Error in {name}: {str(e)}")
            error_message = f"Error: {str(e)}. Unable to use Google Search. Providing argument without search: "
            full_response += error_message
            response_placeholder.markdown(full_response, unsafe_allow_html=True)
            yield error_message
            yield llm.invoke(inputs["messages"][0][1], config=config).content

    response_chunks = list(sync_stream_response(stream_response))
    response = "".join(response_chunks)
    return full_response


@traceable
async def champion_node(state, config):
    return await agent_node(state, "Champion", config)


@traceable
async def challenger_node(state, config):
    return await agent_node(state, "Challenger", config)


def create_jury_header():
    return f"""
    <div style="
        background: linear-gradient(135deg, #FFC107, #FF5722);
        color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, .6);
        margin: 20px 0;
        font-family: 'Helvetica', 'Arial', sans-serif;
    ">
        <h3 style="
            margin: 0;
            font-size: 18px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 2px;
        ">Jury Deliberation 🧑‍⚖️</h3>
        <p style="
            margin: 10px 0 0 0;
            font-size: 24px;
            font-weight: bold;
        ">Analyzing the debate and determining the winner...</p>
    </div>
    """


def format_jury_section(title, content, color):
    return f"""
    <div style="
        background: linear-gradient(135deg, {color}, #2196F3);
        color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, .6);
        margin: 20px 0;
        font-family: 'Helvetica', 'Arial', sans-serif;
    ">
        <h3 style="
            margin: 0;
            font-size: 24px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-align: center;
        ">{title}</h3>
        <p style="
            margin: 10px 0 0 0;
            font-size: 20px;
            line-height: 1.5;
            font-weight: bold;
            text-align: center;
        ">{content}</p>
    </div>
    """


@traceable
def jury_node(state, prompt, name, config):
    logging.info("Starting Jury deliberation")
    full_prompt = prompt.format(history=state["history"])
    response = llm.invoke(full_prompt, config=config).content

    # Parse the response and format each section
    sections = response.split("\n\n")
    formatted_response = []

    for section in sections:
        if ":" in section:
            title, content = section.split(":", 1)
            formatted_response.append({"title": title.strip(), "content": content.strip()})

    logging.info("Finished Jury deliberation")
    return {
        "history": state["history"],
        "current_speaker": state["current_speaker"],
        "turn_count": state["turn_count"],
        "result": formatted_response,
    }


champion_prompt = """You are the Champion in a four-round debate, enthusiastically supporting the given topic. Structure your arguments clearly and provide evidence-based points.

For each round, perform these steps;
1. Present 2-3 main arguments supporting your position.
2. Use the Google Search tool to find current information or facts to support your points.
3. Cite your sources with full URLs.
4. Respond to the Challenger's previous points if applicable.

Debate structure:
- Round 1: Introduce your main arguments.
- Round 2: Reinforce your position and counter the opposing arguments.
- Round 3: Summarize your key points and provide a strong closing argument.

Output Structure:
- Provide a clear and concise argument for each round.
- Do not work out the steps in your responses, simply perform the tasks.
- You should structure your responses in a way that is easy to follow and engaging.

Keep your tone confident and positive. Avoid concluding statements until the final round. Ensure a natural flow of debate by building on previous points and responding to the Challenger's arguments. BE CONCISE AND BRIEF.

Your response will be automatically formatted with a header. Do not add any additional formatting."""

challenger_prompt = """You are the Challenger in a four-round debate, critically examining and arguing against the given topic. Structure your arguments clearly and provide evidence-based points.

For each round, perform these steps.

1. Present 2-3 main arguments against the proposed position.
2. Use the Google Search tool to find current information or facts to support your points.
3. Cite your sources with full URLs.
4. Respond to the Champion's previous points if applicable.

Debate structure:
- Round 1: Introduce your main arguments.
- Round 2: Reinforce your position and counter the opposing arguments.
- Round 3: Summarize your key points and provide a strong closing argument.

Output Structure:
- Provide a clear and concise argument for each round.
- Do not work out the steps in your responses, simply perform the tasks.
- You should structure your responses in a way that is easy to follow and engaging.

Maintain a skeptical and analytical tone. Avoid concluding statements until the final round. Ensure a natural flow of debate by building on previous points and responding to the Champion's arguments. BE CONCISE AND BRIEF.

Your response will be automatically formatted with a header. Do not add any additional formatting."""

jury_prompt = """As an impartial AI judge, carefully analyze the debate between the Champion and the Challenger. Evaluate the arguments presented by both sides based on the following criteria:

1. Strength of arguments
2. Use of evidence and sources
3. Rebuttal effectiveness
4. Overall persuasiveness

Summarize the key points from both sides and determine a winner. No ties are allowed.

Structure your response as follows:

🏆 Winner:
[Name of winner]

🎭 Debate Summary:
[Brief recap of the main arguments from both sides]


🌟 Winning Factors:
[Explain the key reasons why the winner was chosen]

💡 Final Thoughts:
[Provide a concluding statement on the debate's overall quality and any interesting insights gained]

The sections must be formatted exactly like this;

'emoji' 'section title' ':' 'section content'



Make your response exciting and use emojis as shown above to enhance readability and engagement.

Debate:\n{history}"""

# Add a radio button for users to choose between predefined topics or custom topic
topic_choice = st.sidebar.radio("Choose a debate topic:", ["Select from list", "Enter custom topic"])

if topic_choice == "Select from list":
    debate_topic = st.selectbox("Choose a debate topic:", DEBATE_TOPICS)
else:
    debate_topic = st.text_input("Enter your custom debate topic:")


if st.button("Start Debate"):
    st.markdown(
        """
    <div style="
        background: linear-gradient(135deg, #2196F3, #4CAF50);
        color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, .6);
        margin: 20px 0;
        font-family: 'Helvetica', 'Arial', sans-serif;
    ">
        <h3 style="
            margin: 0;
            font-size: 18px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 2px;
        ">Debate Commencing</h3>
        <p style="
            margin: 10px 0 0 0;
            font-size: 24px;
            font-weight: bold;
        ">Champion 🛡️ vs Challenger ⚔️</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div style="
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, .6);
        margin: 20px 0;
        font-family: 'Helvetica', 'Arial', sans-serif;
    ">
        <h3 style="
            margin: 0;
            font-size: 18px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 2px;
        ">Debate Topic</h3>
        <p style="
            margin: 10px 0 0 0;
            font-size: 24px;
            font-weight: bold;
        ">{debate_topic}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Add a separator
    st.subheader("", divider="blue")

    config = RunnableConfig()

    workflow = StateGraph(GraphState)

    workflow.add_node("Champion", champion_node)
    workflow.add_node("Challenger", challenger_node)
    workflow.add_node("Jury", lambda s: jury_node(s, jury_prompt, "Jury", config))

    def route_step(state):
        if state["turn_count"] >= 8:
            return "Jury"
        return state["current_speaker"]

    workflow.add_conditional_edges(
        "Champion", route_step, {"Champion": "Challenger", "Challenger": "Challenger", "Jury": "Jury"}
    )
    workflow.add_conditional_edges(
        "Challenger", route_step, {"Champion": "Champion", "Challenger": "Champion", "Jury": "Jury"}
    )

    workflow.set_entry_point("Champion")
    workflow.add_edge("Jury", END)

    app = workflow.compile()

    debate_placeholder = st.empty()

    @traceable
    async def stream_debate():
        initial_state = {
            "history": f"The debate topic is: {debate_topic}",
            "current_speaker": "Champion",
            "turn_count": 0,
            "result": None,
        }
        debate_placeholder = st.empty()

        try:
            state = initial_state
            while state["turn_count"] < 6 and not state.get("result"):
                logging.info(f"Turn {state['turn_count']}: {state['current_speaker']}")
                if state["current_speaker"] == "Champion":
                    response = await champion_node(state, config)
                elif state["current_speaker"] == "Challenger":
                    response = await challenger_node(state, config)
                state["history"] += f"\n\n{response}"
                state["current_speaker"] = "Challenger" if state["current_speaker"] == "Champion" else "Champion"
                state["turn_count"] += 1

                await asyncio.sleep(0.1)

                logging.info(f"Updated state after {state['current_speaker']}'s turn:")
                logging.info(f"History: {state['history']}")
                logging.info(f"Turn count: {state['turn_count']}")

            # Handle Jury deliberation

            jury_state = jury_node(state, jury_prompt, "Jury", config)

            # Return only the formatted result
            return jury_state["result"]
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            logging.error(traceback.format_exc())
            return None

    # After the stream_debate function
    with st.spinner("Debate in progress..."):
        final_decision = asyncio.run(stream_debate())

    st.success("Debate finished!")
    st.markdown("<hr style='border: 2px solid #e0e0e0; margin: 30px 0;'>", unsafe_allow_html=True)

    # Display the final decision
    if final_decision:
        st.markdown("<h2 style='text-align: center;'>Jury's Decision</h2>", unsafe_allow_html=True)

        for section in final_decision:
            if "🏆" in section["title"]:
                color = "#FFD700"  # Gold
            elif "🎭" in section["title"]:
                color = "#4CAF50"  # Green
            elif "🌟" in section["title"]:
                color = "#F44336"  # Red
            elif "💡" in section["title"]:
                color = "#9C27B0"  # Purple
            else:
                color = "#607D8B"  # Blue Grey

            formatted_html = format_jury_section(section["title"], section["content"], color)
            st.markdown(formatted_html, unsafe_allow_html=True)
    else:
        st.error("An error occurred during the debate. No final decision was reached.")