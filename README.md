# Book Club Team Project

A small library API and command-line client for a book club. The project uses FastAPI and SQLite to manage members, books, authors, loans, and reservations. Books can be searched in the local collection or looked up through Open Library.

## Features

- Browse, search, add, update, and remove books.
- Create, view, update, return, and delete loans.
- Reserve books and view overdue loans.
- View book borrowing statistics and books that have never been borrowed.
- Search Open Library and save a selected result to the local collection.
- Protect routes that change data with an `X-API-Key` header.
- Use the interactive command-line client in `client.py`.

## Database diagram

![ER diagram](docs/ER%20Diagram.PNG)

The SQLite schema is in `schema.sql`; `seed.py` adds sample data.

## Personal data

The `Members` table stores these fields about each member:

`member_id` Internal identifier used to distinguish members and link their loans and reservations (auto-generated).

`first_name`, `last_name` Used to identify a member in the library and show who has borrowed or reserved a book. 

`member_role` Indicates whether the member is recorded as an ordinary user or an admin. 

The project does not store other personal information like emails for members as the API does not need such information yet.

## Requirements

- Python 3.10 or newer
- pip

## Install

Run these commands from the project directory. Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv

.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
```

Create your local environment file from the example (.env.example -> .env) and set your own values for both secrets:
`API_KEY` is required for write routes and for the client to make authenticated changes. `ADMIN_PASSWORD` is used by the command-line client's admin menu.

## Create and seed the database

Create the tables, then insert the sample data:

```powershell
python -c "import sqlite3; db=sqlite3.connect('library.db'); db.executescript(open('schema.sql', encoding='utf-8').read()); db.close()"

python seed.py
```

Run the schema command only when creating a new database. 
Run `seed.py` once per fresh database.

## Run the API

Start the server from the project directory:

```powershell
uvicorn main:app --reload
```

For development use:

```powershell
fastapi dev main.py
```

The API is available at <http://127.0.0.1:8000>. FastAPI's interactive API documentation is at <http://127.0.0.1:8000/docs>.

## Run the command-line client

```powershell
.venv\Scripts\Activate.ps1
python client.py
```
