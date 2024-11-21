from fastapi import FastAPI, HTTPException, status
from src.books.routes import book_router
from src.auth.routes import user_router
from src.tags.routes import tag_router
from src.reviews.routes import reviews_router
from .config import settings
from contextlib import asynccontextmanager
from src.db.main import init_db
from .middleware import register_middleware

# from dotenv import load_dotenv

# load_dotenv()


version = settings.VERSION
ROOT_ROUTE = settings.ROOT_ROUTE


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Server has Started Running...")
    try:
        await init_db()
    except:
        print("Database Connection Failed")
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Database Connection Failed",
        )
    yield
    print("Server Stopped Running!")


app = FastAPI(
    title="Bookly", description="A REST app of Books Library", version=version
)

# Register Middleware

register_middleware(app)


# Add Routers

app.include_router(book_router, prefix=f"/{ROOT_ROUTE}/{version}", tags=["books"])
app.include_router(user_router, prefix=f"/{ROOT_ROUTE}/{version}/auth", tags=["auth"])
app.include_router(
    reviews_router, prefix=f"/{ROOT_ROUTE}/{version}/reviews", tags=["reviews"]
)
app.include_router(tag_router, prefix=f"/{ROOT_ROUTE}/{version}/tags", tags=["tags"])
