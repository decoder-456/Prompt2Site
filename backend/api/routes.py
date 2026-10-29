from fastapi import APIRouter, HTTPException
from langgraph.types import Command
from backend.state import StartRequest, ResumeRequest
from backend.services.website_files import safe_id
from backend.graph.runtime import graph, graph_lock

router = APIRouter()

def config_for(project_id: str):
    return {"configurable": {"thread_id": safe_id(project_id)}}

def project_data(project_id: str):
    config = config_for(project_id)
    snapshot = graph.get_state(config)
    state = dict(snapshot.values) if snapshot.values else {}
    pending = None
    for task in snapshot.tasks:
        for item in task.interrupts:
            pending = item.value
            break
        if pending is not None:
            break
    if not state:
        raise HTTPException(404, "Project not found.")
    status = "awaiting_approval" if pending else "approved" if state.get("approved") else "completed" if not snapshot.next else "running"
    keys = ["requirement", "plan", "design_spec", "html", "css", "javascript", "test_report", "passed", "attempts", "approved", "human_feedback", "error_history"]
    return {"project_id": safe_id(project_id), "status": status, "state": {k: state.get(k) for k in keys}, "interrupt": pending}

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/projects/{project_id}/start")
def start_project(project_id: str, body: StartRequest):
    if not body.requirement.strip():
        raise HTTPException(400, "Requirement cannot be empty.")
    initial = {"requirement": body.requirement.strip(), "plan": "", "design_spec": "", "html": "", "css": "", "javascript": "", "test_report": "", "passed": False, "attempts": 0, "approved": False, "human_feedback": "", "error_signature": "", "error_history": []}
    try:
        with graph_lock:
            graph.invoke(initial, config_for(project_id))
        return project_data(project_id)
    except Exception as exc:
        raise HTTPException(500, str(exc))

@router.get("/projects/{project_id}")
def get_project(project_id: str):
    return project_data(project_id)

@router.post("/projects/{project_id}/resume")
def resume_project(project_id: str, body: ResumeRequest):
    action = body.action.lower().strip()
    if action not in {"approve", "revise", "reject"}:
        raise HTTPException(400, "action must be approve, revise, or reject")
    config = config_for(project_id)
    snapshot = graph.get_state(config)
    state = dict(snapshot.values) if snapshot.values else {}
    if not state:
        raise HTTPException(404, "Project not found")
    pending = [item.value for task in snapshot.tasks for item in task.interrupts]
    if not pending:
        raise HTTPException(409, "Project is not waiting for approval")
    if action == "revise" and not pending[0].get("can_revise", False):
        raise HTTPException(400, "Repair limit reached; revision unavailable")
    try:
        with graph_lock:
            graph.invoke(Command(resume={"action": action, "feedback": body.feedback}), config)
        return project_data(project_id)
    except Exception as exc:
        raise HTTPException(500, str(exc))

@router.get("/projects/{project_id}/preview")
def get_preview(project_id: str):
    state = project_data(project_id)["state"]
    if not state.get("html"):
        raise HTTPException(404, "No preview available")
    return {"html": state["html"], "css": state["css"], "javascript": state["javascript"]}
