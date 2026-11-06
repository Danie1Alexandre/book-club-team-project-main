import requests
import loans
from datetime import datetime, timedelta
from user_input import input_positive_integer, input_integer_between, input_date
from api_client import get_json
import os
import getpass
from dotenv import load_dotenv
from database import get_overdue_loans

load_dotenv()
FASTAPI_URL = "http://127.0.0.1:8000"

API_KEY = os.getenv("API_KEY") 

def print_lines():
     print("_"*50)   

def print_books(books):
    if not books:
        print("No matching books found.")
        return
    
    for book in books:
        book_id = book.get('id')
        title = book.get('title')
        year = book.get('year')
        author = book.get('author')
        print(f"{title} ({year}) — {author or 'Unknown author'}. Book id {book_id}")
    print_lines()

def browse_books():
    books = get_json(f"{FASTAPI_URL}/books")
    if not books:
        print("The Library Have No Books")
        print("\n--- BOOKS ---")  
    return print_books(books)

def search_books_by_query():
    query = input("Search for a book or author: ").strip().casefold()
    if not query:
        print("Please enter something.")
        return
    results = get_json(f"{FASTAPI_URL}/books/local-search", params={"q": query})
    print("\n--- Search Result ---")
    print_books(results)

def show_most_read_authors():
    member_id = input_positive_integer("Enter your member id: ")
    authors = get_json(f"{FASTAPI_URL}/members/{member_id}/most-read-authors")
    if not authors:
        print("No author reading history found for this member.")
        return
    print("Your most read authors:")
    for rank, author in enumerate(authors, start=1):
        print(f"{rank}. {author['author_name']} — {author['loan_count']} loan(s)")
    if len(authors) == 1:
        print(f"Your favorite author: {authors[0]['author_name']}")
    else:
        author_names = ", ".join(author['author_name'] for author in authors)
        print(f"Your favorite authors: {author_names}")

def borrow_book(days_to_borrow: int = 14):
    browse_books()
    book_id = input_positive_integer("Enter the id of the book you want to borrow: ")
    if book_is_available(book_id):    
        member_id = input_positive_integer("Enter your member id: ")

        date_today = datetime.today().date()
        due_date = date_today + timedelta(days=days_to_borrow)
        date_today_string = date_today.strftime("%Y-%m-%d")
        due_date_string = due_date.strftime("%Y-%m-%d")

        send_borrow_book_request(book_id=book_id, member_id=member_id, 
                                loan_date=date_today_string, due_date=due_date_string)
    else:
        print("The chosen book is unavailable.")

def book_is_available(book_id: int) -> bool:
    parameters = {"book_id": book_id}
    loans_for_book = get_json(f"{FASTAPI_URL}/loans/active", params=parameters)
    return len(loans_for_book) == 0

def reserve_book():
    browse_books()
    book_id = input_positive_integer("Enter the id of the book to reserve: ")
    if not book_is_available(book_id):       
        member_id = input_positive_integer("Enter your member id: ")
        payload = {
            "book_id": book_id,
            "member_id": member_id,
            "reservation_date": datetime.today().date().isoformat(),
        }

        headers = {
            "X-API-Key": API_KEY
        }
        response = requests.post(f"{FASTAPI_URL}/reservations", json=payload,  headers=headers, timeout=5)
        if response.status_code == 201:
            print("Reservation submitted.")
        else:
            detail = response.json().get("detail", "Sorry, could not reserve this book.")
            print(detail)
    else:
        print("The chosen book is already available.")

def send_borrow_book_request(book_id: int, member_id: int, loan_date: str, 
                due_date: str, returned_date: str | None = None):
    new_loan = {
        "loan_date": loan_date, 
        "due_date": due_date, 
        "returned_date": returned_date, 
        "book_id": book_id, 
        "member_id": member_id
    }

    headers = {
            "X-API-Key": API_KEY
        }

    response = requests.post(f"{FASTAPI_URL}/loans", json=new_loan, headers= headers, timeout=5)
    if response.status_code == 201:
        print("Your loan was created successfully.")
        print(f"Book loaned until {due_date}.")
    else:
        detail = response.json().get("detail", "Could not process loan.")
        print(f"Error: {detail}")

