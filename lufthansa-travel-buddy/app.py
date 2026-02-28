import streamlit as st
import asyncio
from travel_buddy.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

st.set_page_config(
    page_title="Lufthansa Travel Buddy",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Lufthansa Business Travel Buddy")
st.caption("Proactive disruption manager for business travelers")

if "runner" not in st.session_state:
    st.session_state.session_id = "streamlit-session"
    st.session_state.messages = []
    st.session_state.session_service = InMemorySessionService()
    st.session_state.runner = Runner(
        agent=root_agent,
        app_name="lufthansa_travel_buddy",
        session_service=st.session_state.session_service,
    )
    asyncio.run(
        st.session_state.session_service.create_session(
            app_name="lufthansa_travel_buddy",
            user_id="streamlit-user",
            session_id=st.session_state.session_id,
        )
    )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about your flight, delays, or travel plans..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Checking flights..."):
            async def get_response():
                user_message = Content(
                    role="user",
                    parts=[Part(text=prompt)]
                )
                response_text = ""
                async for event in st.session_state.runner.run_async(
                    user_id="streamlit-user",
                    session_id=st.session_state.session_id,
                    new_message=user_message,
                ):
                    if hasattr(event, 'content') and event.content:
                        if hasattr(event.content, 'parts'):
                            for part in event.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    response_text += part.text
                return response_text
            
            response = asyncio.run(get_response())
            if response:
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                st.warning("No response received")

with st.sidebar:
    st.header("Quick Actions")
    if st.button("Check LH400 Status"):
        st.session_state.messages.append({"role": "user", "content": "Check the status of flight LH400 today"})
        st.rerun()
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
