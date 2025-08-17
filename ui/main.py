# main.py
import streamlit as st
from agents.planner import planner_agent
from agents.coder import coder_agent
from dotenv import load_dotenv
import os

# Setup
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Please set OPENAI_API_KEY")

st.set_page_config(layout="wide")
st.sidebar.header("Agentic IDE")

# Session state
if "frontend_files" not in st.session_state:
    st.session_state.frontend_files = {}
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []
if "spec_text" not in st.session_state:
    st.session_state.spec_text = ""

# User input
user_prompt = st.sidebar.text_area("Enter your main request:", "")
enhancement_prompt = st.sidebar.text_area("Enhancement / refine output:", "")

tabs = st.tabs(["📂 Project Structure", "💻 Code Viewer", "🛠️ Agent Logs", "🚀 Live Preview"])

frontend_files = st.session_state.frontend_files

# Run Agents (batched)
tasks = []
if enhancement_prompt:
    st.session_state.spec_text = enhancement_prompt  # keep only latest full spec
    tasks = planner_agent(enhancement_prompt, api_key=api_key)
elif user_prompt:
    st.session_state.spec_text = user_prompt
    tasks = planner_agent(user_prompt, api_key=api_key)

if tasks:
    updated_files = coder_agent(
        tasks=tasks,
        api_key=api_key,
        existing_files=frontend_files if enhancement_prompt else None,
        spec_text=st.session_state.spec_text
    )
    frontend_files.update(updated_files)
    st.session_state.agent_logs.append(
        f"{'Enhancement' if enhancement_prompt else 'Planner'} | Tasks: {[t['task'] for t in tasks]} | Updated: {list(updated_files.keys())}"
    )
    st.session_state.frontend_files = frontend_files

# Tabs content
with tabs[0]:
    st.write("### Project Files")
    for fname in frontend_files:
        st.write(f"- {fname}")

with tabs[1]:  # Code Viewer / Editor
    st.write("### Generated Code / Editor")
    with st.expander("Code Editor", expanded=True):
        html_code = st.text_area("index.html", frontend_files.get("index.html",""), height=200, key="html_editor")
        css_code = st.text_area("style.css", frontend_files.get("style.css",""), height=200, key="css_editor")
        js_code = st.text_area("script.js", frontend_files.get("script.js",""), height=200, key="js_editor")

        if st.button("💾 Save"):
            st.session_state.frontend_files["index.html"] = html_code
            st.session_state.frontend_files["style.css"] = css_code
            st.session_state.frontend_files["script.js"] = js_code
            st.experimental_rerun()  # refresh live preview after save

with tabs[2]:
    st.write("### Agent Execution Logs")
    if st.session_state.agent_logs:
        for log in st.session_state.agent_logs:
            st.write(log)
    else:
        st.write("Awaiting user request...")

with tabs[3]:
    st.write("### Live Preview")
    if frontend_files:
        html_content = frontend_files.get("index.html","")
        css_content = frontend_files.get("style.css","")
        js_content = frontend_files.get("script.js","")

        if "</head>" in html_content:
            html_content = html_content.replace("</head>", f"<style>{css_content}</style></head>", 1)
        else:
            html_content = f"<style>{css_content}</style>\n" + html_content

        if "</body>" in html_content:
            html_content = html_content.replace("</body>", f"<script>{js_content}</script></body>", 1)
        else:
            html_content = html_content + f"\n<script>{js_content}</script>"

        st.components.v1.html(html_content, height=600, scrolling=True)
    else:
        st.write("Live preview will appear here once frontend files are generated.")
