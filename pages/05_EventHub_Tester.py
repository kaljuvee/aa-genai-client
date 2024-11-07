import streamlit as st
import json
from datetime import datetime
from utils.api_util import get_api_response

# Streamlit UI
st.title("EventHub Tester")

# Initialize session state for message log if not exists
if "message_log" not in st.session_state:
    st.session_state.message_log = []

# Documentation section
with st.expander("API Documentation"):
    st.markdown("""
    ### EventHub Testing Interface

    #### Send Test Message
    **Endpoint:** `/api/eventhub/send`  
    **Method:** POST  
    **Description:** Sends a predefined test message to the configured EventHub destination.

    **Test Message Format:**
    ```json
    {
        "id": "1",
        "processCell": "TestCell",
        "apc": "TestAPC",
        "tag": "TestTag",
        "tagValue": "TestValue",
        "enhancedPromptTitle": "Test Enhanced Title",
        "enhancedPromptMessageDetails": "Test Enhanced Message Details",
        "created": "2024-XX-XXTXX:XX:XX.XXXZ",
        "updated": "2024-XX-XXTXX:XX:XX.XXXZ"
    }
    ```

    #### Read Messages
    **Endpoint:** `/api/eventhub/read`  
    **Method:** POST  
    **Description:** Initiates a 10-second reading session from the configured EventHub source.
    """)

# Test Message Configuration
st.subheader("Test Message Configuration")
col1, col2 = st.columns(2)

with col1:
    process_cell = st.text_input("Process Cell", value="TestCell")
    apc = st.text_input("APC", value="TestAPC")
    tag = st.text_input("Tag", value="TestTag")
    tag_value = st.text_input("Tag Value", value="TestValue")

with col2:
    enhanced_title = st.text_input("Enhanced Prompt Title", value="Test Enhanced Title")
    enhanced_details = st.text_area("Enhanced Prompt Message Details", 
                                  value="Test Enhanced Message Details",
                                  height=100)

# Send Test Message Button
if st.button("Send Test Message"):
    try:
        # Prepare the test message
        test_message = {
            "id": "1",
            "processCell": process_cell,
            "apc": apc,
            "tag": tag,
            "tagValue": tag_value,
            "enhancedPromptTitle": enhanced_title,
            "enhancedPromptMessageDetails": enhanced_details,
            "created": datetime.utcnow().isoformat() + "Z",
            "updated": datetime.utcnow().isoformat() + "Z"
        }

        # Send the message using the API utility
        response = get_api_response(
            "/eventhub/send",
            method="POST",
            payload=test_message
        )

        # Show API details in expander
        with st.expander("View API Details"):
            st.write("**Request:**")
            st.code(f"POST /api/eventhub/send\n\n{json.dumps(test_message, indent=2)}", 
                   language="http")
            st.write("**Response:**")
            st.json(response)

        if not response.get("error"):
            st.success(response.get("data", {}).get("message", "Message sent successfully"))
        else:
            st.error(f"Error: {response.get('message', 'Unknown error occurred')}")

    except Exception as e:
        st.error(f"Error sending message: {str(e)}")

# Read Messages Button
st.subheader("Read Messages")
st.write("Click the button below to start a 10-second reading session from EventHub.")

if st.button("Start Reading Messages"):
    try:
        with st.spinner("Reading messages for 10 seconds..."):
            # Call the read endpoint
            response = get_api_response("/eventhub/read", method="POST")

            # Show API details in expander
            with st.expander("View API Details"):
                st.write("**Request:**")
                st.code("POST /api/eventhub/read", language="http")
                st.write("**Response:**")
                st.json(response)

            if response.get("status") == "success":
                st.success(response.get("message", "Reading session completed"))
                # Add any received messages to the log
                if "data" in response:
                    st.session_state.message_log.extend(response["data"])
            else:
                st.error(f"Error: {response.get('message', 'Unknown error occurred')}")

    except Exception as e:
        st.error(f"Error reading messages: {str(e)}")

# Message Log
st.subheader("Message Log")
if st.session_state.message_log:
    for message in st.session_state.message_log:
        with st.expander(f"Message {message.get('id', 'Unknown')} - "
                        f"{message.get('created', 'Unknown time')}"):
            st.json(message)
else:
    st.info("No messages in log. Start a reading session to see messages.")

# Clear Log Button
if st.session_state.message_log and st.button("Clear Message Log"):
    st.session_state.message_log = []
    st.rerun()