def edit_loan():
    loan_id = input_positive_integer("Enter a loan id to edit: ")
    book_id = input_positive_integer("Enter a new book id for the loan: ")
    member_id = input_positive_integer("Enter a new member id for the loan: ")
    loan_date = input_date("Enter a new loan date for the loan: ")
    due_date = input_date("Enter a new due date for the loan: ")
    returned_date = input_date("Enter a new return date for the loan: ")

    send_edit_loan_request(loan_id, book_id, member_id, loan_date, due_date, returned_date)

def send_edit_loan_request(loan_id: int, book_id: int, member_id: int, loan_date: str, 
                due_date: str, returned_date: str | None = None):
    edited_loan = {
        "book_id": book_id, 
        "member_id": member_id,
        "loan_date": loan_date, 
        "due_date": due_date, 
        "returned_date": returned_date, 
    }

    headers = {
            "X-API-Key": API_KEY
        }

    response = requests.put(f"{FASTAPI_URL}/loans/{loan_id}", headers=headers, json=edited_loan, timeout=5)
    if response.status_code == 200:
        print("Your loan was edited successfully.")
    elif response.status_code == 404:
        print("The loan was not found.")

def delete_loan():
    loan_id = input_positive_integer("Enter a loan id to delete: ")
    headers = {
            "X-API-Key": API_KEY
        }
    response = requests.delete(f"{FASTAPI_URL}/loans/{loan_id}", headers=headers, timeout=5)
    if response.status_code == 204:
        print("The loan was deleted successfully.")
    elif response.status_code == 404:
        print("The loan was not found.")
        
def return_book():
    member_id = input_positive_integer("Enter your member id: ")
    parameters = {"member_id": member_id}
    loans_for_member = get_json(f"{FASTAPI_URL}/loans/active", params=parameters)
    if loans_for_member:
        loans.print_loans(loans_for_member)
        list_number_choice = input_integer_between(min=1, max=len(loans_for_member), 
                                                   prompt="Enter number for the book you want to return: ")
        loan_id = get_loan_id_from_list_choice(list_number_choice, loans_for_member)
        send_return_book_request(loan_id)
    else:
        print("You have no loans.")

def send_return_book_request(loan_id: int, returned_date: str | None = None):
    if not returned_date:
        returned_date = datetime.today().date().strftime("%Y-%m-%d")

    return_info = {
        "loan_id": loan_id, 
        "returned_date": returned_date, 
    }

    headers = {
            "X-API-Key": API_KEY
        }

    response = requests.patch(f"{FASTAPI_URL}/loans", headers=headers, json=return_info, timeout=5)
    if response.status_code == 200:
        print("Your loan was returned successfully.")

def get_loan_id_from_list_choice(list_number_choice: int, loans_for_member: list) -> int:
    loan_index = list_number_choice - 1
    chosen_loan = loans_for_member[loan_index]
    return chosen_loan[0]

def view_a_loan():
    loan_id = input_positive_integer("Enter a loan id: ")
    loan = get_json(f"{FASTAPI_URL}/loans/{loan_id}")
    if loan:
        print_loan(loan)
    else:
        print("There is no such loan.")

def view_all_loans():
    loans = get_json(f"{FASTAPI_URL}/loans")
    if loans:
        print_loans(loans)
    else:
        print("There are no loans.")

def print_loans(loans: list):
    print("Your loans:")
    for number, loan in enumerate(loans, start=1):
        print(f"{number}. ", end="")
        print_loan(loan)

