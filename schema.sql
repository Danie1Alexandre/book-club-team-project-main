CREATE TABLE Members(
	member_id INTEGER PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	member_role TEXT CHECK(member_role IN ('admin', 'user'))
);

CREATE TABLE Books(
	book_id INTEGER PRIMARY KEY,
	title TEXT NOT NULL,
	year TEXT 
);

CREATE TABLE Loans(
	loan_id INTEGER PRIMARY KEY,
	loan_date TEXT NOT NULL,
	due_date TEXT NOT NULL CHECK(due_date>=loan_date),
	returned_date TEXT,
	book_id INTEGER NOT NULL, 
	member_id INTEGER NOT NULL,
	FOREIGN KEY (book_id) REFERENCES Books(book_id),
	FOREIGN KEY (member_id) REFERENCES Members(member_id)
);

CREATE TABLE Authors(
	author_id INTEGER PRIMARY KEY,
	author_name TEXT NOT NULL
);

CREATE TABLE Books_Author(
	book_id INTEGER,
	author_id INTEGER,
	PRIMARY KEY (book_id, author_id),
	FOREIGN KEY (book_id) REFERENCES Books(book_id),
	FOREIGN KEY (author_id) REFERENCES Authors(author_id)
);

CREATE TABLE Reservations(
	reservation_id INTEGER PRIMARY KEY,
	reservation_date TEXT NOT NULL,
	book_id INTEGER NOT NULL,
	member_id INTEGER NOT NULL,
	FOREIGN KEY (book_id) REFERENCES Books(book_id),
	FOREIGN KEY (member_id) REFERENCES Members(member_id)
);





