from backend.llm import website_llm
from backend.state import AgentState

def coder_agent(state: AgentState):
    files = website_llm.invoke(f"""Build a complete static website using vanilla HTML, CSS, and JavaScript.\nREQUIREMENT:\n{state['requirement']}\nPLAN:\n{state['plan']}\nDESIGN:\n{state['design_spec']}\nReturn complete index.html, style.css, and script.js. Make requested interactions functional and accessible. Use responsive design and matching selectors. Include a page title, viewport meta tag, stylesheet link, and deferred script link. Avoid eval() and document.write(). Return source code without Markdown fences.""")
    return {"html": files.html.strip(), "css": files.css.strip(), "javascript": files.javascript.strip(), "attempts": 0, "passed": False, "approved": False, "human_feedback": "", "test_report": "", "error_signature": "", "error_history": []}
