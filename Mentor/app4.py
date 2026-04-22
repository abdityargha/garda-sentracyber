import streamlit as st
import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import fitz

st.title("Salam Bela Negara")


if "GOOGLE_API_KEY" not in os.environ:
    google_api_key = st.text_input("Google API Key", type="password")
    start_button = st.button("Start")
    if start_button:
        os.environ["GOOGLE_API_KEY"] = google_api_key
        st.rerun()
    st.stop()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

if "participant_resume" not in st.session_state:
    uploaded_pdf = st.file_uploader("Upload CV", type="pdf")
    if uploaded_pdf:
        pdf_bytes = uploaded_pdf.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = "\n".join([page.get_text() for page in doc])
        st.session_state["participant_resume"] = text
        st.rerun()
    st.stop()
resume = st.session_state["participant_resume"]


if "messages_history" not in st.session_state:
    st.session_state["messages_history"] = [
        SystemMessage(
            "You are a resume reviewer, this is the resume you are going to review {context}".format(context=resume)
        )  
    ]
messages_history = st.session_state["messages_history"]

for message in messages_history:
    if type(message) is SystemMessage:
        continue
    role = "User" if type(message) is HumanMessage else "AI"
    with st.chat_message(role):
        st.markdown(message.content)

prompt = st.chat_input("Chat with AI")
if not prompt:
    st.stop()
messages_history.append(HumanMessage(prompt))
with st.chat_message("User"):
    st.markdown(prompt)

response = llm.invoke(messages_history)
messages_history.append(response)
with st.chat_message("AI"):
    st.markdown(response.content)