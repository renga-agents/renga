---
applyTo: "**/*.py,**/pyproject.toml"
---

# Python Conventions — FastAPI, Pydantic, LangChain, LangGraph

> Philosophy: **typed, async, minimal**. Type everything, use async when relevant, keep functions short and composable.
>
> **Prerequisites**: Python >= 3.12, uv (dependency manager), Ruff (linter + formatter)

---

## Python 3.12+

### Modern type hints — required

```python

# ✅ Modern syntax (3.10+ / 3.12+)
def process(items: list[str], config: dict[str, int] | None = None) -> tuple[bool, str]:
    ...

# ❌ Old style — FORBIDDEN
from typing import List, Dict, Optional, Tuple
def process(items: List[str], config: Optional[Dict[str, int]] = None) -> Tuple[bool, str]:
    ...

```

| Modern (3.10+) | Old (forbidden) |
| --- | --- |
| `str | None` | `Optional[str]` |
| `list[str]` | `List[str]` |
| `dict[str, int]` | `Dict[str, int]` |
| `tuple[int, ...]` | `Tuple[int, ...]` |
| `type[MyClass]` | `Type[MyClass]` |

### Remaining allowed typing imports

```python

from typing import (
    Annotated,     # Pydantic validators, FastAPI Depends
    Any,           # when unavoidable (LangChain callbacks, raw data)
    ClassVar,      # Pydantic class variables
    Literal,       # LangGraph Command return types
    TypeVar,       # Pydantic generics
    Generic,       # generic models
    TypeAlias,     # type aliases
    Protocol,      # structural subtyping
    TypeGuard,     # type narrowing
    Self,          # Pydantic model_validator return type
)
from typing_extensions import TypedDict  # LangGraph state
from collections.abc import AsyncIterator, Sequence  # prefer collections.abc over typing

```

### General conventions

- Guard clauses at the start of functions (early return)
- Pure functions when possible — no implicit side effects
- No mutable global variables
- No `print()` — use `logging` or `structlog`
- Constants in `UPPER_SNAKE_CASE`, variables/functions in `snake_case`, classes in `PascalCase`
- Google-style docstrings on all public functions
- Explicit `__all__` in each public module

### Async patterns

```python

# ✅ native async/await for I/O
async def fetch_data(client: httpx.AsyncClient, url: str) -> dict:
    response = await client.get(url)
    response.raise_for_status()
    return response.json()

# ✅ async context manager
async with httpx.AsyncClient() as client:
    data = await fetch_data(client, url)

# ✅ async iteration
async for chunk in response.aiter_bytes():
    process_chunk(chunk)

# ✅ Parallel gathering
results = await asyncio.gather(fetch_a(), fetch_b(), fetch_c())

# ✅ def for CPU-bound work or pure logic
def transform_data(raw: dict[str, Any]) -> ProcessedData:
    ...

```

---

## Tooling

### uv — dependency manager

```bash

uv init               # initialize a project
uv add fastapi        # add a dependency
uv add --dev pytest   # dev dependency
uv sync               # install dependencies
uv run python app.py  # run with the environment
uv lock               # lock dependencies

```

- `uv` is the **default** manager — no poetry, no direct pip
- `pyproject.toml` as the single source of truth (no `requirements.txt`)
- `uv.lock` committed to Git

### Ruff — linter + formatter

```toml

# pyproject.toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = [
    "E", "W",    # pycodestyle
    "F",          # pyflakes
    "I",          # isort
    "N",          # pep8-naming
    "UP",         # pyupgrade
    "B",          # flake8-bugbear
    "SIM",        # flake8-simplify
    "C4",         # flake8-comprehensions
    "TCH",        # flake8-type-checking
    "RUF",        # ruff-specific
    "ASYNC",      # flake8-async
    "S",          # flake8-bandit (security)
]
ignore = ["E501"]  # handled by the formatter

[tool.ruff.lint.isort]
known-first-party = ["app", "src"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

```

- Ruff replaces Black, isort, flake8, pyflakes, etc.
- `ruff check --fix` + `ruff format` as the only lint/format commands

---

## Pydantic 2.x

> **Pydantic v2 only** — all v1 syntax is forbidden.

### v2 API — required

| Action | v2 (required) | v1 (forbidden) |
| --- | --- | --- |
| Serialize to dict | `.model_dump()` | ~~`.dict()`~~ |
| Serialize to JSON | `.model_dump_json()` | ~~`.json()`~~ |
| Validate from dict | `Model.model_validate(data)` | ~~`Model.parse_obj(data)`~~ |
| Validate from JSON | `Model.model_validate_json(json_str)` | ~~`Model.parse_raw(json_str)`~~ |
| Copy a model | `model.model_copy(update={...})` | ~~`.copy(update={...})`~~ |
| JSON Schema | `Model.model_json_schema()` | ~~`.schema()`~~ |
| Rebuild schema | `Model.model_rebuild()` | ~~`update_forward_refs()`~~ |

