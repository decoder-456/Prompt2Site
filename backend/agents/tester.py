from backend.llm import review_llm
from backend.services.website_files import save_preview
from backend.services.static_checks import static_checks
from backend.services.browser_tests import browser_test
from backend.services.repair_policy import error_signature
from backend.state import AgentState

def test_engine_agent(state: AgentState, config):
    project_id = str(config["configurable"]["thread_id"])
    save_preview(state, project_id)
    static_errors = static_checks(state)
    browser_errors = browser_test(project_id)
    errors = static_errors + browser_errors
    result = review_llm.invoke(f"""You are the Test Engineer Agent. Review the website against the requirement, plan, and design. Do not claim unperformed tests passed.\nREQUIREMENT: {state['requirement']}\nPLAN: {state.get('plan', '')}\nDESIGN: {state.get('design_spec', '')}\nSTATIC ERRORS: {static_errors}\nBROWSER ERRORS: {browser_errors}\nHTML: {state.get('html', '')}\nCSS: {state.get('css', '')}\nJAVASCRIPT: {state.get('javascript', '')}\nSet passed=true only if the supplied checks have no errors and the website appears to meet the requirement. Give specific repair instructions.""")
    passed = not errors and result.passed
    report = "STATIC CHECKS:\n" + ("\n".join(static_errors) if static_errors else "None detected") + "\n\nBROWSER CHECKS:\n" + ("\n".join(browser_errors) if browser_errors else "None detected by current tests") + "\n\nAI REVIEW:\n" + result.review
    signature = error_signature(errors, "AI_REVIEW_FAILED\n" + result.review if not result.passed else "")
    history = list(state.get("error_history", []))
    if signature:
        history.append(signature)
    return {"passed": passed, "test_report": report, "error_signature": signature, "error_history": history}