def print_loan(loan: list):
    loan_date = loan[1]
    due_date = loan[2]
    return_date = loan[3]
    book_id = loan[4]
    book = get_json(f"{FASTAPI_URL}/books/{book_id}")
    book_title = book[0][1]
    if return_date:
        print(f"{book_title}, due on {due_date}, loaned on {loan_date}, returned on {return_date}")
    else:
        print(f"{book_title}, due on {due_date}, loaned on {loan_date}")

def add_book_from_open_library():
    # get book info from openLibrary
    print("search for a book")
    search_book_title = input("Type Title: ")

    results = get_json(f"{FASTAPI_URL}/books/search", params= {"title": search_book_title})
    if not results:
        print("No results returned from API.")
        return

    #filter and print search results
    print("\nSearch results:")
    for index, doc in enumerate (results, start=1):
       title = doc.get ("title", "Title Unkown")
       authors = ", ".join(doc.get("author_name", ["Unknown Author"]))
       year = str (doc.get("first_publish_year", "Year Unkown"))
       print (f"[{index}] {title} - by {authors} ({year})")
    
    #user pick book to save
    try:
        choice = int(input(f"\nWhich book do you want to save? Pick a number between 1 and {len(results)}: "))
        if choice < 1 or choice > len(results):
            print("Not A Valid Number")
            return
    except ValueError:
        print("Choice Has To Be A Number.")
        return
    
    book_choice = results[choice-1]
    the_book = {
        "title": book_choice.get("title", "Title Unknown"),
        "year": str( book_choice.get("first_publish_year", "Year Unkown")),
        "authors": book_choice.get("author_name", ["Unknown Author"])
    }
    # Data gets sent to fast api
    headers = {
            "X-API-Key": API_KEY
        }

    save_book_to_db = requests.post(f"{FASTAPI_URL}/books", json=the_book, headers= headers, timeout= 10 )
    if save_book_to_db.status_code == 200:
        print(f"Book Saved: {the_book['title']}")
    else:
        try:
            detail = save_book_to_db.json().get("detail", "Book was not saved")
            print(f"Error: {detail}")
        except Exception:
            print(f"Book was not saved (Status code: {save_book_to_db.status_code})")   

def edit_book_title_year():
    book_id = input_positive_integer("Enter a book id to edit: ")
    new_title = input("Enter a new title for the book, or leave blank to not change it: ").strip()
    new_year = input("Enter a new year for the book, or leave blank to not change it: ").strip()

    edit_info = {
        "title": None if new_title == "" else new_title, 
        "year": None if new_year == "" else new_year 
    }

    headers = {
            "X-API-Key": API_KEY
        }

    response = requests.patch(f"{FASTAPI_URL}/books/{book_id}", headers=headers, json=edit_info, timeout=5)
    if response.status_code == 204:
        print("Your book was edited successfully.")
    elif response.status_code == 404:
        print("The book was not found.")

def edit_book_all_fields():
    book_id = input_positive_integer("Enter a book id to edit: ")
    new_title = input("Enter a new title for the book: ").strip()
    new_year = input("Enter a new year for the book: ").strip()
    authors_input = input("Enter the new author name(s), separated by commas: ").strip()
    authors_list = [name.strip() for name in authors_input.split(",")]

    edit_info = {
        "title": new_title, 
        "year": new_year,
        "authors": authors_list,
    }
    
    headers = {
            "X-API-Key": API_KEY
        }

    response = requests.put(f"{FASTAPI_URL}/books/{book_id}", headers=headers, json=edit_info, timeout=5)
    if response.status_code == 204:
        print("Your book was edited successfully.")
    elif response.status_code == 404:
        print("The book was not found.")

def delete_book():
    book_id = input_positive_integer("Enter a book id to delete: ")
    headers = {
            "X-API-Key": API_KEY
        }
    response = requests.delete(f"{FASTAPI_URL}/books/{book_id}", headers=headers, timeout=5)
    if response.status_code == 204:
        print("The book was deleted successfully.")
    elif response.status_code == 404:
        print("The book was not found.")