### BaseModel — standard pattern

```python

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Self

class ProductCreate(BaseModel):
    model_config = ConfigDict(
        strict=True,              # no implicit coercion
        frozen=True,              # immutable, replaces allow_mutation=False
        extra="forbid",         # reject unknown fields
        str_strip_whitespace=True,
        from_attributes=True,     # supports model_validate() from ORM objects
    )

    name: str = Field(min_length=1, max_length=200)
    price: float = Field(gt=0)
    category: str
    tags: list[str] = Field(default_factory=list)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = {"electronics", "clothing", "food"}
        if v not in allowed:
            raise ValueError(f"Category must be one of {allowed}")
        return v

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.price > 10000 and "premium" not in self.tags:
            raise ValueError("Expensive products must have 'premium' tag")
        return self

```

### When to use what

| Structure | Usage |
| --- | --- |
| `BaseModel` | Input/output validation, serialization, APIs, DTOs |
| `TypedDict` | LangGraph state, lightweight dicts without validation |
| `dataclass` | Simple internal objects without validation or serialization |
| `NamedTuple` | Immutable named tuples, positional destructuring |

### Generics and RootModel

```python

from pydantic import BaseModel, RootModel
from typing import Generic, TypeVar

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    data: T
    meta: dict[str, Any] = Field(default_factory=dict)

# Usage: ApiResponse[list[User]], ApiResponse[Product]

class Tags(RootModel[list[str]]):
    pass

```

### Private attributes and class variables

```python

from datetime import datetime
from typing import ClassVar
from pydantic import BaseModel, PrivateAttr

class Document(BaseModel):
    MAX_SIZE: ClassVar[int] = 10_000       # class variable, not a field
    content: str
    _created_at: datetime = PrivateAttr(default_factory=datetime.now)  # private, not serialized

```

---

## FastAPI

### Lifespan — startup/shutdown

```python

from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize resources
    app.state.db_pool = await create_pool()
    app.state.http_client = httpx.AsyncClient()
    yield
    # Shutdown: release resources
    await app.state.db_pool.close()
    await app.state.http_client.aclose()

app = FastAPI(title="My Service", version="1.0.0", lifespan=lifespan)

```

> `@app.on_event("startup")` / `@app.on_event("shutdown")` are **deprecated** — use `lifespan`.

### Routers & Dependency Injection

```python

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/v1/products", tags=["products"])

# ✅ Annotated pattern — reusable and readable
ProductServiceDep = Annotated[ProductService, Depends(ProductService)]
CurrentUser = Annotated[User, Depends(get_current_user)]

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(body: ProductCreate, service: ProductServiceDep) -> ProductResponse:
    return await service.create(body)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, service: ProductServiceDep) -> ProductResponse:
    product = await service.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

# Mount in the main app
app.include_router(router)

```

### Error handling

```python

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

class AppError(Exception):
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )

```

### SSE streaming

```python

from fastapi.responses import StreamingResponse

@router.post("/chat/stream")
async def chat_stream(body: ChatRequest) -> StreamingResponse:
    async def event_generator():
        async for chunk in agent.astream(body.messages):
            yield f"data: {chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

```

### CORS middleware

```python

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

```

---

## LangChain

### Package architecture

```text

langchain-core          # Core abstractions, required
langchain               # Chains, agents, higher-level orchestration
langchain-openai        # ChatOpenAI, OpenAI embeddings
langchain-anthropic     # ChatAnthropic
langchain-google-genai  # ChatGoogleGenerativeAI
langchain-community     # Community integrations
langgraph               # Stateful agent graphs

```

- Always import from the **most specific package**
- `langchain-core` is the only required dependency for abstractions

### Chat Models — instantiation

```python

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

model = ChatOpenAI(model="gpt-4.1", temperature=0, max_tokens=4096, timeout=30, max_retries=2)
model = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)

```

### Prompts

```python

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}. Respond in {language}."),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])

# LCEL: pipe operator
chain = prompt | model
result = await chain.ainvoke({"role": "assistant", "language": "English", "history": [], "input": "Hello"})

```

### Structured Output — `.with_structured_output()`

```python

from pydantic import BaseModel

class ProductAnalysis(BaseModel):
    sentiment: str
    confidence: float
    key_features: list[str]

structured_model = model.with_structured_output(ProductAnalysis)
result: ProductAnalysis = await structured_model.ainvoke("Analyze this product review: ...")

```

- Prefer `.with_structured_output()` over `PydanticOutputParser`
- Works with OpenAI, Anthropic, and Google through each provider's native tool/function calling

### Tools — `@tool` decorator

