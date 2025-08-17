# agents/planner.py
import os
import json
import re
from langchain_openai import ChatOpenAI

def extract_json(text: str) -> str:
    """Extract the first JSON array from the response text."""
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        return match.group(0)
    return "[]"

def planner_agent(prompt: str, api_key: str) -> list:
    """
    Breaks down user prompt (new or enhancement) into structured subtasks.
    Returns list of dicts: [{task, type}]
    """
    if not prompt.strip():
        return []

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, api_key=api_key)

    planner_prompt = f"""
    You are a **software planning agent**.
    Break the following request into clear subtasks. 
    Classify each subtask as one of: frontend, backend, database.
    
    Rules:
    - Respond ONLY with a JSON array of objects.
    - Do NOT include any text outside JSON.
    - If user asks for enhancement, merge it logically with previous tasks.

    Example:
    [
      {{"task": "Create index.html structure", "type": "frontend"}},
      {{"task": "Style with CSS", "type": "frontend"}},
      {{"task": "Add interactivity in JS", "type": "frontend"}}
    ]

    User request: {prompt}
    """

    reply = llm.invoke(planner_prompt)

    # Extract JSON safely
    raw_text = reply.content.strip()
    json_text = extract_json(raw_text)

    try:
        subtasks = json.loads(json_text)
    except Exception as e:
        print(f"[Planner] JSON parsing failed: {e}\nRaw: {raw_text}")
        subtasks = [{"task": prompt, "type": "frontend"}]

    return subtasks
