from fastapi import FastAPI
import uvicorn
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.api.auth import router as auth_router
from src.api.authors import router as authors_router
from src.api.books import router as read_router
from src.api.reviews import router as reviews_router
from src.api.admin import router as admin_router

from src.middlewares.middlewares import BanCheckMiddleware

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Lume API",
    description="<h2>Онлайн-библиотека Lume: пользователи, авторы, книги, отзывы, админ панель</h2>",
    version="1.0.0",
)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


app.include_router(auth_router)
app.include_router(authors_router)
app.include_router(read_router)
app.include_router(reviews_router)
app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, etc)
    allow_headers=["*"],  # Разрешить все заголовки
)
app.add_middleware(BanCheckMiddleware)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
