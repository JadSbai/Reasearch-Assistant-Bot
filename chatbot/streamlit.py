import streamlit as st
import requests
from main_openai import llm, search_documents, generate_prompt, predict, upload_stream_file
from langchain.schema import AIMessage, HumanMessage

def modified_predict(message, history):
    # Retrieve relevant documents based on the message
    documents = search_documents(message)
    # Generate the prompt using the retrieved documents and the user message
    prompt = generate_prompt(message, documents)

    # Format the history for the llm
    history_formatted = []
    for human, ai in history:
        history_formatted.append(HumanMessage(content=human))
        history_formatted.append(AIMessage(content=ai))

    # Add the current prompt to the history
    history_formatted.append(HumanMessage(content=prompt))

    # Get the response from the llm
    gpt_response = llm(history_formatted)
    return gpt_response.content


# Initialize session state
if 'history' not in st.session_state:
    print('lol')
    st.session_state['history'] = []
if 'document_titles' not in st.session_state:
    st.session_state['document_titles'] = []

# Layout
st.title("Research Bot Assistant")
col1, col2 = st.columns((2, 1))

with col1:
    # Session Selector
    session_mode = st.selectbox("Choose Session Mode", ["Upload Papers", "Retrieve Papers by Theme"])

    # Chat Interface
    if session_mode == "Upload Papers":
        uploaded_files = st.file_uploader("Upload Papers", accept_multiple_files=True)
        for uploaded_file in uploaded_files:
            # Process each file
            upload_stream_file(uploaded_file)

    else:  # Retrieve Papers by Theme
        theme = st.text_input("Enter Research Theme")
        if st.button("Retrieve Papers"):
            documents = search_documents(theme)
            st.session_state['document_titles'] = [doc['title'] for doc in documents]

    # User Message Input
    user_message = st.text_input("Your Query")
    if st.button("Ask"):
        # Process the query based on the mode
        response = modified_predict(user_message, st.session_state['history'])
        st.session_state['history'].append((user_message, response))

    # Display Chat History
    for human, ai in st.session_state['history']:
        st.text_area("You", value=human, height=50, disabled=True)
        st.text_area("Bot", value=ai, height=50, disabled=True)

with col2:
    # Paper Display Panel
    st.subheader("Papers in Use")
    for title in st.session_state['document_titles']:
        st.write(title)


# Run the Streamlit app
# if __name__ == "__main__":
#     st.run()
