import streamlit as st

# Initialize session state for login status
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Hardcoded credentials (in a real application, this should be more secure)
VALID_EMAIL = "genai@angloamerican.com"
VALID_PASSWORD = "GenAI2$2"

def login():
    st.session_state.logged_in = True

def logout():
    st.session_state.logged_in = False

# Custom CSS to hide sidebar when not logged in
def local_css():
    style = """
    <style>
    #MainMenu {visibility: hidden;}
    .stSidebar {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    if not st.session_state.logged_in:
        st.markdown(style, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Process Control AI Assistant", page_icon="🏠")
    local_css()

    if st.session_state.logged_in:
        # Show sidebar when logged in
        st.markdown(
            """
            <style>
            .stSidebar {visibility: visible;}
            </style>
            """,
            unsafe_allow_html=True
        )
        
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
        2. **Ask Questions**:
           - Type your questions in the chat input
           - Get AI-powered responses based on system data
           - View conversation history in the chat window

        3. **Session Management**:
           - Use the "Refresh Session" button to start a new conversation
           - Your chat history is preserved during your session

        ### System Alerts Viewer (Coming Soon):
        Navigate to the "System Alerts Viewer" to see enriched system alerts and their analysis.

        Start exploring by selecting a system from the sidebar! 👈
        """)

        st.sidebar.success("Select a system above.")
        
        if st.sidebar.button('Logout'):
            logout()
            st.rerun()
    else:
        st.title('Login')
        email = st.text_input('Email')
        password = st.text_input('Password', type='password')
        
        if st.button('Login'):
            if email == VALID_EMAIL and password == VALID_PASSWORD:
                login()
                st.rerun()
            else:
                st.error('Invalid email or password')

if __name__ == "__main__":
    main()
