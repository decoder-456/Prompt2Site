from backend.llm import llm
from backend.state import AgentState

def planner_agent(state: AgentState):
    response = llm.invoke(f"""You are the Planner Agent. Create an implementation plan and explicit acceptance criteria. Include sections, features, interactions, accessibility, and responsive behavior.\nUSER REQUIREMENT:\n{state['requirement']}""")
    return {"plan": str(response.content)}
