from pydantic import BaseModel
from typing import List, Literal

class Loan(BaseModel):
    loan_date: str
    due_date: str
    returned_date: str | None
    book_id: int
    member_id: int

class LoanPatch(BaseModel):
    returned_date: str
    loan_id: int

class Book(BaseModel):
    title: str
    year: str
    authors: List[str]

class BookPatch(BaseModel):
    title: str | None
    year: str | None

class ReservationCreate(BaseModel):
    reservation_date: str
    book_id: int
    member_id: int


class MemberCreate(BaseModel):
    first_name: str
    last_name: str
    member_role: Literal["admin", "user"] = "user"
