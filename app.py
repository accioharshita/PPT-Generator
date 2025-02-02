__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import sys
import streamlit as st
from langtrace_python_sdk import langtrace
from src.edu_flow_v2.crews.researchers.researchers import Researchers
from src.edu_flow_v2.crews.writers.writers import Writers
from crewai.flow.flow import Flow, start, listen

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="PPT Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to make the app more attractive
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
        background-color: #FF4B4B;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    h1 {
        color: #FF4B4B;
        font-size: 2.5rem !important;
    }
    h3 {
        color: #31333F;
    }
    .api-key-warning {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .watermark {
        position: fixed;
        bottom: 20px;
        right: 20px;
        opacity: 0.5;
        font-size: 1rem;
        color: #666;
        z-index: 1000;
        font-family: 'Arial', sans-serif;
        letter-spacing: 2px;
        pointer-events: none;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for API Key Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("---")
    
    # OpenAI API Key
    openai_api_key = st.text_input("🔑 OpenAI API Key", type="password", key="openai_key")
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    else:
        st.markdown("""
            <div class="api-key-warning">
                ⚠️ OpenAI API Key is required!
            </div>
        """, unsafe_allow_html=True)

    # Serper API Key
    serper_api_key = st.text_input("🔑 Serper API Key", type="password", key="serper_key")
    if serper_api_key:
        os.environ["SERPER_API_KEY"] = serper_api_key
    else:
        st.markdown("""
            <div class="api-key-warning">
                ⚠️ Serper API Key is required!
            </div>
        """, unsafe_allow_html=True)

    # LangTrace API Key (Optional)
    st.markdown("---")
    with st.expander("🔧 Advanced Settings"):
        user_api_key = st.text_input("LangTrace API Key (Optional)", type="password")
        api_key = user_api_key.strip() if user_api_key else os.getenv("LANGTRACE_API_KEY")
        
        if api_key:
            langtrace.init(api_key=api_key)
        else:
            st.info("ℹ️ LangTrace API Key not provided. Using default config.")

# Main content
st.title("📄 PPT Generator")
st.markdown("### Transform Your Ideas into Professional Presentations")

# Create two columns for better layout
col1, col2 = st.columns([2, 1])

with col1:
    topic = st.text_input(
        "What would you like to create a presentation about?",
        placeholder="Enter your topic here...",
        help="Enter any topic and we'll generate a well-structured presentation for you!"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
    generate_button = st.button("🚀 Generate Presentation", use_container_width=True)

# Define the EduFlow class
class EduFlow(Flow):
    def __init__(self, input_variables=None):
        super().__init__()
        self.input_variables = input_variables or {}

    @start()
    def generate_researched_content(self):
        return Researchers().crew().kickoff(self.input_variables).raw

    @listen(generate_researched_content)
    def generate_educational_content(self, plan):
        return Writers().crew().kickoff(self.input_variables).raw

    @listen(generate_educational_content)
    def save_to_markdown(self, content):
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        topic = self.input_variables.get("topic")
        file_name = f"{topic}.md".replace(" ", "_")
        output_path = os.path.join(output_dir, file_name)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return output_path

# Handle generation
if generate_button:
    if not topic.strip():
        st.error("🎯 Please enter a topic to generate content.")
    elif not openai_api_key or not serper_api_key:
        st.error("🔑 Please enter both OpenAI and Serper API Keys in the sidebar.")
    else:
        # Use a spinner instead of st.write for the loading state
        with st.spinner("🎨 Crafting your presentation..."):
            # Run the flow
            input_variables = {"topic": topic}
            edu_flow = EduFlow(input_variables)
            output_path = edu_flow.kickoff()

            # Display final markdown file in Streamlit
            if output_path and os.path.exists(output_path):
                with open(output_path, "r", encoding="utf-8") as file:
                    markdown_content = file.read()
                
                # Create an expander for the content
                with st.expander("📑 Generated Presentation", expanded=True):
                    st.markdown(markdown_content, unsafe_allow_html=True)
                
                # Add download button
                st.download_button(
                    label="📥 Download Presentation",
                    data=markdown_content,
                    file_name=f"{topic}_presentation.md",
                    mime="text/markdown"
                )
            else:
                st.error("❌ Failed to generate presentation. Please try again.")

# Add Accredian watermark
st.markdown("""
    <div class="watermark">
        accredian
    </div>
""", unsafe_allow_html=True)