from fastapi import APIRouter
from src.api.dependencies import authorize_and_return_user_id, DBDep


router = APIRouter(prefix="/admin", tags=["Админ панель ⚜️"])


@router.get("/reviews")
async def get_all_reviews(
    db: DBDep,
    user_id: int = authorize_and_return_user_id(3),
):
    return await db.reviews.get_all()