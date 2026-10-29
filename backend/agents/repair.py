from backend.llm import website_llm
from backend.state import AgentState

def repair_agent(state: AgentState):
    files = website_llm.invoke(f"""You are the Repair Agent. Fix reported problems while preserving working features. Avoid repeating failed approaches.\nREQUIREMENT: {state['requirement']}\nPLAN: {state.get('plan', '')}\nDESIGN: {state.get('design_spec', '')}\nCURRENT HTML:\n{state.get('html', '')}\nCURRENT CSS:\n{state.get('css', '')}\nCURRENT JAVASCRIPT:\n{state.get('javascript', '')}\nTEST REPORT:\n{state.get('test_report', '')}\nHUMAN FEEDBACK:\n{state.get('human_feedback', '') or 'None'}\nPREVIOUS ERROR SIGNATURES: {state.get('error_history', [])}\nReturn all three complete files without Markdown fences.""")
    return {"html": files.html.strip(), "css": files.css.strip(), "javascript": files.javascript.strip(), "attempts": state.get("attempts", 0) + 1, "passed": False, "approved": False, "human_feedback": ""}
