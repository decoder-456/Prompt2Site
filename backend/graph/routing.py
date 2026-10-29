from backend.config import MAX_REPAIRS
from backend.state import AgentState


def route_after_test(state: AgentState) -> str:
    """Choose whether to approve the tested website or repair it."""
    # If testing passes, send the website for human approval.
    if state.get("passed"):
        return "approval"

    # Stop automatic repair when the limit is reached.
    if state.get("attempts", 0) >= MAX_REPAIRS:
        return "approval"

    # Avoid repeatedly repairing the same error.
    history = state.get("error_history", [])

    if len(history) >= 2 and history[-1] == history[-2]:
        return "approval"

    # Otherwise, try to repair the website.
    return "repair"


def route_after_approval(state: AgentState) -> str:
    """Choose the next step based on the user's decision."""

    # Save the website if the user approved it.
    if state.get("approved"):
        return "save"

    # If the user requested changes, attempt a revision.
    if (
        state.get("attempts", 0) < MAX_REPAIRS
        and state.get("human_feedback")
    ):
        return "repair"

    # Otherwise, finish the workflow without saving.
    return "end"
