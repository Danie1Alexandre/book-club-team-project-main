# Daily scrum status reports
## Week 1
### October 27
What we did yesterday: Sprint planning as a group

What we are going to do today: Database creation as a group

Blockers: None

### October 28
Yesterday: 

Database creation, started on individual tasks.

Today: 
* Daniel: Working on adding a new book, and using the external book API when adding new books.
* Martin: Made a pull request for browsing the book collection, now available for review. Will continue on edit and remove books from the library next.
* Sanne: Working on borrowing a book. Will integrate the borrowing with browsing the book collection once browse book collection has been merged to main.

Blockers: None

### October 29
Yesterday:
* Daniel: Worked on adding a new book using the external book API. Created a pull request for it.
* Martin: Worked on add, edit and remove books from the library.
* Sanne: Worked on borrowing a book. Created a pull request for it.

Today:
* Daniel: PR review. Start on Use FastAPI for browsing books.
* Martin: PR review. Continue on add, edit and remove books from the library.
* Sanne: PR review. Start on return a book.

Blockers: None

### October 30
Yesterday:
* Daniel: PR review and comments changes, and started working on Use FastAPI to browse books.
* Martin: Continued working on add, edit and remove books from the library.
* Sanne: PR review and merge conflict fixing, and started working on returning a book.

Today:
* Daniel: Almost done with use FastAPI to browse books. Will create a pull request for it once done, and pick a new task from the board.
* Martin: Created a pull request for add, edit and remove a book. Will pick a new task from the board once done.
* Sanne: Will continue on returning a book and create a pull request for it if finished. Will pick a new task if return a book is finished. Will also create a pull request for this week's daily scrum notes. 
* Dmitri: Joins the team today. 
* As a team: PR review. Sprint review and retrospective at 2 pm today.

Blockers: Dmitri does not have access to the repo or board yet. This will be fixed after the daily standup meeting today.


## Week 2

### November 2
Friday last week:
* Daniel: Worked on use FastAPI to browse books.
* Martin: Worked on the bug fix for printing books with multiple authors when browsing books.
* Sanne: Continued on return a book.
* Dmitri: Worked on reserve a book.

Today:
* As a team: Sprint planning to start the day. Then PR review.
* Daniel: Will work on most borrowed books and books never borrowed.
* Martin: Will continue on the bug fix for books with multiple authors.
* Sanne: Will finish return a book, and fix the merge conflicts and the merge bug.
* Dmitri: Will work on most read authors. 

Blockers: None

### November 3
Yesterday:
As a team: Sprint planning.
* Daniel: Worked on view most borrowed books and books never borrowed.
* Martin: Made a PR for the bug fix with mulitple authors.
* Sanne: Finished and created a pull request for return a book.
* Dmitri: Made a PR for most read authors. Merged the reserve book PR. Started on a helper for the external API. 

Today:
* Daniel: Will work on adding API keys to every route that changes data.
* Martin: Will pick a new task from the board, and have a look at the PR for add, edit and remove books.
* Sanne: Will start on developing the admin view, and fix the new merge conflicts in the return a book PR.
* Dmitri: Will continue working on the helper for the external API.

Blockers: None

### November 4
Yesterday:
* Daniel: Added API keys to every route that changes data. Also viewing never borrowed books.
* Martin: Worked on seeing your own overdue books.
* Sanne: Started working on the admin view. Will split the task into two since it it large: Admin view with CRUD for books and Admin view with CRUD for loans. 
* Dmitri: Worked on the helper for the external API.

Today:
* Daniel: Will work on personal data endpoints.
* Martin: Will work on seeing your own overdue books.
* Sanne: Will work on adding admin mode, and CRUD operations for loans.
* Dmitri: Will work on showing borrowed books for member.

Blockers: The task for Admin view with CRUD for books is dependent on an open PR that contains database functions for adding, deleting and editing books. We merged this open PR during the standup.

### November 5
Yesterday:
* Daniel: Worked on personal data endpoints.
* Martin: Worked on seeing your own overdue books.
* Sanne: Finished admin mode and the CRUD paths for loans.
* Dmitri: Worked on showing borrowed books for member.

Today:
* Daniel: Work on adding an endpoint for getting and deleting personal data.
* Martin: Will pick a new task from the board.
* Sanne: Work on and finish the admin mode CRUD for books.
* Dmitri: Work on adding timeout to external API call, create member for admin, and view overdue loans for all members.
As a group: Presentation and demo preparations.

Blockers: None