from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from . import jsonrpc
from .model_router import ModelRouter
from . import prompt_templates

app = FastAPI()
router = ModelRouter()

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
