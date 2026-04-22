"""
Untuk jalankan,

python app2.py
"""

import getpass
import os
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

GOOGLE_API_KEY = getpass.getpass("Enter your API key: ")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
print()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

messages_history: list = [
    SystemMessage(
        "You are a comedian that knows a lot about Bali. Always response in less than 3 sentences"
    )   
]

while True: 
    user_prompt = input("User: ")
    messages_history.append(HumanMessage(user_prompt))
    response = llm.invoke(messages_history)
    messages_history.append(response)
    print(f"AI: {response.content}")
