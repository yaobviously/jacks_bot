# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 19:12:18 2023

@author: yaobv
"""
import os
import openai
import streamlit as st

from streamlit_chat import message
from dotenv import load_dotenv

load_dotenv()

# defining page header
st.set_page_config(page_title="Jack's Bot", page_icon=":robot_face:")
st.markdown("<h1 style='text-align: center;'>Jack's Personal Bot 😬</h1>", unsafe_allow_html=True)

# setting org and key
openai.organization = os.environ.get('OPENAI_ORG')
openai.api_key = os.environ.get('OPENAI_KEY')

# initializing state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "You are an enthusiastic teacher. Santa Claus is real. Explain everything like I am 5. Keep explanations to one paragraph. Please refer to me as 'Jack' occasionally. Ask my follow-up questions sometimes."}
    ]
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0

# sidebar with suggested questions that i can modify now and again
st.sidebar.title("Suggestions")

how_question = st.sidebar.button("How do I..", key='how')
why_question = st.sidebar.button("Why does it..", key='why')
when_question = st.sidebar.button("When was the..", key='when')
who_question = st.sidebar.button("Who invented the..", key='who')
where_question = st.sidebar.button("Where in the world is", key='where')
what_question = st.sidebar.button("What is a..", key='what')
clear_button = st.sidebar.button("Clear Conversation", key="clear")

if how_question:
    text = 'How do I'
elif why_question:
    text = 'Why does it'
elif when_question:
    text = 'When was that'
elif who_question:
    text = 'Who invented the'
elif where_question:
    text = 'Where in the world is'
elif what_question:
    text = 'What is a'
else:
    text = ''
    
# map model names to openai names. gpt3.5 for now
model_name = "GPT-3.5"

if model_name == "GPT-3.5":
    model = "gpt-3.5-turbo"
else:
    model = "gpt-4"

# reset everything
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [
        {"role": "system", "content": "You are an enthusiastic teacher. Santa Claus is real. Explain everything like I am 5. Keep explanations to one paragraph. Please refer to me as 'Jack' occasionally. Ask my follow-up questions sometimes."}
    ]
    st.session_state['number_tokens'] = []
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_cost'] = 0.0
    st.session_state['total_tokens'] = []


# generate a response
def generate_response(prompt):
    st.session_state['messages'].append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model=model,
        messages=st.session_state['messages']
    )
    response = completion.choices[0].message.content
    st.session_state['messages'].append({"role": "assistant", "content": response})

    # print(st.session_state['messages'])
    total_tokens = completion.usage.total_tokens
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    return response, total_tokens, prompt_tokens, completion_tokens


# container for chat history
response_container = st.container()
# container for text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100, value=text)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['model_name'].append(model_name)
        st.session_state['total_tokens'].append(total_tokens)

        # from https://openai.com/pricing#language-models
        if model_name == "GPT-3.5":
            cost = total_tokens * 0.002 / 1000
        else:
            cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000

        st.session_state['cost'].append(cost)
        st.session_state['total_cost'] += cost

if st.session_state['generated']:
    with response_container:
            message(st.session_state["past"][-1], is_user=True, key='_user')
            message(st.session_state["generated"][-1], key='bot')
            print(st.session_state["generated"])
            st.write(
                f"Model used: {st.session_state['model_name'][-1]}; Number of tokens: {st.session_state['total_tokens'][-1]}; Cost: ${st.session_state['cost'][-1]:.5f}")