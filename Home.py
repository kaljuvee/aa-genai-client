import streamlit as st

st.set_page_config(page_title="Process Control AI Assistant", page_icon="🏠")

st.title("APC GenAI - Evaluation Tool")

st.markdown("""
Welcome to the Process Control AI Assistant! This application provides intelligent chat interfaces for different process control systems.

### Available Systems:

1. **APC-J141-LIC-005C**
   - Chat interface for the Level Indicator Controller system
   - Access historical data and operational insights
   - Get expert guidance on system behavior and troubleshooting

2. **APC-J140-BIN-005C**
   - Interactive chat for the Binary Control system
   - Analyze system performance and parameters
   - Understand operational patterns and anomalies

3. **APC-J141-LIC-002-004C**
   - Chat interface for the dual Level Indicator Controller system
   - Access combined system insights and interactions
   - Get guidance on interconnected system behaviors

### How to Use:

1. **Select a System**: Choose your desired system from the sidebar navigation
2. **Configure Settings**:
   - Choose your preferred AI model from the dropdown:
     - GPT-4O: Optimized for process control
     - GPT-4O-Mini: Faster, lighter version
     - GPT-4/GPT-4-Turbo: General purpose models
   - Customize the system prompt if needed
   
3. **Ask Questions**:
   - Type your questions in the chat input
   - Get AI-powered responses based on system data
   - View conversation history in the chat window

4. **Session Management**:
   - Use the "Refresh Session" button to start a new conversation
   - Your chat history is preserved during your session

### System Messages:
Navigate to the "System Alerts Viewer" to see enriched system alerts and their analysis.

Start exploring by selecting a system from the sidebar! 👈
""")

st.sidebar.success("Select a system above.")
