import streamlit as st
from utils.api_util import get_chat_response
import uuid

# Controller ID for this page
CONTROLLER_ID = "pwo-sep-t-crushing-pwo"

# Streamlit UI
st.title("PWO-SEP-T-CRUSHING-PWO Chat")

# Sidebar for model selection
st.sidebar.title("Settings")

# Initialize session ID if not exists
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Refresh session button
if st.sidebar.button("Refresh Session"):
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())
    st.rerun()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is your question?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get response from API
    response_data = get_chat_response(
        question=prompt,
        controller_id=CONTROLLER_ID,
        session_id=st.session_state.session_id
    )
    
    response = response_data.get("answer", "Sorry, I couldn't get a response")
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
