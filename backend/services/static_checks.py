import re
from html.parser import HTMLParser
from pathlib import Path
from backend.state import AgentState

class HTMLInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.classes, self.stylesheets, self.scripts = set(), set(), [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if attrs.get("class"):
            self.classes.update(attrs["class"].split())
        if tag == "link" and "stylesheet" in attrs.get("rel", "").lower().split():
            self.stylesheets.append(attrs.get("href", ""))
        if tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])

def static_checks(state: AgentState) -> list[str]:
    errors = []
    html, css, js = state.get("html", ""), state.get("css", ""), state.get("javascript", "")
    if not html.strip():
        return ["HTML file is empty."]
    if not css.strip(): errors.append("CSS file is empty.")
    if not js.strip(): errors.append("JavaScript file is empty.")
    parser = HTMLInspector()
    try:
        parser.feed(html)
        parser.close()
    except Exception as exc:
        errors.append(f"HTML parser error: {exc}")
        return errors
    if not any(Path(x.split("?")[0]).name == "style.css" for x in parser.stylesheets):
        errors.append("HTML does not link to style.css.")
    if not any(Path(x.split("?")[0]).name == "script.js" for x in parser.scripts):
        errors.append("HTML does not load script.js.")
    for element_id in re.findall(r'''getElementById\(\s*['"]([^'"]+)['"]\s*\)''', js):
        if element_id not in parser.ids:
            errors.append(f"JavaScript references missing ID: #{element_id}")
    for selector in re.findall(r'''querySelector(?:All)?\(\s*['"]([.#][\w-]+)['"]\s*\)''', js):
        if selector.startswith("#") and selector[1:] not in parser.ids:
            errors.append(f"JavaScript references missing selector: {selector}")
        if selector.startswith(".") and selector[1:] not in parser.classes:
            errors.append(f"JavaScript references missing selector: {selector}")
    return list(dict.fromkeys(errors))