def print_most_borrowed(books):
    if not books:
        print("No books have been borrowed yet.")
        return
    print("\n--- MOST BORROWED BOOKS ---")
    for rank, book in enumerate(books, start=1):
        print(f"{rank}. {book['title']} ({book['year']}) — {book['author']} (Borrowed {book['borrow_count']} times)")

def view_most_borrowed_books():
    results = get_json(
        f"{FASTAPI_URL}/books/most-borrowed")
    if results is None:
        return
    print_most_borrowed(results)
    print_lines()

def view_never_borrowed_books():
    results = get_json(
        f"{FASTAPI_URL}/books/never-borrowed")
    if results is None:
        return
    print("\n--- BOOKS NEVER BORROWED ---")
    print_books(results)

def view_member_data():
    member_id = input("Enter your member ID to view profile: ").strip()
    if not member_id:
        print("Id Can Not Be Empty")
    
    headers = {
        "X-API-KEY": API_KEY
    }

    profile_data = get_json(f"{FASTAPI_URL}/members/{member_id}", headers= headers)
    
    if profile_data is None:
        return
    
    member_name = str (profile_data.get('first_name') + " " + profile_data.get('last_name'))
    print("\n--- PERSONAL PROFILE ---")
    print(f"ID: {profile_data.get('member_id')}")
    print(f"Name: {member_name}")
    print(f"Member Role: {profile_data.get('member_role')}")
    print_lines()
    
def view_overdue_loans():
    member_id = input_positive_integer("Enter your member id: ")
    overdue_loans = get_overdue_loans()
    member_loans = [
        loan for loan in overdue_loans
        if loan["member_id"] == member_id
    ]

    if not member_loans:
        print("You have no overdue loans.")
        return

    print("Your overdue loans:")
    for loan in member_loans:
        print(f"- {loan['title']} — due on {loan['due_date']}")
    print_lines()

def view_all_overdue_loans():
    overdue_loans = get_json(f"{FASTAPI_URL}/loans/overdue")
    if overdue_loans is None:
        return
    if not overdue_loans:
        print("There are no overdue loans.")
        return

    print("\n--- OVERDUE LOANS ---")
    for loan in overdue_loans:
        print(f"{loan['member_name']}: {loan['title']} — due on {loan['due_date']}")
    print_lines()

def view_member_borrowed_books():
    member_id = input_positive_integer("Enter your member id: ")
    borrowed_books = loans.get_active_loans(member_id)
    if borrowed_books:
        print("Your borrowed books:")
        for loan in borrowed_books:
            loans.print_loan(loan)
    else:
        print("You have no borrowed books.")

def print_menu_options(options: list[str]):
    for option in options:
        print(option)

def admin_mode_authorization():
    password = getpass.getpass(prompt="Enter your admin password to enter admin mode: ")
    if password == os.getenv("ADMIN_PASSWORD"):
        admin_menu()
    else:
        print("Incorrect password.")

def delte_user_data():
    member_id = input("Enter the member ID: ").strip()
    if not member_id:
        print("ID cannot be empty.")
        return
    
    confirm = input(f"Are you sure you want to delete personal info for member {member_id}? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Operation cancelled.")
        return
    
    headers = {
        "X-API-Key": API_KEY
    }

    try:
        response = requests.delete(f"{FASTAPI_URL}/members/{member_id}/anonymize", headers=headers, timeout=5)
        
        if response.status_code == 200:
            print(response.json()["message"])
        elif response.status_code == 401:
            print(f"Error: {response.json().get('detail')}")
        elif response.status_code == 404:
            print("Error: Member not found.")
        else:
            print(f"Failed to delete data. Server status: {response.status_code}")
            
    except requests.exceptions.RequestException:
        print("Could not connect to server.")


