import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="Chatbot LLAMA 2 🦙💬")

# Credenciais
with st.sidebar:
    st.title('Chatbot utilizando LLAMA 2 🦙💬')
    st.write('Esse chatbot é apenas um MVP do que pode ser feito em relação à Chatbots e à utilização de LLMs em soluções de dados.')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API Pronta!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Escreva sua API_KEY:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Preencha o campo!', icon='⚠️')
        else:
            st.success('Agora execute seu prompt!', icon='👉')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api
    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
    if selected_model == 'Llama2-7B':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'Llama2-13B':
        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=150, max_value=1550, value=300, step=10)

# Manter chat
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Como posso te ajudar?"}]

# Display Mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Como posso te ajudar?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Respostas do modelo
def generate_llama2_response(prompt_input):
    string_dialogue = "Use only the portugese language to answer all the question (specifically brazillian portuguese). If it is a bussiness related question, answer it lika a consultant would do."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
    return output

# Prompt do usuário
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Gerar nova resposta
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Pensando"):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)