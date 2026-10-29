from langgraph.types import interrupt
from backend.services.website_files import save_preview
from backend.state import AgentState
from backend.config import MAX_REPAIRS

def human_approval_node(state: AgentState, config):
    project_id = str(config["configurable"]["thread_id"])
    folder = save_preview(state, project_id)
    decision = interrupt({"message": "Review the generated website.", "requirement": state["requirement"], "test_report": state.get("test_report", ""), "preview_file": str(folder / "index.html"), "attempts": state.get("attempts", 0), "can_revise": state.get("attempts", 0) < MAX_REPAIRS, "passed": state.get("passed", False)})
    action = str(decision.get("action", "reject")).lower()
    if action == "approve":
        return {"approved": True, "human_feedback": ""}
    if action == "revise" and state.get("attempts", 0) < MAX_REPAIRS:
        return {"approved": False, "human_feedback": decision.get("feedback", "") or "Improve the website."}
    return {"approved": False, "human_feedback": decision.get("feedback", "Rejected by user.")}
