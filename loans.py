from datetime import date

from user_input import input_positive_integer
from api_client import FASTAPI_URL, get_json


def print_loan(loan: list):
    loan_date = loan[1]
    due_date = loan[2]
    book_id = loan[4]
    book = get_json(f"{FASTAPI_URL}/books/{book_id}")
    book_title = book[0][1]
    print(f"{book_title}, due on {due_date}, loaned on {loan_date}")


def print_loans(loans: list):
    print("Your loans:")
    for number, loan in enumerate(loans, start=1):
        print(f"{number}. ", end="")
        print_loan(loan)
        

def get_active_loans(member_id: int):
    active_loans = get_json(
        f"{FASTAPI_URL}/loans/active", params={"member_id": member_id})
    return active_loans
