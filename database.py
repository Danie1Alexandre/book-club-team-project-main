from datetime import date
import sqlite3
from typing import Literal

DATABASE_PATH = "library.db"

class DuplicateReservationError(Exception):
    """Raised when a member tries to reserve the same book more than once."""

def connect(database_path: str):
    conn = sqlite3.connect(database_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def save_book_to_db(title, year, authors):
    conn = connect('library.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Books(title, year) 
            VALUES (?,?);
            """, (title, year)
        )  
        book_id = cursor.lastrowid

        for author_name in authors:
            cursor.execute("""
                SELECT author_id FROM Authors 
                WHERE author_name = ?;
            """,(author_name,))
            row = cursor.fetchone()

            if row:
                author_id = row[0]
            else:
                cursor.execute("""
                INSERT INTO Authors (author_name)
                VALUES (?);
                """,(author_name,)   
                )

                author_id = cursor.lastrowid
            
            cursor.execute("""
                INSERT INTO Books_Author (book_id, author_id)
                VALUES (?,?);
                """,(book_id, author_id)
            )

        conn.commit()
        return True
    except sqlite3.Error as e:
        print (f"Database error: {e}")
        return False
    finally:
        conn.close()

def add_member(conn, first_name: str, last_name: str, member_role: Literal["admin", "user"]):
    conn.execute(
        "INSERT INTO Members (first_name, last_name, member_role) VALUES (?, ?, ?)",
        (first_name, last_name, member_role))
    conn.commit()

def add_author(conn, author_name: str):
    conn.execute(
        "INSERT INTO Authors (author_name) VALUES (?)",
        (author_name,))
    conn.commit()

def add_book(conn, title: str, year: str):
    conn.execute(
        "INSERT INTO Books (title, year) VALUES (?, ?)",
        (title, year))
    conn.commit()

def add_books_author(conn, book_id: int, author_id: int):
    conn.execute(
        "INSERT INTO Books_Author (book_id, author_id) VALUES (?, ?)",
        (book_id, author_id))
    conn.commit()

def get_book_by_id(book_id: int):
    conn = connect(DATABASE_PATH)
    cursor = conn.execute(
        "SELECT * FROM Books WHERE book_id = ?", 
        (book_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_loan(book_id: int, member_id: int, loan_date: str, due_date: str, returned_date: str | None = None):
    conn = connect(DATABASE_PATH)
    conn.execute(
        "INSERT INTO Loans (loan_date, due_date, returned_date, book_id, member_id) VALUES (?, ?, ?, ?, ?)",
        (loan_date, due_date, returned_date, book_id, member_id))
    conn.commit()
    conn.close()

def member_exists(member_id: int) -> bool:
    conn = connect(DATABASE_PATH)
    try:
        return conn.execute(
            "SELECT 1 FROM Members WHERE member_id = ? LIMIT 1",
            (member_id,)
        ).fetchone() is not None
    finally:
        conn.close()

def get_all_loans():
    conn = connect(DATABASE_PATH)
    cursor = conn.execute("SELECT * FROM Loans")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_loans_for_book(book_id: int):
    conn = connect(DATABASE_PATH)
    cursor = conn.execute(
        "SELECT * FROM Loans WHERE book_id = ?", 
        (book_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_loans_for_member(member_id: int):
    conn = connect(DATABASE_PATH)
    cursor = conn.execute(
        "SELECT * FROM Loans WHERE member_id = ?", 
        (member_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_active_loans():
    conn = connect(DATABASE_PATH)
    cursor = conn.execute("SELECT * FROM Loans WHERE returned_date IS NULL")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_active_loans_for_book(book_id: int):
    conn = connect(DATABASE_PATH)
    cursor = conn.execute(
        "SELECT * FROM Loans WHERE book_id = ? AND returned_date IS NULL", 
        (book_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_active_loans_for_member(member_id: int):
    conn = connect(DATABASE_PATH)
    cursor = conn.execute(
        "SELECT * FROM Loans WHERE member_id = ? AND returned_date IS NULL", 
        (member_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def return_loan(loan_id: int, returned_date: str):
    conn = connect(DATABASE_PATH)
    conn.execute(
        "UPDATE Loans SET returned_date = ? WHERE loan_id = ?",
        (returned_date, loan_id,))
    conn.commit()
    conn.close()

def edit_loan(loan_id: int, book_id: int, member_id: int, loan_date: str, due_date: str, returned_date: str | None = None):
    conn = connect(DATABASE_PATH)
    try:
        conn.execute(
            "UPDATE Loans SET loan_date = ?, due_date = ?, returned_date = ?, book_id = ?, member_id = ? WHERE loan_id = ?",
            (loan_date, due_date, returned_date, book_id, member_id, loan_id))
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()

def delete_loan(loan_id: int):
    conn = connect(DATABASE_PATH)
    try:
        conn.execute(
            "DELETE FROM Loans WHERE loan_id = ?",
            (loan_id,))
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()
    
def get_most_read_authors_for_member(member_id: int):
    conn = connect(DATABASE_PATH)
    rows = conn.execute(
        """
        WITH author_loan_counts AS (
            SELECT a.author_name, COUNT(l.loan_id) AS loan_count
                FROM Loans AS l
            JOIN Books_Author AS ba ON ba.book_id = l.book_id
            JOIN Authors AS a ON a.author_id = ba.author_id
            WHERE l.member_id = ?
            GROUP BY a.author_name
        )
        SELECT author_name, loan_count
        FROM author_loan_counts
        WHERE loan_count = (SELECT MAX(loan_count) FROM author_loan_counts)
        ORDER BY author_name
        """,
        (member_id,)
    ).fetchall()
    conn.close()
    return [
        {"author_name": row[0], "loan_count": row[1]} for row in rows
    ]

BOOKS_QUERY = """
    SELECT b.book_id, b.title, b.year, GROUP_CONCAT(a.author_name, ', ')
    FROM Books AS b
    LEFT JOIN Books_Author AS ba USING (book_id)
    LEFT JOIN Authors AS a USING (author_id)
    GROUP BY b.book_id, b.title, b.year
"""

def browse_books_db():
    conn = connect('library.db')
    rows = conn.execute(BOOKS_QUERY + "ORDER BY b.title").fetchall()
    conn.close()
    
    book_list = []
    for row in rows:
        book_list.append({
            "id": row[0],
            "title": row[1],
            "year": row[2],
            "author": row[3]
        })
    return book_list

def search_books_or_authors(query: str):
    search_word = query.strip().casefold() 
    
    conn = connect('library.db')
    books = conn.execute(BOOKS_QUERY + "ORDER BY b.title").fetchall()
    conn.close()
    
    matched_book_list = [
        book for book in books
        if search_word in book[1].casefold()
        or (book[3] and search_word in book[3].casefold())
    ]

    #make a list of dictionarys
    books_dictionary = []
    for book in matched_book_list:
        books_dictionary.append({
            "id": book[0],
            "title": book[1],
            "year": book[2],
            "author": book[3]
    })
    return(books_dictionary)

def view_most_borrowed_books_db():
    conn = connect(DATABASE_PATH)
    most_borrowed_books = conn.execute("""
        SELECT 
            Books.book_id, 
            Books.title,
            Books.year,
            GROUP_CONCAT(DISTINCT Authors.author_name) AS author_name, 
            COUNT(DISTINCT Loans.loan_id) AS borrow_count
        FROM Books
        INNER JOIN Loans ON Books.book_id = Loans.book_id
        LEFT JOIN Books_Author ON Books.book_id = Books_Author.book_id
        LEFT JOIN Authors On Books_Author.author_id = Authors.author_id
        GROUP BY Books.book_id
        ORDER BY borrow_count DESC
        """).fetchall()
    conn.close()
    
    most_borrowed_list = []
    for book in most_borrowed_books:
        
        # This is part, only for add space between authors when printing
        author_text = book[3] or "Unknown author"
        author_space= author_text.replace(",", ", ")   

        most_borrowed_list.append({
            "id": book[0],
            "title": book[1],
            "year": book[2],
            "author": author_space,
            "borrow_count": book[4]
    })
    return(most_borrowed_list)

def view_never_borrowed_books_db():
    conn = connect('library.db')
    never_borrowed_books = conn.execute("""
        SELECT Books.book_id, Books.title, Books.year, GROUP_CONCAT(Authors.author_name, ', ') AS author_name
        FROM Books
        LEFT JOIN Loans ON Books.book_id = Loans.book_id
        LEFT JOIN Books_Author ON Books.book_id = Books_Author.book_id
        LEFT JOIN Authors On Books_Author.author_id = Authors.author_id
        WHERE Loans.loan_id IS NULL
        GROUP BY Books.book_id
        ORDER BY Books.title
        """).fetchall()
    conn.close()

    never_borrowed_list = []
    for book in never_borrowed_books:
        never_borrowed_list.append({
            "id": book[0],
            "title": book[1],
            "year": book[2],
            "author": book[3] or "Unknown author",
    })
    return(never_borrowed_list)

def reserve_book(book_id: int, member_id: int, reservation_date: str):
    conn = connect(DATABASE_PATH)
    try:
        existing = conn.execute(
            "SELECT 1 FROM Reservations WHERE book_id = ? AND member_id = ? LIMIT 1",
            (book_id, member_id)
        ).fetchone()
        if existing:
            raise DuplicateReservationError

        cursor = conn.execute(
            "INSERT INTO Reservations (reservation_date, book_id, member_id) VALUES (?, ?, ?)",
            (reservation_date, book_id, member_id))
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def add_book_alternative_version(title, year):
    conn = connect(DATABASE_PATH)
    try:
        cursor = conn.execute(
            "INSERT INTO Books (title, year) VALUES (?, ?)",
            (title, year),
        )
        book_id = cursor.lastrowid
        conn.commit()
        return book_id
    finally:
        conn.close()


def edit_book_patch(book_id: int, title: str | None = None, year: int | None = None):
    conn = connect(DATABASE_PATH)
    try:
        updates = []
        values = []

        if title is not None:
            updates.append("title = ?")
            values.append(title)
        if year is not None:
            updates.append("year = ?")
            values.append(year)

        if not updates:
            return False

        values.append(book_id)
        cursor = conn.execute(
            f"UPDATE Books SET {', '.join(updates)} WHERE book_id = ?",
            values,
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def edit_book_put(book_id: int, title: int, year: int, authors: list[str]):
    conn = connect(DATABASE_PATH)
    try:
        cursor = conn.execute(
            "UPDATE Books SET title = ?, year = ? WHERE book_id = ?",
            (title, year, book_id),
        )

        for author_name in authors:
            cursor.execute("""
                SELECT author_id FROM Authors 
                WHERE author_name = ?;
            """,(author_name,))
            row = cursor.fetchone()
        
            if row:
                author_id = row[0]
            else:
                cursor.execute("""
                INSERT INTO Authors (author_name)
                VALUES (?);
                """,(author_name,)   
                )
        
                author_id = cursor.lastrowid
        
            cursor = conn.execute(
                "UPDATE Books_Author SET book_id = ? WHERE author_id = ?",
                (book_id, author_id),
            )

        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def remove_book(book_id: int):
    conn = connect(DATABASE_PATH)
    try:
        conn.execute(
            "DELETE FROM Books_Author WHERE book_id = ?",
            (book_id,),
        )
        cursor = conn.execute(
            "DELETE FROM Books WHERE book_id = ?",
            (book_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_member_info_db(member_id: int):
    conn = connect(DATABASE_PATH)
    member_info = conn.execute(
        "SELECT member_id, first_name, last_name, member_role FROM Members WHERE member_id = ?",
        (member_id,)
    ).fetchone()
    conn.close()

    if not member_info:
        return None
    
    return{
        "member_id": member_info[0],
        "first_name": member_info[1],
        "last_name": member_info[2],
        "member_role": member_info[3]
    }

def get_overdue_loans():
    conn = connect(DATABASE_PATH)
    try:
        rows = conn.execute("""
            SELECT Members.member_id, Members.first_name, Members.last_name,
                   Books.book_id, Books.title, Loans.loan_id, Loans.due_date
            FROM Loans
            JOIN Members ON Members.member_id = Loans.member_id
            JOIN Books ON Books.book_id = Loans.book_id
            WHERE Loans.returned_date IS NULL
              AND Loans.due_date < ?
            ORDER BY Members.last_name, Members.first_name, Loans.due_date
        """, (date.today().isoformat(),)).fetchall()

        return [
            {
                "member_id": row[0],
                "member_name": f"{row[1]} {row[2]}",
                "book_id": row[3],
                "title": row[4],
                "loan_id": row[5],
                "due_date": row[6],
            }
            for row in rows
        ]
    finally:
        conn.close()

def delet_user(member_id: int )-> bool:
    conn = connect(DATABASE_PATH)

    member = conn.execute("SELECT 1 FROM Members WHERE member_id = ?", (member_id,)).fetchone()
    if not member:
        conn.close()
        return False

    conn.execute("""
        UPDATE Members 
        SET first_name = 'Deleted', last_name = 'User' 
        WHERE member_id = ?
    """, (member_id,))
    conn.commit()
    conn.close()
    return True

def create_member(first_name: str, last_name: str, member_role: Literal["admin", "user"] = "user"):
    conn = connect(DATABASE_PATH)
    try:
        add_member(conn, first_name, last_name, member_role)
    finally:
        conn.close()
