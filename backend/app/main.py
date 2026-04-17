from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .errors import register_error_handlers
from .routers import agents, auth, customers, dashboard, notifications, orders, subscriptions

app = FastAPI(title="auto Flow API", version="1.0.0")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

register_error_handlers(app)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "auto Flow API"}


app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(agents.router)
app.include_router(orders.router)
app.include_router(notifications.router)
app.include_router(subscriptions.router)
app.include_router(dashboard.router)
