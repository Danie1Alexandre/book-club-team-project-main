from database import connect, add_member, add_author, add_book, add_books_author, add_loan

DATABASE_PATH = "library.db"

def create_test_data():
    conn = connect(DATABASE_PATH)
    add_member(conn, "Benny", "Andersson", "user")
    add_member(conn, "Anni-Frid", "Lyngstad", "user")
    add_member(conn, "Agnetha", "Fältskog", "user")
    add_member(conn, "Björn", "Ulvaeus", "user")
    add_member(conn, "Admin", "Librarian", "admin")

    add_author(conn, "J.R.R. Tolkien")
    add_author(conn, "Terry Pratchett")
    add_author(conn, "Neil Gaiman")
    add_author(conn, "Astrid Lindgren")

    add_book(conn, "The Hobbit", "1937")
    add_book(conn, "Good Omens", "1990")
    add_book(conn, "Pippi Långstrump", "1945")

    add_books_author(conn, book_id=1, author_id=1)
    add_books_author(conn, book_id=2, author_id=2)
    add_books_author(conn, book_id=2, author_id=3)
    add_books_author(conn, book_id=3, author_id=4)
    
    add_loan(loan_date="2026-10-27", due_date="2026-11-07", book_id=1, member_id=1)
    conn.close()

create_test_data()