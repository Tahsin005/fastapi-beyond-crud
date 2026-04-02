from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from src.reviews.schemas import ReviewCreateModel
from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio.session import AsyncSession

book_service = BookService()
user_service = UserService()

class ReviewService:
    async def add_review_to_book(self, user_email: str, book_uid: str, review_data: ReviewCreateModel, session: AsyncSession):
        try:
            book = await book_service.get_book(book_uid=book_uid, session=session)

            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )

            user = await user_service.get_user_by_email(email=user_email, session=session)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            review_data_dict = review_data.model_dump()

            new_review = Review(
                **review_data_dict,
            )

            new_review.user = user
            new_review.book = book

            session.add(new_review)
            await session.commit()
            await session.refresh(new_review)

            return new_review
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )