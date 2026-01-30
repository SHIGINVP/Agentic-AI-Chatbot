
# # from dotenv import load_dotenv
# # load_dotenv()


#Step1: Setup UI with streamlit (model provider, model, system prompt, web_search, query)
import streamlit as st
import requests




def sanitize_messages(messages):
    """
    Normalize and sanitize chat messages before processing.

    This function ensures that each message in the chat history
    has a valid string-based `content` field. It is primarily used
    to handle cases where the assistant response may be returned
    as a dictionary (e.g., {"response": "..."}), which can cause
    validation errors in downstream processing or API requests.

    The function converts all message contents to strings and
    preserves the original message roles.

    Args:
        messages (list[dict]):
            A list of message objects representing the chat history.
            Each message is expected to contain:
            - "role" (str): The role of the sender (e.g., "user", "assistant")
            - "content" (str | dict): The message content or response payload

    Returns:
        list[dict]:
            A cleaned list of message objects where:
            - "content" is guaranteed to be a string
            - "role" remains unchanged

    Example:
        >>> sanitize_messages([
        ...     {"role": "assistant", "content": {"response": "Hello"}},
        ...     {"role": "user", "content": "Hi"}
        ... ])
        [
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "Hi"}
        ]
    """
    cleaned = []
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, dict):
            content = content.get("response", "")
        cleaned.append({
            "role": msg.get("role"),
            "content": str(content)
        })
    return cleaned




# -----------------------------------------------------------
# Page configuration
# Sets the browser tab title and defines a centered layout
# -----------------------------------------------------------
st.set_page_config(
    page_title="Agentic AI Assistant",
    layout="centered"
)


# -----------------------------------------------------------
# Header layout
# Create two columns:
# - Left column for assistant icon
# - Right column for title and description
# ----------------------------------------------------------

col1, col2 = st.columns([1, 6])



# -----------------------------------------------------------
# Left column: AI assistant icon
# Displayed as a large emoji using custom HTML styling
# -----------------------------------------------------------
with col1:
    st.markdown(
        "<div style='font-size:60px; text-align:center;'>🤖</div>",
        unsafe_allow_html=True
    )




# -----------------------------------------------------------
# Right column: Application title and subtitle
# Uses HTML for precise control over typography and spacing
# -----------------------------------------------------------
with col2:
    st.markdown(
        """
        <h1 style='margin-bottom:0;'>Agentic AI Assistant</h1>
        <p style='font-size:18px; color: gray; margin-top:5px;'>
        Chat with a memory-enabled, tool-using AI agent
        </p>
        """,
        unsafe_allow_html=True
    )



# -----------------------------------------------------------
# Visual separator between header and main application content
# -----------------------------------------------------------
st.divider()



# -----------------------------------------------------------
# Sidebar section: Agent configuration controls
# -----------------------------------------------------------
st.sidebar.markdown("## Agent Settings")





# -----------------------------------------------------------
# Supported model lists by provider
# These values are used to dynamically populate the model selector
# -----------------------------------------------------------
MODEL_NAMES_GROQ = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
MODEL_NAMES_OPENAI = ["gpt-4o-mini"]






# -----------------------------------------------------------
# Model provider selection
# Allows the user to choose between supported LLM providers
# -----------------------------------------------------------
provider = st.sidebar.radio(
    "Model Provider",
    ("Groq", "OpenAI")
)




# -----------------------------------------------------------
# Model selection dropdown
# Displays available models based on the selected provider
# -----------------------------------------------------------
if provider == "Groq":
    selected_model = st.sidebar.selectbox("Model", MODEL_NAMES_GROQ)
else:
    selected_model = st.sidebar.selectbox("Model", MODEL_NAMES_OPENAI)



# -----------------------------------------------------------
# Sidebar separator for visual clarity
# -----------------------------------------------------------
st.sidebar.divider()


# -----------------------------------------------------------
# Clear conversation state
# Resets the stored chat history and refreshes the UI
# -----------------------------------------------------------
if st.sidebar.button("Clear Conversation"):
    st.session_state.chat_history = []
    st.rerun()


# --------------------------------
# Initialize Memory
# --------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --------------------------------
# System Prompt (Act As)
# --------------------------------
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("**Act as:**")

with col2:
    system_prompt = st.text_input(
        "",
        placeholder="e.g., Senior Data Scientist, AI Tutor, Career Coach"
    )


# --------------------------------
# Display Chat History
# --------------------------------
st.divider()


for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])



# # --------------------------------
# # User Input Area
# # --------------------------------
allow_web_search = st.checkbox("Allow Web Search")

user_query = st.chat_input("Type your message...")


# -----------------------------------------------------------
# Backend API endpoint
# Defines the URL used to communicate with the FastAPI backend
# -----------------------------------------------------------
API_URL="http://127.0.0.1:9999/chat"



# -----------------------------------------------------------
# Handle user input submission
# Triggered when the user enters a message in the chat input
# -----------------------------------------------------------
if user_query:
    
    
    # -------------------------------------------------------
    # Store the user's message in session state
    # This preserves conversation history across interactions
    # -------------------------------------------------------
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_query
    })


    # -------------------------------------------------------
    # Construct the request payload for the backend API
    # -------------------------------------------------------
    payload = {
        # Selected LLM and provider configuration
        "model_name": selected_model,
        "model_provider": provider,

        # System prompt that controls agent behavior and response style
        "system_prompt": f"""
                        {system_prompt}

                        Explain the topic in a clear, human-friendly way.
                        Rules:
                        - Do NOT start with Yes or No
                        - Do NOT give one-word answers
                        - Start directly with the explanation
                        - Use bullet points
                        - Keep it simple and natural
                        """,

        # Sanitized chat history to prevent schema and type errors
        "messages": sanitize_messages(st.session_state.chat_history),

        # Flag indicating whether the agent may use web search tools
        "allow_search": allow_web_search
    }


    # -------------------------------------------------------
    # Send the request to the backend AI service
    # -------------------------------------------------------
    response = requests.post(API_URL, json=payload)


    # -------------------------------------------------------
    # Handle successful backend response
    # -------------------------------------------------------
    if response.status_code == 200:
        response_data = response.json()


        # ---------------------------------------------------
        # Backend-level error handling
        # ---------------------------------------------------
        if "error" in response_data:
            st.error(response_data["error"])
        else:
            # Extract assistant's textual response
            assistant_text = response_data.get("response", "")


            # ------------------------------------------------
            # Store assistant response in session state
            # ------------------------------------------------
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": assistant_text
            })

            # ------------------------------------------------
            # Rerender UI to display updated chat history
            # ------------------------------------------------
            st.rerun()

    # -------------------------------------------------------
    # Handle backend connection or server errors
    # -------------------------------------------------------
    else:
        st.error(f"Error {response.status_code}: {response.text}")