```python

from langchain_core.tools import tool

@tool
async def search_products(query: str, category: str | None = None) -> list[dict]:
    """Search products in the catalog.

    Args:
        query: Search query string
        category: Optional category filter
    """
    # The docstring is used as the LLM-facing tool description
    results = await db.search(query, category=category)
    return [r.model_dump() for r in results]

# Bind tools to the model
model_with_tools = model.bind_tools([search_products])

```

### Output Parsers

```python

from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

# String output
chain = prompt | model | StrOutputParser()

# JSON output
chain = prompt | model | JsonOutputParser(pydantic_object=MySchema)

```

### Streaming

```python

# Token streaming
async for chunk in chain.astream({"input": "Hello"}):
    print(chunk, end="", flush=True)

# Event streaming — more granular
async for event in chain.astream_events({"input": "Hello"}, version="v2"):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="")

```

### Messages

```python

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

# ✅ Message objects
HumanMessage(content="Hello")
AIMessage(content="Hi!", tool_calls=[...])
SystemMessage(content="You are helpful.")
ToolMessage(content="Result", tool_call_id="call_123")

```

### LangChain anti-patterns

| Forbidden | Why | Alternative |
| --- | --- | --- |
| `ConversationBufferMemory` | Deprecated, legacy | LangGraph state + `add_messages` |
| `LLMChain` | Deprecated | LCEL: `prompt | model | parser` |
| `AgentExecutor` | Replaced by LangGraph | `create_react_agent()` or custom `StateGraph` |
| `from langchain.chat_models import X` | Monolithic package | `from langchain_openai import X` |
| `invoke()` sync in async code | Blocks the event loop | `ainvoke()`, `astream()` |

---

## LangGraph

### Core concepts

LangGraph models agents as **state graphs**:

- **State**: `TypedDict` with reducers for updates
- **Nodes**: functions that transform the state
- **Edges**: transitions between nodes
- **Checkpointer**: state persistence for multi-turn conversations

### State — TypedDict with reducers

```python

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import add_messages
import operator

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    context: Annotated[list[str], operator.add]
    query: str
    iteration_count: int

```

| Reducer | Behavior |
| --- | --- |
| `add_messages` | Adds messages, handles IDs and deduplication |
| `operator.add` | Concatenates lists |
| None | Overwrites the previous value |

### Multiple schemas

```python

class InputState(TypedDict):
    user_input: str

class OutputState(TypedDict):
    result: str

class OverallState(TypedDict):
    user_input: str
    result: str
    internal_data: str

builder = StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)

```

### StateGraph — graph construction

```python

from langgraph.graph import StateGraph, START, END

builder = StateGraph(AgentState)

async def analyze(state: AgentState) -> dict:
    """Each node returns a partial dict update; only returned keys are modified."""
    response = await model.ainvoke(state["messages"])
    return {"messages": [response]}

async def search(state: AgentState) -> dict:
    results = await search_tool.ainvoke(state["query"])
    return {"context": [results], "iteration_count": state["iteration_count"] + 1}

def should_continue(state: AgentState) -> str:
    """Conditional routing — return the next node name."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Graph construction
builder.add_node("analyze", analyze)
builder.add_node("search", search)
builder.add_node("tools", ToolNode(tools=[search_products]))

builder.add_edge(START, "analyze")
builder.add_conditional_edges("analyze", should_continue, {"tools": "tools", END: END})
builder.add_edge("tools", "analyze")

# Compile with checkpointer
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
agent = builder.compile(checkpointer=checkpointer)

```

### Invocation with thread

```python

config = {"configurable": {"thread_id": "user-123-conv-1"}}

# Each invocation with the same thread_id resumes the conversation
result = await agent.ainvoke(
    {"messages": [HumanMessage(content="Hello")]},
    config=config,
)

```

### Conditional Edges — routing

```python

from typing import Literal

def route_by_intent(state: AgentState) -> Literal["search", "answer", "__end__"]:
    """Routing function — return the next node name."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "search"
    return "__end__"

builder.add_conditional_edges("llm_node", route_by_intent)

```

### Command — combine update + routing

```python

from langgraph.types import Command

def review_node(state: AgentState) -> Command[Literal["approve", "reject"]]:
    if state["score"] > 0.8:
        return Command(update={"status": "approved"}, goto="approve")
    return Command(update={"status": "rejected"}, goto="reject")

```

> Return type annotation is **mandatory**: `Command[Literal["node_a", "node_b"]]`

### Human-in-the-loop — `interrupt()`

```python

from langgraph.types import interrupt, Command

def human_review(state: AgentState) -> dict:
    # Pause the graph and wait for human input
    answer = interrupt("Do you approve this action?")
    return {"messages": [HumanMessage(content=answer)]}

# First call — pauses at interrupt()
config = {"configurable": {"thread_id": "thread-1"}}
result = await agent.ainvoke({"messages": [HumanMessage(content="Do X")]}, config)

# Resume — interrupt() returns the provided value
result = await agent.ainvoke(Command(resume="yes"), config)

```

