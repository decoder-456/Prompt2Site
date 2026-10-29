from backend.config import MAX_REPAIRS
from backend.state import AgentState

def route_after_test(state: AgentState) -> str:
    if state.get("passed"):
        return "approval"
    if state.get("attempts", 0) >= MAX_REPAIRS:
        return "approval"
    history = state.get("error_history", [])
    if len(history) >= 2 and history[-1] == history[-2]:
        return "approval"
    return "repair"

def route_after_approval(state: AgentState) -> str:
    if state.get("approved"):
        return "save"
    if state.get("attempts", 0) < MAX_REPAIRS and state.get("human_feedback"):
        return "repair"
    return "end"
