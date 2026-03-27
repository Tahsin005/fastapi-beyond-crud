from fastapi import FastAPI
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db

@asynccontextmanager
async def life_span(app: FastAPI):
    # startup tasks
    print("Starting up the application...")
    await init_db()
    yield
    # shutdown tasks
    print("Shutting down the application...")

version = "v1"

description = """A REST API for a book review web service."""

version_prefix =f"/api/{version}"

app = FastAPI(
    title="Books API",
    description="A simple API for managing books",
    version=version,
    lifespan=life_span
)

app.include_router(book_router, prefix=f"{version_prefix}/books", tags=["books"])