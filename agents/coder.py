# agents/coder.py
import json
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


def coder_agent(
    task_text: str,
    api_key: str = None,
    existing_files: dict = None,
    spec_text: str = None
) -> dict:
    """
    Coder Agent: Generates or enhances frontend code (HTML, CSS, JS).

    Args:
        task_text (str): The coding task or enhancement request.
        api_key (str, optional): OpenAI API key (if not set globally).
        existing_files (dict, optional): Existing frontend files to enhance.
        spec_text (str, optional): Full project requirements/specification.

    Returns:
        dict: Dictionary of file contents with keys:
              - "index.html"
              - "style.css"
              - "script.js"
    """

    # Initialize LLM (low temperature for consistency/reliability)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=api_key)

    # =========================
    # 1. Prepare Prompt
    # =========================
    if existing_files:
        # Enhancement flow
        prompt = f"""
You are enhancing an existing frontend project.

Current files:
{json.dumps(existing_files, indent=2)}

Enhancement request:
{task_text}

Full requirements/specification (must always be respected):
{spec_text}

Rules:
- Implement features so the project matches the FULL specification.
- Return ONLY a valid JSON object with updated file contents.
- Keys must be exactly: "index.html", "style.css", "script.js".
- Ensure index.html references style.css and script.js correctly.
- If charts are needed, use Chart.js via CDN.
- Do not include explanations, markdown formatting, or extra text.
"""
    else:
        # Fresh generation flow
        prompt = f"""
You are a frontend developer. Generate a working, responsive frontend app.

Subtask:
{task_text}

Full requirements/specification (must always be respected):
{spec_text}

Rules:
- Implement ALL relevant parts of the spec (e.g., expense tracker with categories, table, balance, chart, etc.).
- Keep filenames exactly: "index.html", "style.css", "script.js".
- "index.html" must reference "style.css" and "script.js".
- If the spec includes charts, use Chart.js via a CDN.
- Provide visually appealing, responsive styling.
- Avoid generic placeholder apps; tailor to the spec.
- Return ONLY a valid JSON object with keys: index.html, style.css, script.js.
- Do not include explanations, markdown formatting, or extra text.
"""

    # =========================
    # 2. Call the LLM
    # =========================
    response = llm.invoke([HumanMessage(content=prompt)])

    # =========================
    # 3. Parse JSON Response
    # =========================
    try:
        files = json.loads(response.content)
    except Exception as e:
        # Handle JSON parsing errors
        print("Error parsing LLM output:", e)
        print("Raw output:", response.content)

        # Provide safe fallback files
        files = {
            "index.html": "<!DOCTYPE html><html><head></head><body>Error generating HTML</body></html>",
            "style.css": "body { font-family: Arial, sans-serif; background: #f4f4f4; }",
            "script.js": "// Error in generation"
        }

    # =========================
    # 4. Ensure File Integrity
    # =========================
    for fname in ["index.html", "style.css", "script.js"]:
        if fname not in files:
            if fname == "index.html":
                # Ensure index.html has a base structure
                files[fname] = "<!DOCTYPE html><html><head></head><body></body></html>"
            else:
                files[fname] = ""

    return files
