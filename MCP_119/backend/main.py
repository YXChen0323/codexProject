from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from utils import summarize_results
import json
from fastapi.middleware.cors import CORSMiddleware
import jsonrpc
from model_router import ModelRouter
import prompt_templates
from context_manager import ConversationContext
import sql_generator
import answer_generator
import database

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


class RetrieveRequest(BaseModel):
    user_id: str


class ResetRequest(BaseModel):
    user_id: str


class SQLRequest(BaseModel):
    question: str
    model: str | None = None


class SQLExecuteRequest(BaseModel):
    query: str
    user_id: str | None = None
    model: str | None = None
    question: str | None = None

@app.get("/")
async def root():
    """Return a simple greeting for the API root."""
    return {"message": "Welcome"}


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


@app.get("/models")
@app.get("/api/models")
async def list_models():
    """Return the list of available model names."""
    models = router.list_models()
    return {"models": models}


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


@app.post("/context/retrieve")
@app.post("/api/context/retrieve")
async def retrieve_history(request: RetrieveRequest):
    """Retrieve the conversation history for a user."""
    messages = context_manager.get_history(request.user_id)
    return {"history": [m.__dict__ for m in messages]}


@app.post("/context/reset")
@app.post("/api/context/reset")
async def reset_history(request: ResetRequest):
    """Delete all conversation history for a user."""
    context_manager.reset(request.user_id)
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
    try:
        sql = sql_generator.generate_sql(request.question, model=request.model)
    except ValueError as exc:
        return {"error": str(exc)}
    except Exception as exc:  # pragma: no cover - depends on environment
        return {"error": str(exc)}
    return {"sql": sql}


@app.post("/sql/execute")
@app.post("/api/sql/execute")
async def execute_sql(request: SQLExecuteRequest):
    """Execute a SQL query, store the result, and return a JSON-RPC response."""
    try:
        results = database.execute_query(request.query)
    except Exception as exc:  # pragma: no cover - depends on environment
        return jsonrpc.build_response(
            error={"code": -32000, "message": str(exc)}
        )
    if request.user_id:
        context_manager.record(request.user_id, request.query, json.dumps(results))
    summary = summarize_results(results)
    answer = None
    if request.question:
        try:
            answer = answer_generator.generate_answer(
                request.question, results, model=request.model or "llama3.2:3b"
            )
        except Exception:  # pragma: no cover - depends on environment
            answer = ""
    return jsonrpc.build_response(result={
        "results": results,
        "model": request.model,
        "sql": request.query,
        "summary": summary,
        "answer": answer,
    })


@app.get("/roads")
@app.get("/api/roads")
async def get_roads(limit: int = 100):
    """Return road geometries from the tiger schema as GeoJSON."""
    try:
        limit = int(limit)
    except ValueError:
        limit = 100
    if limit < 1:
        limit = 1
    if limit > 1000:
        limit = 1000
    query = (
        "SELECT gid, fullname, ST_AsGeoJSON(geom) AS geom_json "
        "FROM tiger.roads LIMIT %d" % limit
    )
    rows = database.execute_query(query)
    features = []
    for row in rows:
        geom_json = row.pop("geom_json", None)
        if geom_json:
            geometry = json.loads(geom_json)
        else:
            geometry = None
        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": row,
        })
    return {"type": "FeatureCollection", "features": features}
