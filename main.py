from fastapi import FastAPI, HTTPException, Header, Depends
from models import Loan, LoanPatch, Book, BookPatch, ReservationCreate, MemberCreate
from dotenv import load_dotenv
import external_api
import database
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

def check_key(x_api_key: str | None = Header(None)):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Server Configuration error")
    
    if x_api_key !=API_KEY:
        raise HTTPException(status_code=401, detail= "not valid API key")

def find_loan(loan_id: int):
    for loan in database.get_all_loans():
        if loan[0] == loan_id:
            return loan
    raise HTTPException(status_code=404, detail="Loan not found")

def find_book(book_id: int):
    for book in database.browse_books_db():
        if book.get("id") == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/loans")
def get_loans(member_id: int | None = None, book_id: int | None = None):
    if book_id:
        return database.get_all_loans_for_book(book_id)
    elif member_id:
        return database.get_all_loans_for_member(member_id)
    else:
        return database.get_all_loans()

@app.get("/loans/active")
def get_active_loans(book_id: int | None = None, member_id: int | None = None):
    if member_id:
        return database.get_active_loans_for_member(member_id)
    elif book_id:
        return database.get_active_loans_for_book(book_id)
    else:
        return database.get_all_active_loans()

@app.get("/loans/overdue")
def get_overdue_loans():
    return database.get_overdue_loans()

@app.get("/loans/{loan_id}")
def get_loan(loan_id: int):
    return find_loan(loan_id)

@app.get("/members/{member_id}/most-read-authors")
def get_most_read_authors(member_id: int):
    return database.get_most_read_authors_for_member(member_id)

@app.post("/loans", status_code=201, dependencies=[Depends(check_key)])
def create_loan(loan: Loan):
    if not database.member_exists(loan.member_id):
        raise HTTPException(status_code=404, detail="Member not found!")
        
    new_loan = {
            "loan_date": loan.loan_date, 
            "due_date": loan.due_date, 
            "returned_date": loan.returned_date, 
            "book_id": loan.book_id, 
            "member_id": loan.member_id
        }
    database.add_loan(**new_loan)
    return new_loan
  
@app.patch("/loans", dependencies=[Depends(check_key)])
def return_loan(loan_update: LoanPatch):
    loan = find_loan(loan_update.loan_id)
    returned_date = loan[3]
    if returned_date:
        raise HTTPException(status_code=409, detail="The book has already been returned")
    else:
        update = {
                    "loan_id": loan_update.loan_id, 
                    "returned_date": loan_update.returned_date, 
                }
        database.return_loan(**update)
        return update

@app.put("/loans/{loan_id}", status_code=200, responses={404: {"description": "Not found"}}, dependencies=[Depends(check_key)])
def edit_loan(loan_id: int, edited_loan: Loan):
    existing_loan = find_loan(loan_id)
    edited_loan_info = {
            "loan_date": edited_loan.loan_date, 
            "due_date": edited_loan.due_date, 
            "returned_date": edited_loan.returned_date, 
            "book_id": edited_loan.book_id, 
            "member_id": edited_loan.member_id,
            "loan_id": loan_id
        }
    if existing_loan:
        database.edit_loan(**edited_loan_info)
        return edited_loan

@app.delete("/loans/{loan_id}", status_code=204, responses={404: {"description": "Not found"}}, dependencies=[Depends(check_key)])
def delete_loan(loan_id: int):
    loan = find_loan(loan_id)
    if loan:
        database.delete_loan(loan_id)
      
@app.post("/reservations", status_code=201, dependencies=[Depends(check_key)])
def create_reservation(reservation: ReservationCreate):
    try:
        reservation_id = database.reserve_book(
            reservation.book_id, reservation.member_id, reservation.reservation_date)
        return {"reservation_id": reservation_id, "message": "Book reserved."}
    except database.DuplicateReservationError:
        raise HTTPException(status_code=409, detail="You have already reserved this book.")
    except Exception as e:
        print(f"error: {e} ---")
        raise HTTPException(status_code=400, detail="Could not reserve the book.")

@app.get("/books/search")
def search_book_open_library(title: str):
    results = external_api.search_open_library(title)

    if not results:
        raise HTTPException(status_code=404, detail="No books found")
    return results

@app.post("/books", dependencies=[Depends(check_key)])
def add_book(book: Book):
    saved = database.save_book_to_db(book.title, book.year, book.authors)
    if not saved:
        raise HTTPException(status_code=500, detail= "Book Colud Not Be Saved in Database")
    return {"message": f"The book was saved: {book.title}"}

@app.get("/books")
def get_book_colection():
    books = database.browse_books_db()
    return books

@app.get("/books/local-search")
def search_local_library(q: str = ""):
    return database.search_books_or_authors(q)

@app.get("/books/most-borrowed")
def get_most_borrowed_books():
    return database.view_most_borrowed_books_db()

@app.get("/books/never-borrowed")
def get_never_borrowed_books():
    return database.view_never_borrowed_books_db()

@app.get("/books/{book_id}")
def get_book(book_id: int):
    return database.get_book_by_id(book_id)

@app.patch("/books/{book_id}", status_code=204, responses={404: {"description": "Not found"}}, dependencies=[Depends(check_key)])
def patch_book(book_id: int, book_update: BookPatch):
    book = find_book(book_id)
    if book:
        database.edit_book_patch(book_id, book_update.title, book_update.year)

@app.put("/books/{book_id}", status_code=204, responses={404: {"description": "Not found"}}, dependencies=[Depends(check_key)])
def put_book(book_id: int, book_update: Book):
    book = find_book(book_id)
    if book:
        database.edit_book_put(book_id, book_update.title, book_update.year, book_update.authors)

@app.delete("/books/{book_id}", status_code=204, responses={404: {"description": "Not found"}}, dependencies=[Depends(check_key)])
def delete_book(book_id: int):
    book = find_book(book_id)
    if book:
        database.remove_book(book_id)

@app.get("/members/{member_id}", dependencies=[Depends(check_key)])
def get_member_info(member_id: int):
    member_data = database.get_member_info_db(member_id)

    if not member_data:
        raise HTTPException(status_code=404, detail="Member not found")
    
    return member_data

@app.delete("/members/{member_id}/anonymize",status_code=200, dependencies=[Depends(check_key)])
def anonymize_member(member_id: int):
    anonymize = database.delet_user(member_id)

    if not anonymize:
        raise HTTPException(status_code=404, detail= "Member not found")
    
    return {"message": f"Peronal Data For Member {member_id} has been deleted"}


@app.post("/members", status_code=201, dependencies=[Depends(check_key)])
def create_member(member: MemberCreate):
    database.create_member(
        member.first_name,
        member.last_name,
        member.member_role,
    )

    return {
        "first_name": member.first_name,
        "last_name": member.last_name,
        "member_role": member.member_role,
    }