def create_member():
    first_name = input("Enter the member's first name: ").strip()
    last_name = input("Enter the member's last name: ").strip()
    if not first_name or not last_name:
        print("First name and last name are required.")
        return

    response = requests.post(
        f"{FASTAPI_URL}/members",
        json={"first_name": first_name, "last_name": last_name},
        headers={"X-API-Key": API_KEY},
        timeout=5,
    )
    if response.status_code == 201:
        print(f"Member created: {first_name} {last_name}.")
    else:
        detail = response.json().get("detail", "Could not create member.")
        print(f"Error: {detail}")

def user_menu():
    user_menu_options = ["\n1. Browse books", "2. Search books or authors", "3. Borrow a book", 
                            "4. Return a book", "5. Reserve a book", "6. View My Borrowed Books", 
                            "7. View My Most Read Authors", "8. View my overdue loans", 
                            "9. Admin mode", "10. Quit"]
    
    while True:
        print("\n--- USER MENU ---")
        print_menu_options(user_menu_options)
        choice = input("Choose an option: ").strip()
        if choice == "1":
            browse_books()
        elif choice == "2":
            search_books_by_query()
        elif choice == "3":
            borrow_book()
        elif choice == "4":
            return_book()
        elif choice == "5":
            reserve_book()
        elif choice == "6":
            view_member_borrowed_books()
        elif choice == "7": 
            show_most_read_authors() 
        elif choice == "8":
            view_overdue_loans()
        elif choice == "9":
            admin_mode_authorization()
        elif choice == "10":
            break
        else:
            print(f"Choose a number between 1 and {len(user_menu_options)}.")
            
def admin_menu():
    admin_menu_options = ["\n1. Browse books", "2. Search books or authors", "3. View Most Borrowed Books", 
                          "4. View Never Borrowed Books", "5. Manage books", "6. Manage loans", 
                          "7. View Overdue Loans", "8. Create Member", "9. View member data", 
                          "10. Delete personal member data","11. Quit"]

    while True:
        print("\n--- ADMIN MENU ---")
        print_menu_options(admin_menu_options)
        choice = input("Choose an option: ").strip()
    
        if choice == "1":
            browse_books()
        elif choice == "2":
            search_books_by_query()
        elif choice == "3":
            view_most_borrowed_books()
        elif choice == "4":
            view_never_borrowed_books() 
        elif choice == "5":
            admin_menu_books()
        elif choice == "6":
            admin_menu_loans()
        elif choice == "7":
            view_all_overdue_loans()
        elif choice == "8":
            create_member()
        elif choice == "9":
            view_member_data()
        elif choice == "10":
            delte_user_data()
        elif choice == "11":
            break
        else:
            print(f"Choose a number between 1 and {len(admin_menu_options)}.")

def admin_menu_books():
    admin_menu_book_options = ["\n1. Add a book from Open Library", "2. Edit book title and/or year", 
                               "3. Edit all book fields", "4. Delete a book", "5. Go back"]
    while True:
        print_menu_options(admin_menu_book_options)
        choice = input("Choose an option: ").strip()
    
        if choice == "1":
            add_book_from_open_library()
        elif choice == "2":
            edit_book_title_year()
        elif choice == "3":
            edit_book_all_fields()
        elif choice == "4":
            delete_book()
        elif choice == "5":
            break
        else:
            print(f"Choose a number between 1 and {len(admin_menu_book_options)}.")

def admin_menu_loans():
    admin_menu_loans_options = ["\n1. Create a loan", "2. Return a loan", "3. View a loan", 
                                "4. View all loans", "5. Edit a loan", "6. Delete a loan", "7. Go back"]
    while True:
        print_menu_options(admin_menu_loans_options)
        choice = input("Choose an option: ").strip()
    
        if choice == "1":
            borrow_book()
        elif choice == "2":
            return_book()
        elif choice == "3":
            view_a_loan()
        elif choice == "4":
            view_all_loans()
        elif choice == "5":
            edit_loan()
        elif choice == "6":
            delete_loan()
        elif choice == "7":
            break
        else:
            print(f"Choose a number between 1 and {len(admin_menu_loans_options)}.")

user_menu()
