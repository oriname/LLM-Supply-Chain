import os
import importlib
import sys
import pandas as pd
import matplotlib.pyplot as plt 
import streamlit as st
from io import BytesIO
from modules.table_tool import PandasAgent
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar
from modules.history import ChatHistory

def reload_module(module_name):
    """For updating changes
    made to modules in localhost (press r)"""

    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    return sys.modules[module_name]

table_tool_module = reload_module('modules.table_tool')
layout_module = reload_module('modules.layout')
utils_module = reload_module('modules.utils')
sidebar_module = reload_module('modules.sidebar')
#history_module = reload_module('modules.history')

#ChatHistory = history_module.ChatHistory
Layout = layout_module.Layout
Utilities = utils_module.Utilities
Sidebar = sidebar_module.Sidebar

st.set_page_config(layout="wide", page_icon="📈", page_title="ChainBotAI")

layout, sidebar, utils = Layout(), Sidebar(), Utilities()

layout.show_header("CSV, Excel")

user_api_key = utils.load_api_key()
os.environ["OPENAI_API_KEY"] = user_api_key

if not user_api_key:
    layout.show_api_key_missing()

else:
    st.session_state.setdefault("reset_chat", False)
    uploaded_file = utils.handle_upload(["csv", "xlsx"])

    if uploaded_file:
        # Configure the sidebar
        sidebar.show_options()
        #sidebar.about()
        
        uploaded_file_content = BytesIO(uploaded_file.getvalue())
        if uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" or uploaded_file.type == "application/vnd.ms-excel":
            df = pd.read_excel(uploaded_file_content)
        else:
            df = pd.read_csv(uploaded_file_content)
        
        def show_csv_file(uploaded_file):
                file_container = st.expander("Data Quick Glance:")
                uploaded_file.seek(0) # Ensure starting from the beginning
                shows = pd.read_csv(uploaded_file)
                file_container.write(shows)
                #uploaded_file.seek(0)  # Reset file pointer to the beginning after reading
        # Show the contents of the file based on its extension
        def get_file_extension(uploaded_file):
            return os.path.splitext(uploaded_file)[1].lower()
        
        file_extension = get_file_extension(uploaded_file.name)

            # Show the contents of the file based on its extension
        if file_extension == ".csv" :
            show_csv_file(uploaded_file)
        
        # After processing the uploaded file:
        st.session_state.df = df

        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []
        csv_agent = PandasAgent()

        # Create containers for responses and prompts
        response_container = st.container()
        prompt_container = st.container()

        # Display chat history and responses in the response_container
        with response_container:
            csv_agent.display_chat_history()

        # Display the chat box in the prompt_container
        with prompt_container:
            is_ready, user_input = layout.prompt_form()
            if is_ready:
                result, captured_output = csv_agent.get_agent_response(df, user_input)
                cleaned_thoughts = csv_agent.process_agent_thoughts(captured_output)
                csv_agent.display_agent_thoughts(cleaned_thoughts)
                csv_agent.update_chat_history(user_input, result)
        
        if st.session_state.df is not None:
            st.subheader("Current dataframe:")
            #st.write(st.session_state.df)
