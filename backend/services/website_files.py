import re
from pathlib import Path
from backend.config import PREVIEW_ROOT, OUTPUT_ROOT
from backend.state import AgentState

def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", value).strip("_") or "website"

def save_preview(state: AgentState, project_id: str) -> Path:
    folder = (PREVIEW_ROOT / safe_id(project_id)).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    for name, content in {
        "index.html": state.get("html", ""),
        "style.css": state.get("css", ""),
        "script.js": state.get("javascript", ""),
    }.items():
        (folder / name).write_text(content, encoding="utf-8")
    return folder

def save_final(state: AgentState, project_id: str) -> Path:
    folder = OUTPUT_ROOT / safe_id(project_id)
    folder.mkdir(parents=True, exist_ok=True)
    files = {
        "index.html": state.get("html", ""),
        "style.css": state.get("css", ""),
        "script.js": state.get("javascript", ""),
        "development_plan.txt": state.get("plan", ""),
        "design_spec.txt": state.get("design_spec", ""),
        "test_report.txt": state.get("test_report", ""),
    }
    for name, content in files.items():
        (folder / name).write_text(content, encoding="utf-8")
    return folder
