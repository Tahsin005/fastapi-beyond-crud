from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from src.reviews.schemas import ReviewCreateModel

from sqlalchemy.ext.asyncio.session import AsyncSession

class ReviewService:
    async def add_review_to_book(self, user_email: str, book_uid: str, review_data: ReviewCreateModel, session: AsyncSession):
        pass