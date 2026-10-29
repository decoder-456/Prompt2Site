import sqlite3
import threading
from backend.config import DATABASE_PATH
from langgraph.checkpoint.sqlite import SqliteSaver
from backend.graph.builder import build_graph

DB_PATH = str(DATABASE_PATH)
_connection = sqlite3.connect(DB_PATH, check_same_thread=False)
_checkpointer = SqliteSaver(_connection)
_checkpointer.setup()
graph = build_graph(_checkpointer)
graph_lock = threading.RLock()
