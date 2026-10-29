from backend.llm import llm
from backend.state import AgentState

def designer_agent(state: AgentState):
    response = llm.invoke(f"""You are the UI/UX Designer Agent. Specify layout, visual hierarchy, color palette, typography, spacing, responsive breakpoints, components, and interaction states. Do not write code.\nREQUIREMENT:\n{state['requirement']}\nPLAN:\n{state.get('plan', '')}""")
    return {"design_spec": str(response.content)}
