import streamlit as st
import os
import time
from dotenv import load_dotenv
from langchain_core.runnables.config import RunnableConfig

from agent.graph import master_graph
from utils.pdf_export import generate_pdf

load_dotenv()

st.set_page_config(page_title="Multi-Agent Research Assistant", layout="wide")
st.title("🤖 Multi-Agent Research Assistant")

# Initialize session thread ID for LangGraph checkpointer memory
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(time.time())

config: RunnableConfig = {"configurable": {"thread_id": st.session_state.thread_id}}

topic = st.text_input("Enter a Research Topic:")

if st.button("Start Research"):
    # Generate new thread for new topic session
    st.session_state.thread_id = str(time.time())
    config = {"configurable": {"thread_id": st.session_state.thread_id}}  # type: ignore[assignment]
    
    with st.spinner("Researching and Analyzing..."):
        for event in master_graph.stream({"topic": topic}, config):  # type: ignore[arg-type]
            for k, v in event.items():
                if k == "research":
                    st.toast("Research completed!")
                elif k == "analysis":
                    st.toast("Analysis completed!")
    
    st.rerun()

# Retrieve current state to handle interruptions
state = master_graph.get_state(config)  # type: ignore[arg-type]

if state and state.next and "writer" in state.next:
    st.info("Analysis is complete. Please review the outline before drafting the final report.")
    with st.expander("View Analysis Outline", expanded=True):
        st.write(state.values.get("analysis", "No analysis found..."))
        
    if st.button("Approve & Write Report"):
        with st.spinner("Writing and Critiquing Report..."):
            # Resuming graph execution with None after hitl interruption
            for event in master_graph.stream(None, config):  # type: ignore[arg-type]
                for k, v in event.items():
                    if k == "writer":
                        st.toast("Draft Report Written!", icon="✍️")
                    elif k == "critic":
                        st.toast("Critic Node Reviewing...", icon="🧐")
        st.rerun()

elif state and not state.next and state.values.get("draft_report"):
    st.success("Final Report is Ready!")
    st.markdown("### Final Report")
    
    with st.expander("View Final Report Draft", expanded=True):
        st.markdown(state.values["draft_report"])
    
    safe_topic = state.values['topic'].replace(' ', '_').replace(':', '')
    pdf_path = f"{safe_topic}_Report.pdf"
    
    # We dynamically generate the PDF directly for the download button
    if st.button("Prepare PDF Document"):
        with st.spinner("Generating PDF formatting..."):
            generate_pdf(
                topic=state.values["topic"],
                markdown_content=state.values["draft_report"],
                search_results=state.values.get("search_results", []),
                output_filename=pdf_path
            )
            
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name=pdf_path,
            mime="application/pdf"
        )
