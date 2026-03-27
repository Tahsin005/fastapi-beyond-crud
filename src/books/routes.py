from fastapi import APIRouter, status, Depends
from fastapi import HTTPException
from typing import List

from src.books.schemas import BookModel, BookCreateModel, BookUpdateModel
from src.books.service import BookService
from src.db.main import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
import uuid

book_router = APIRouter()
book_service = BookService()

@book_router.get('/', response_model=List[BookModel])
async def get_books(session: AsyncSession = Depends(get_session)):
    books = await book_service.get_all_books(session=session)
    return books


@book_router.get('/{book_uid}', response_model=BookModel)
async def get_book(book_uid: uuid.UUID, session: AsyncSession = Depends(get_session)):
    book = await book_service.get_book(book_uid=book_uid, session=session)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book

@book_router.post('/', status_code=status.HTTP_201_CREATED, response_model=BookModel)
async def create_book(book: BookCreateModel, session: AsyncSession = Depends(get_session)):
    new_book = await book_service.create_book(book_data=book, session=session)
    return new_book

@book_router.patch('/{book_uid}', status_code=status.HTTP_200_OK, response_model=BookModel)
async def update_book(book_uid: uuid.UUID, book_update_data: BookUpdateModel, session: AsyncSession = Depends(get_session)):
    book_to_update = await book_service.update_book(book_uid=book_uid, update_data=book_update_data, session=session)
    if not book_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book_to_update

@book_router.delete('/{book_uid}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_uid: uuid.UUID, session: AsyncSession = Depends(get_session)):
    book_to_delete = await book_service.get_book(book_uid=book_uid, session=session)
    if not book_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    await book_service.delete_book(book_uid=book_uid, session=session)
