import streamlit as st
import json
from pathlib import Path

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

st.title("System Alerts Viewer")

# Load the JSON data
json_path = Path("reports/system_alerts_enriched.json")
data = load_json(json_path)

# Display each message in an expander
for i, message in enumerate(data, 1):
    with st.expander(f"Message {i}: {message['original_message'][:100]}..."):
        st.write("**Treshold Violation:**")
        st.write(message['original_message'])

        st.write("**Gains Context:**")
        st.write(message['gains_context'])
        
        gains_context = message['gains_context']
        st.write("**Question to Model:**")
        st.write(message['follow_up_question'])
        
        st.write("**Model Response:**")
        st.write(message['follow_up_answer'])
