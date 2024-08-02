import streamlit as st
import replicate
import json

# Set page configuration
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

# Get Replicate API token and other parameters from Streamlit secrets
replicate_api = st.secrets.get("REPLICATE_API_TOKEN")
model_name = st.secrets.get("MODEL_NAME")
temperature = float(st.secrets.get("TEMPERATURE", 0.1))
top_p = float(st.secrets.get("TOP_P", 0.9))
max_length = int(st.secrets.get("MAX_LENGTH", 120))

if not replicate_api:
    st.error('Replicate API token not found. Please add it to the Streamlit secrets.')
else:
    try:
        replicate.Client(api_token=replicate_api)
    except Exception as e:
        st.error(f'Failed to initialize Replicate client: {e}')
    
    try:
        with open('data.json') as f:
            faq_data = json.load(f)
    except FileNotFoundError:
        st.error('data.json file not found. Please ensure the file is in the correct location.')
        faq_data = {}
    except json.JSONDecodeError:
        st.error('Error decoding data.json. Please ensure the file contains valid JSON.')
        faq_data = {}

    st.title('🦙💬 Llama 2 Chatbot')

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

    def generate_llama2_response(prompt_input):
        if prompt_input in faq_data:
            return [faq_data[prompt_input]]
        
        string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
        for dict_message in st.session_state.messages:
            if dict_message["role"] == "user":
                string_dialogue += "User: " + dict_message["content"] + "\n\n"
            else:
                string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
        try:
            output = replicate.run(
                model_name, 
                input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                       "temperature": temperature, "top_p": top_p, "max_length": max_length, "repetition_penalty": 1}
            )
            return output
        except Exception as e:
            st.error(f'Error generating response: {e}')
            return ["Sorry, there was an error processing your request."]

    if prompt := st.chat_input(disabled=not replicate_api):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

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
