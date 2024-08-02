import streamlit as st
import replicate
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set page configuration
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

# Get Replicate API token from environment variable
replicate_api = os.getenv('REPLICATE_API_TOKEN')

if not replicate_api:
    st.error('Replicate API token not found. Please add it to the .env file.')
else:
    # Set the Replicate API token
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    # Define the model and parameters
    llm = os.getenv('MODEL_NAME')
    temperature = float(os.getenv('TEMPERATURE', 0.1))
    top_p = float(os.getenv('TOP_P', 0.9))
    max_length = int(os.getenv('MAX_LENGTH', 120))

    # Load FAQ data from JSON file
    with open('data.json') as f:
        faq_data = json.load(f)

    # Set app title
    st.title('🦙💬 Llama 2 Chatbot')

    # Store LLM generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

    # Function for generating LLaMA2 response
    def generate_llama2_response(prompt_input):
        # Check if the prompt matches any FAQ
        if prompt_input in faq_data:
            return [faq_data[prompt_input]]
        
        # If not an FAQ, use the LLM to generate a response
        string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
        for dict_message in st.session_state.messages:
            if dict_message["role"] == "user":
                string_dialogue += "User: " + dict_message["content"] + "\n\n"
            else:
                string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
        output = replicate.run(
            llm, 
            input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                   "temperature": temperature, "top_p": top_p, "max_length": max_length, "repetition_penalty": 1}
        )
        return output

    # User-provided prompt
    if prompt := st.chat_input(disabled=not replicate_api):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    # Generate a new response if the last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_llama2_response(prompt)
                placeholder = st.empty()
                full_response = ''
                for item in response:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)