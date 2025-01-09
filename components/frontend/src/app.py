import os
import logging
import utils
import streamlit as st
import json
import requests
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()


BACKEND_URL = BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
url = f"{BACKEND_URL}/bot/v1/chat"

thread_id = str(uuid4())
reqHeaders = {"Accept": "application/json", "Content-Type": "application/json"}

st.set_page_config(
    page_title="Procurement Assistant Chatbot", page_icon="📄", layout="wide"
)


@utils.enable_chat_history
def main():
    with st.sidebar:
        st.title("Procurement Assistant Chatbot")

    user_query = st.chat_input(placeholder="Ask me anything!")

    if user_query:
        utils.display_msg(user_query, "user")
        with st.chat_message("assistant"):
            payload = {"user_message": user_query, "thread_id": thread_id}

            with st.spinner("Processing..."):
                response = requests.post(url, headers=reqHeaders, json=payload)
                if response.status_code != 200:
                    st.error(f"Error: {response.status_code} - {response.text}")
                    return

                try:
                    response_data = response.json()
                    assistant_message = response_data.get(
                        "bot_response", "I'm sorry, I couldn't process your query."
                    )
                    st.markdown(assistant_message)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": assistant_message}
                    )
                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding JSON response: {e}")
                    st.error(
                        "There was an error processing the response. Please try again."
                    )


if __name__ == "__main__":
    main()
