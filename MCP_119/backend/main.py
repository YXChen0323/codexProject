from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from . import jsonrpc
from .model_router import ModelRouter
from . import prompt_templates
from .context_manager import ConversationContext
from . import sql_generator

app = FastAPI()
router = ModelRouter()
context_manager = ConversationContext()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


class ModelRequest(BaseModel):
    task_type: str | None = None
    user_id: str | None = None


class PromptRequest(BaseModel):
    model: str
    task: str
    query: str


class RecordRequest(BaseModel):
    user_id: str
    query: str
    response: str


class SQLRequest(BaseModel):
    question: str

@app.get("/hello")
async def read_root():
    return {"message": "Hello from FastAPI"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except Exception:
        await websocket.close()


@app.post("/query")
@app.post("/api/query")
async def handle_query(request: QueryRequest):
    """Receive a user query and wrap it in JSON-RPC format."""
    rpc_payload = jsonrpc.build_request(
        method="query",
        params={"query": request.query},
    )
    return rpc_payload


@app.post("/model")
@app.post("/api/model")
async def select_model(request: ModelRequest):
    """Select a model based on user or task information."""
    model_name = router.route(task_type=request.task_type, user_id=request.user_id)
    return {"model": model_name}


@app.post("/prompt")
@app.post("/api/prompt")
async def build_prompt(request: PromptRequest):
    """Return a prompt with the user's query filled in."""
    template = prompt_templates.load_template(request.model, request.task)
    prompt = prompt_templates.fill_template(template, request.query)
    return {"prompt": prompt}


@app.post("/context/record")
@app.post("/api/context/record")
async def record_interaction(request: RecordRequest):
    """Record a user query and response in the conversation context."""
    context_manager.record(request.user_id, request.query, request.response)
    return {"status": "ok"}


@app.get("/context/history")
@app.get("/api/context/history")
async def get_history(user_id: str):
    """Return the message history for a user."""
    messages = context_manager.get_history(user_id)
    return {"history": [m.__dict__ for m in messages]}


@app.get("/context/summary")
@app.get("/api/context/summary")
async def get_summary(user_id: str):
    """Return a summary of the conversation history for a user."""
    summary = context_manager.summarize(user_id)
    return {"summary": summary}


@app.post("/sql")
@app.post("/api/sql")
async def generate_sql(request: SQLRequest):
    """Generate an SQL query (including PostGIS syntax) using an LLM."""
    sql = sql_generator.generate_sql(request.question)
    return {"sql": sql}
