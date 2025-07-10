from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from utils import summarize_results, results_to_geojson
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


class AskRequest(BaseModel):
    question: str
    model: str | None = None
    user_id: str | None = None


class ChartRequest(BaseModel):
    question: str
    model: str | None = None
    user_id: str | None = None

@app.get("/")
async def root():
    """Return a simple greeting for the API root."""
    return jsonrpc.build_response(result={"message": "Welcome"})


@app.get("/hello")
async def read_root():
    return jsonrpc.build_response(result={"message": "Hello from FastAPI"})

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
    return jsonrpc.build_response(result={"model": model_name})


@app.get("/models")
@app.get("/api/models")
async def list_models():
    """Return the list of available model names."""
    models = router.list_models()
    return jsonrpc.build_response(result={"models": models})


@app.post("/prompt")
@app.post("/api/prompt")
async def build_prompt(request: PromptRequest):
    """Return a prompt with the user's query filled in."""
    template = prompt_templates.load_template(request.model, request.task)
    prompt = prompt_templates.fill_template(template, request.query)
    return jsonrpc.build_response(result={"prompt": prompt})


@app.post("/context/record")
@app.post("/api/context/record")
async def record_interaction(request: RecordRequest):
    """Record a user query and response in the conversation context."""
    context_manager.record(request.user_id, request.query, request.response)
    return jsonrpc.build_response(result={"status": "ok"})


@app.post("/context/retrieve")
@app.post("/api/context/retrieve")
async def retrieve_history(request: RetrieveRequest):
    """Retrieve the conversation history for a user."""
    messages = context_manager.get_history(request.user_id)
    return jsonrpc.build_response(result={"history": [m.__dict__ for m in messages]})


@app.post("/context/reset")
@app.post("/api/context/reset")
async def reset_history(request: ResetRequest):
    """Delete all conversation history for a user."""
    context_manager.reset(request.user_id)
    return jsonrpc.build_response(result={"status": "ok"})


@app.get("/context/history")
@app.get("/api/context/history")
async def get_history(user_id: str):
    """Return the message history for a user."""
    messages = context_manager.get_history(user_id)
    return jsonrpc.build_response(result={"history": [m.__dict__ for m in messages]})


@app.get("/context/summary")
@app.get("/api/context/summary")
async def get_summary(user_id: str):
    """Return a summary of the conversation history for a user."""
    summary = context_manager.summarize(user_id)
    return jsonrpc.build_response(result={"summary": summary})


@app.post("/sql")
@app.post("/api/sql")
async def generate_sql(request: SQLRequest):
    """Generate an SQL query (including PostGIS syntax) using an LLM."""
    try:
        sql = sql_generator.generate_sql(request.question, model=request.model)
    except ValueError as exc:
        return jsonrpc.build_response(
            error={"code": -32000, "message": str(exc)}
        )
    except Exception as exc:  # pragma: no cover - depends on environment
        return jsonrpc.build_response(
            error={"code": -32000, "message": str(exc)}
        )
    return jsonrpc.build_response(result={"sql": sql})


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
    geojson = results_to_geojson(results)
    answer = ""
    if request.question:
        # Run the NLP template to turn the raw results into a friendly
        # natural language answer for the frontend.  The prompt template
        # is loaded inside ``generate_answer`` using the "nlp" task name.
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
        "geojson": geojson,
    })


@app.post("/ask")
@app.post("/api/ask")
async def ask(request: AskRequest):
    """Generate SQL from a question, execute it, and return the results."""
    try:
        sql = sql_generator.generate_sql(request.question, model=request.model)
    except ValueError as exc:
        return jsonrpc.build_response(
            error={"code": -32000, "message": str(exc)}
        )
    except Exception as exc:  # pragma: no cover - depends on environment
        return jsonrpc.build_response(
            error={"code": -32000, "message": str(exc)}
        )

    try:
        results = database.execute_query(sql)
    except Exception as exc:  # pragma: no cover - depends on environment
        return jsonrpc.build_response(
            error={"code": -32000, "message": str(exc)}
        )

    if request.user_id:
        context_manager.record(request.user_id, sql, json.dumps(results))

    summary = summarize_results(results)
    geojson = results_to_geojson(results)
    answer = ""
    try:
        answer = answer_generator.generate_answer(
            request.question,
            results,
            model=request.model or "llama3.2:3b",
        )
    except Exception:  # pragma: no cover - depends on environment
        answer = ""

    return jsonrpc.build_response(result={
        "results": results,
        "model": request.model,
        "sql": sql,
        "summary": summary,
        "answer": answer,
        "geojson": geojson,
    })


@app.post("/chart")
@app.post("/api/chart")
async def chart(request: ChartRequest):
    """Generate comparative chart data using two LLM SQL passes."""
    try:
        base_sql = sql_generator.generate_sql(request.question, model=request.model)
        chart_sql = sql_generator.generate_chart_sql(request.question, model=request.model)
    except ValueError as exc:
        return jsonrpc.build_response(
            error={"code": -32000, "message": str(exc)}
        )
    except Exception as exc:  # pragma: no cover - depends on environment
        return jsonrpc.build_response(
            error={"code": -32000, "message": str(exc)}
        )

    try:
        results = database.execute_query(chart_sql)
    except Exception as exc:  # pragma: no cover - depends on environment
        return jsonrpc.build_response(
            error={"code": -32000, "message": str(exc)}
        )

    if request.user_id:
        context_manager.record(request.user_id, chart_sql, json.dumps(results))

    summary = summarize_results(results)

    geojson = results_to_geojson(results)
    answer = ""
    try:
        answer = answer_generator.generate_answer(
            request.question,
            results,
            model=request.model or "llama3.2:3b",
        )
    except Exception:  # pragma: no cover - depends on environment
        answer = ""

    return jsonrpc.build_response(result={
        "results": results,
        "model": request.model,
        "sql": chart_sql,
        "base_sql": base_sql,
        "summary": summary,
        "answer": answer,
        "geojson": geojson,
    })
