from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from src.reviews.service import ReviewService
from src.db.main import get_session
from src.auth.dependencies import get_current_user, RoleChecker
from src.db.models import User, Book, Review
from src.reviews.schemas import ReviewCreateModel

review_router = APIRouter()
review_service = ReviewService()

admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["user", "admin"]))

@review_router.post("/book/{book_uid}")
async def add_review_to_book(
    book_uid: str, 
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    new_review = await review_service.add_review_to_book(
        user_email=current_user.email,
        review_data=review_data,
        book_uid=book_uid,
        session=session
    )

    return new_review    

@review_router.get("/{review_uid}", dependencies=[user_role_checker])
async def get_review(review_uid: str, session: AsyncSession = Depends(get_session)):
    book = await review_service.get_review(review_uid, session)

    if not book:
        raise

@review_router.get("/", dependencies=[admin_role_checker])
async def get_all_reviews(session: AsyncSession = Depends(get_session)):
    books = await review_service.get_all_reviews(session)

    return books
