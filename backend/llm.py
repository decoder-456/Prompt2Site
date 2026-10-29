from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import MODEL_NAME
from backend.state import WebsiteFiles, ReviewResult

llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0)
website_llm = llm.with_structured_output(WebsiteFiles)
review_llm = llm.with_structured_output(ReviewResult)
