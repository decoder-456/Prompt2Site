
from langgraph.types import interrupt

from backend.config import MAX_REPAIRS
from backend.services.website_files import save_preview
from backend.state import AgentState


def human_approval_node(state: AgentState, config):
    """Pause the workflow and wait for human approval or feedback."""

    project_id = str(config["configurable"]["thread_id"])

    # Save the current website so the user can preview it.
    folder = save_preview(state, project_id)

    # Pause graph execution until the API resumes this thread.
    decision = interrupt(
        {
            "message": "Review the generated website.",
            "requirement": state["requirement"],
            "test_report": state.get("test_report", ""),
            "preview_file": str(folder / "index.html"),
            "attempts": state.get("attempts", 0),
            "can_revise": state.get("attempts", 0) < MAX_REPAIRS,
            "passed": state.get("passed", False),
        }
    )

    # Interpret the decision supplied when the graph resumes.
    action = str(decision.get("action", "reject")).lower()

    if action == "approve":
        return {
            "approved": True,
            "human_feedback": "",
        }

    if action == "revise" and state.get("attempts", 0) < MAX_REPAIRS:
        return {
            "approved": False,
            "human_feedback": (
                decision.get("feedback", "") or "Improve the website."
            ),
        }

    # Reject or disallow a revision when the repair limit is reached.
    return {
        "approved": False,
        "human_feedback": decision.get(
            "feedback", "Rejected by user."
        ),
    }
