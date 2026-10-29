
import os
import re
import requests
import streamlit as st

API_URL = os.getenv(
    "WEBSITE_BUILDER_API",
    "http://127.0.0.1:8000",
).rstrip("/")

st.set_page_config(
    page_title="AI Website Builder",
    page_icon="🛠️",
    layout="wide",
)

st.title("🛠️ AI Website Builder")
st.caption(
    "Modular LangGraph agents · Gemini · Browser tests · Self-repair"
)


# =====================================================
# API HELPERS
# =====================================================

def request(method, path, **kwargs):
    timeout = kwargs.pop("timeout", 300)

    try:
        response = requests.request(
            method,
            f"{API_URL}{path}",
            timeout=timeout,
            **kwargs,
        )

        # A missing project is a normal empty state.
        if response.status_code == 404 and method.upper() == "GET":
            return None

        response.raise_for_status()
        return response.json()

    except requests.RequestException as exc:
        st.error(f"Backend request failed: {exc}")
        return None


def project_path(project_id):
    return "/projects/" + requests.utils.quote(
        project_id,
        safe="",
    )


def preview_document(state):
    html = state.get("html") or (
        "<!doctype html><html><head>"
        "<title>Website Preview</title></head>"
        "<body>No preview yet</body></html>"
    )

    css = state.get("css", "")
    js = state.get("javascript", "")

    # Remove existing local stylesheet reference.
    html = re.sub(
        r"""<link\b(?=[^>]*\bhref\s*=\s*['"](?:\./)?style\.css(?:\?[^'"]*)?['"])[^>]*>""",
        "",
        html,
        flags=re.IGNORECASE,
    )

    # Remove existing local JavaScript reference.
    html = re.sub(
        r"""<script\b(?=[^>]*\bsrc\s*=\s*['"](?:\./)?script\.js(?:\?[^'"]*)?['"])[^>]*>\s*</script\s*>""",
        "",
        html,
        flags=re.IGNORECASE,
    )

    style_tag = f"<style>\n{css}\n</style>"
    script_tag = f"<script>\n{js}\n</script>"

    if re.search(r"</head\s*>", html, re.IGNORECASE):
        html = re.sub(
            r"</head\s*>",
            style_tag + "</head>",
            html,
            count=1,
            flags=re.IGNORECASE,
        )
    else:
        html = style_tag + html

    if re.search(r"</body\s*>", html, re.IGNORECASE):
        html = re.sub(
            r"</body\s*>",
            script_tag + "</body>",
            html,
            count=1,
            flags=re.IGNORECASE,
        )
    else:
        html += script_tag

    return html


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.header("Project")

    project_id = st.text_input(
        "Project ID",
        value="my-website",
    ).strip()

    st.markdown("**Agent pipeline**")
    st.write("Planner → Designer → Coder → Tester → Repair")

if not project_id:
    st.warning("Enter a project ID.")
    st.stop()


# =====================================================
# GENERATE WEBSITE
# =====================================================

requirement = st.text_area(
    "Describe your website",
    height=140,
    placeholder=(
        "Build a responsive portfolio with projects, "
        "skills, and a contact form."
    ),
)

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "Generate website",
        type="primary",
        use_container_width=True,
    ):
        if not requirement.strip():
            st.error("Enter a website requirement first.")
        else:
            with st.spinner(
                "Backend agents are working. This may take a while..."
            ):
                result = request(
                    "POST",
                    f"{project_path(project_id)}/start",
                    json={"requirement": requirement.strip()},
                    timeout=600,
                )

            if result:
                st.rerun()

with col2:
    if st.button(
        "Refresh project",
        use_container_width=True,
    ):
        st.rerun()


# =====================================================
# LOAD PROJECT
# =====================================================

project = request(
    "GET",
    project_path(project_id),
    timeout=30,
)

if not project:
    st.info(
        "No saved project found for this ID. "
        "Enter your requirements and click Generate website."
    )
    st.stop()

state = project.get("state", {})
pending = project.get("interrupt")

left, right = st.columns([1.2, 1])


# =====================================================
# LIVE PREVIEW
# =====================================================

with left:
    st.subheader("Website preview")

    if state.get("html"):
        st.components.v1.html(
            preview_document(state),
            height=620,
            scrolling=True,
        )
    else:
        st.info("Preview will appear after generation.")


# =====================================================
# WORKFLOW STATUS
# =====================================================

with right:
    st.subheader("Workflow")

    st.write(
        "**Status:**",
        project.get("status", "unknown"),
    )

    st.metric(
        "Repair cycles",
        state.get("attempts", 0),
    )

    if state.get("passed"):
        st.success("Automated checks passed.")

    if state.get("plan"):
        with st.expander("Planner output"):
            st.write(state["plan"])

    if state.get("design_spec"):
        with st.expander("UI design"):
            st.write(state["design_spec"])

    if state.get("test_report"):
        with st.expander("Test report", expanded=True):
            st.text(state["test_report"])

    if state.get("error_history"):
        with st.expander("Repair history"):
            st.write(state["error_history"])


# =====================================================
# HUMAN APPROVAL
# =====================================================

if pending:
    st.divider()
    st.subheader("Human approval required")

    st.write(
        pending.get(
            "message",
            "Review the website before deciding.",
        )
    )

    st.code(pending.get("preview_file", ""))

    feedback = st.text_area(
        "Feedback for the agents",
        key=f"feedback-{project_id}",
    )

    col_approve, col_revise, col_reject = st.columns(3)

    with col_approve:
        if st.button(
            "Approve and save",
            type="primary",
            use_container_width=True,
        ):
            result = request(
                "POST",
                f"{project_path(project_id)}/resume",
                json={"action": "approve"},
            )

            if result:
                st.success("Website approved.")
                st.rerun()

    with col_revise:
        if st.button(
            "Request changes",
            disabled=not pending.get("can_revise", False),
            use_container_width=True,
        ):
            result = request(
                "POST",
                f"{project_path(project_id)}/resume",
                json={
                    "action": "revise",
                    "feedback": feedback.strip()
                    or "Improve the website based on the test report.",
                },
                timeout=600,
            )

            if result:
                st.rerun()

    with col_reject:
        if st.button(
            "Reject",
            use_container_width=True,
        ):
            result = request(
                "POST",
                f"{project_path(project_id)}/resume",
                json={
                    "action": "reject",
                    "feedback": feedback.strip()
                    or "Rejected by user.",
                },
            )

            if result:
                st.warning("Website rejected.")
                st.rerun()


# =====================================================
# GENERATED SOURCE CODE
# =====================================================

if state.get("html"):
    st.divider()
    st.subheader("Generated source")

    html_tab, css_tab, js_tab = st.tabs(
        ["index.html", "style.css", "script.js"]
    )

    with html_tab:
        st.code(
            state.get("html", ""),
            language="html",
        )

    with css_tab:
        st.code(
            state.get("css", ""),
            language="css",
        )

    with js_tab:
        st.code(
            state.get("javascript", ""),
            language="javascript",
        )


# =====================================================
# FINAL STATUS
# =====================================================

if state.get("approved"):
    st.success(
        f"Approved website saved under "
        f"generated_website/{project_id}/"
    )
