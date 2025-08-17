# main.py
import streamlit as st
from agents.planner import planner_agent
from agents.coder import coder_agent
from dotenv import load_dotenv
import os

# -------------------------------
# --- Setup
# -------------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ Please set the OPENAI_API_KEY environment variable")

st.set_page_config(layout="wide")
st.sidebar.header("Agentic IDE")

# -------------------------------
# --- Session State
# -------------------------------
if "frontend_files" not in st.session_state:
    st.session_state.frontend_files = {}  # {"index.html": "...", "style.css": "...", "script.js": "..."}

if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []

# ✅ NEW: keep the *full* spec across generations & enhancements
if "spec_text" not in st.session_state:
    st.session_state.spec_text = ""

# -------------------------------
# --- User Input
# -------------------------------
user_prompt = st.sidebar.text_area("Enter your main request:", "")
enhancement_prompt = st.sidebar.text_area("Enhancement / refine output:", "")

tabs = st.tabs(["📂 Project Structure", "💻 Code Viewer", "🛠️ Agent Logs", "🚀 Live Preview"])

# -------------------------------
# --- Run Agents
# -------------------------------
frontend_files = st.session_state.frontend_files

if enhancement_prompt:
    # ✅ Enhancement mode takes priority over initial generation
    # Append enhancement to the running spec so coder always sees full context
    st.session_state.spec_text += f"\n\nEnhancement request: {enhancement_prompt}"

    subtasks = planner_agent(enhancement_prompt, api_key=api_key)
    frontend_files = st.session_state.frontend_files
    for sub in subtasks:
        updated_files = coder_agent(
            task_text=sub["task"],
            api_key=api_key,
            existing_files=frontend_files,          # existing files = enhancement mode
            spec_text=st.session_state.spec_text    # ✅ always pass full spec
        )
        frontend_files.update(updated_files)
        st.session_state.agent_logs.append(
            f"Enhancement: {sub['task']} ({sub['type']}) | Updated: {list(updated_files.keys())}"
        )

    st.session_state.frontend_files = frontend_files

elif user_prompt:
    # ✅ Fresh generation
    # Store full spec from first user request
    st.session_state.spec_text = user_prompt

    subtasks = planner_agent(user_prompt, api_key=api_key)
    frontend_files = {}
    for sub in subtasks:
        files = coder_agent(
            task_text=sub["task"],
            api_key=api_key,
            existing_files=None,                    # no files yet
            spec_text=st.session_state.spec_text    # ✅ pass full spec
        )
        frontend_files.update(files)
        st.session_state.agent_logs.append(
            f"Planner: {sub['task']} ({sub['type']}) | Coder generated: {list(files.keys())}"
        )

    st.session_state.frontend_files = frontend_files

frontend_files = st.session_state.frontend_files

# -------------------------------
# --- Tabs Content
# -------------------------------
with tabs[0]:
    st.write("### Project Files")
    for fname in frontend_files:
        st.write(f"- {fname}")

with tabs[1]:
    st.write("### Generated Code")
    for fname, content in frontend_files.items():
        lang = "html" if fname.endswith(".html") else "css" if fname.endswith(".css") else "javascript"
        st.write(f"#### {fname}")
        st.code(content, language=lang)

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
        html_content = frontend_files.get("index.html", "")
        css_content = frontend_files.get("style.css", "")
        js_content = frontend_files.get("script.js", "")

        # ✅ Safely inject CSS and JS into HTML without breaking <head>/<body>
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