### Send — Map-Reduce pattern

```python

from langgraph.types import Send

def fan_out(state: AgentState) -> list[Send]:
    """Create one node invocation per task — dynamic number of edges."""
    return [Send("worker", {"task": t}) for t in state["tasks"]]

builder.add_conditional_edges("planner", fan_out)

```

### Subgraphs — composition

```python

# A subgraph is a compiled graph used as a node
research_graph = build_research_graph().compile()
writing_graph = build_writing_graph().compile()

parent = StateGraph(ParentState)
parent.add_node("research", research_graph)    # subgraph used as a node
parent.add_node("writing", writing_graph)
parent.add_edge(START, "research")
parent.add_edge("research", "writing")
parent.add_edge("writing", END)

```

### Streaming

```python

# "values" mode — full state at each step
async for state in agent.astream(inputs, config=config, stream_mode="values"):
    print(state["messages"][-1])

# "updates" mode — only per-node changes
async for update in agent.astream(inputs, config=config, stream_mode="updates"):
    node_name, changes = next(iter(update.items()))
    print(f"{node_name}: {changes}")

# "messages" mode — real-time chat tokens
async for msg, metadata in agent.astream(inputs, config=config, stream_mode="messages"):
    if isinstance(msg, AIMessageChunk):
        print(msg.content, end="")

```

### Checkpointers — persistence

| Checkpointer | Usage |
| --- | --- |
| `MemorySaver` | Dev/test only — in memory, no persistence |
| `SqliteSaver` | Local dev — file-based persistence |
| `PostgresSaver` | Production — durable, multi-instance persistence |

```python

# Production
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
    await checkpointer.setup()  # create the tables
    agent = builder.compile(checkpointer=checkpointer)

```

### Prebuilt Agents — `create_react_agent()`

```python

from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=ChatOpenAI(model="gpt-4.1"),
    tools=[search_products, get_product_details],
    checkpointer=checkpointer,
    prompt="You are a helpful product assistant.",
)

result = await agent.ainvoke(
    {"messages": [HumanMessage(content="Find blue shoes")]},
    config={"configurable": {"thread_id": "conv-1"}},
)

```

### RemainingSteps — protection against infinite loops

```python

from langgraph.types import RemainingSteps

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    remaining_steps: RemainingSteps

async def check_steps(state: AgentState) -> dict:
    if state["remaining_steps"] < 2:
        return {"messages": [AIMessage(content="Reaching step limit, summarizing...")]}
    # ...

```

### Node Caching

```python

from langgraph.cache.memory import InMemoryCache
from langgraph.types import CachePolicy

builder.add_node("expensive_node", expensive_fn, cache_policy=CachePolicy(ttl=60))
agent = builder.compile(cache=InMemoryCache())

```

---

## Global anti-patterns

| Forbidden | Correct |
| --- | --- |
| `from typing import List, Dict, Optional` | `list[str]`, `dict[str, int]`, `str | None` |
| `print()` for debugging | `logging.getLogger(__name__)` or `structlog` |
| `pip install` / `requirements.txt` | `uv add` / `pyproject.toml` |
| `@app.on_event("startup")` | `lifespan` context manager |
| `.dict()`, `.json()`, `.parse_obj()` | `.model_dump()`, `.model_dump_json()`, `.model_validate()` |
| `class Config:` in Pydantic | `model_config = ConfigDict(...)` |
| `ConversationBufferMemory` | LangGraph state + checkpointer |
| `AgentExecutor` | LangGraph `StateGraph` or `create_react_agent()` |
| `LLMChain`, `SequentialChain` | LCEL: `prompt | model | parser` |
| `invoke()` sync in async code | `ainvoke()`, `astream()` |
| `from langchain.xxx import YYY` | `from langchain_openai import YYY` |
| `time.sleep()` | `asyncio.sleep()` |
| `requests` | `httpx.AsyncClient` |
| `def f(x=[])` | `def f(x: list | None = None)` |
| `except Exception: pass` | `except SpecificError as e: logger.error(...)` |
| LangGraph state without reducers for lists | `Annotated[list, add_messages]` |

---

## Recommended file structure

```text

src/
  app/
    __init__.py
        main.py
        config.py
        dependencies.py
    routers/
      __init__.py
            products.py
            chat.py
    schemas/
      __init__.py
            product.py
            chat.py
    services/
      __init__.py
            product_service.py
    models/
      __init__.py
            product.py
    agents/
      assistant/
                graph.py
                state.py
                nodes.py
                tools.py
                prompts.py
      research/
        graph.py
        state.py
        nodes.py
tests/
    conftest.py
  test_product_service.py
  test_assistant_graph.py
pyproject.toml
uv.lock

```
