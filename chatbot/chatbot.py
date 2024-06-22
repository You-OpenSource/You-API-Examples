import uuid
from typing import Any, Dict, List
import json

import requests
import sseclient

import streamlit as st

SYSTEM_PROMPT = "You are a helpful smart assistant. Search the web and answer the correct question with ciations. You have access to the web to answer any question"


def build_prompt():
    prompt = ""
    for msg in st.session_state.messages:
        prompt += msg["role"] + ":\t" + msg["content"] + "\n"
    return prompt

ydc_api_key = st.secrets["YDC_API_KEY"]


def get_ydc_answer(messages, mode='smart', stream=False):
    query = build_prompt()
    headers = {'x-api-key': ydc_api_key, 'Content-Type': 'application/json'}
    endpoint = f"https://chat-api.you.com/{mode}" # use /research for Research mode
    params = {"query":query, "chat_id": st.session_state.chat_id}
    response = requests.post(endpoint, json=params, headers=headers)
    print(response)
    return response.json()

def get_ydc_stream_answer(mode='smart'):
    query = build_prompt()
    headers = {'x-api-key': ydc_api_key}

    endpoint = f"https://chat-api.you.com/{mode}" # use /research for Research mode
    params = {"query": query, "stream": True}
    headers = {
        'x-api-key': ydc_api_key,
    }
    response = requests.get(endpoint, headers=headers, params=params, stream=True)
    client = sseclient.SSEClient(response)
    for event in client:
        for event in response.iter_lines():
            if event.event == "token":
                yield (str(event.data))

    return None

# Better way to clear history
def clear_chat_history():
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state["messages"] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "What can I help you build today?"}
    ]


with st.sidebar:
    model_select = st.selectbox("Select a model", ["smart", "research"])
    st.button('Reset Chat', on_click=clear_chat_history)



st.title("💬 YOU.COM API ASSISTANT")
st.caption(""" 🚀 Let us help you build with You.com""")


if "messages" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state["messages"] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "What can I help you build today?"}
    ]

# Display or clear messages
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

# User provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)


# Generate response if last reponse not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        # Test no stream
        full_response = get_ydc_answer(model_select)["answer"]
        st.write(full_response)
        
        # Test Stream Currently not working
        #full_response = get_ydc_stream_answer(model_select)
        #st.write_stream(full_response)

        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)