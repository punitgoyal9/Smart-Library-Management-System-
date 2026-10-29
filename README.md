# Smart Library Management System

## Project Overview

The **Smart Library Management System** is a desktop application for managing library books, members, issue and return transactions, and overdue fines. It uses a Python Tkinter graphical interface, an Oracle Database backend, and PL/SQL procedures for core database operations.

The application helps a librarian issue books, view the catalogue, search active issues, process returns, and check overdue charges. Python handles the user interface and input, while PL/SQL performs important transaction and inventory updates in the database.

## Objectives

- Manage books, members, and borrowing transactions.
- Validate member status and book availability before issuing a book.
- Automatically calculate a due date 15 days after the issue date.
- Track book returns and update available inventory.
- Calculate overdue fines at **₹10 per day**.
- Search active issues and browse them with pagination.
- Provide a graphical desktop interface for common library operations.

## Technology Stack

- **Python** — application logic
- **Tkinter** — desktop graphical user interface
- **Oracle Database** — persistent data storage
- **PL/SQL** — database procedures and fine-calculation function
- **python-oracledb** — Python-to-Oracle connectivity
- **python-dotenv** — loading database configuration from `.env`

## Project Structure

| File or folder | Purpose |
|---|---|
| `punittest.py` | Main Tkinter application, including database operations and library screens |
| `punit.py` | Alternate themed version of the desktop application |
| `requirements.txt` | Python package dependencies |
| `PLSQL/punit.sql` | Oracle table, sequence, sample-data, function, and procedure definitions |
| `.env.example` | Template for Oracle connection settings |
| `advanceFeatures.md` | Notes about additional or planned features |

## Main Features

### Book issue

The user enters a member ID and book ID. The application checks that the book exists and has available copies, then calls the `issue_book_proc` PL/SQL procedure. The procedure checks the member's active status, prevents the same member from issuing the same book again while it is already issued, decreases available stock, and creates a transaction.

### Due-date calculation

The issue date defaults to the current date. The interface calculates the due date as **issue date + 15 days** and displays it as read-only.

### Issued-book search and reports

The application can display active issues by member ID or book ID. A separate issued-books window supports searching by member ID or member name, pagination of 10 records per page, overdue status, and a return action.

### Book catalogue

The catalogue displays each book's ID, title, author, and available copies.

### Fine calculation

Overdue fines are calculated at **₹10 for each day after the due date**. Fine and issue-status information is displayed for active transactions.

### Book return

The return action calls `return_book_proc`. The procedure marks the transaction as returned, records the return date, calculates any overdue fine, and increases the available stock by one.

### Data reset

The application includes a reset operation that removes transaction records and sets every book's available copies to 5.

> **Warning:** The reset operation does not restore each book's original stock value; it sets all stock values to 5.

## Database Design

The SQL script defines these main tables:

- **`books`** — book ID, title, author, and available copies.
- **`members`** — member ID, name, email, and membership status.
- **`library_transactions`** — transaction ID, member ID, book ID, issue date, due date, return date, and status.

It also creates the `trans_seq` sequence to generate transaction IDs and inserts sample books and members.

### PL/SQL components

- **`calculate_library_fine`** — calculates a fine from a due date and return date at ₹10 per overdue day.
- **`issue_book_proc`** — validates the member and book, checks stock and duplicate active issues, updates stock, and creates an issue transaction.
- **`return_book_proc`** — records a return, calculates any fine, and restores one copy to stock.
- **`reset_library_data`** — clears transactions and resets book stock to 5 copies per book.

## Setup and Run

### 1. Prerequisites

Install Python and configure an accessible Oracle Database. The database must support the SQL features used in the application, including `OFFSET ... FETCH NEXT` pagination.

### 2. Install Python dependencies

From the project directory, run:

```bash
pip install -r requirements.txt
```

The dependencies in `requirements.txt` are `oracledb` and `python-dotenv`.

### 3. Configure the database connection

Create a `.env` file in the project root using `.env.example` as a template:

```env
DB_USER=your_oracle_username
DB_PASSWORD=your_oracle_password
DB_DSN=localhost:1521/XE
```

Replace these example values with the credentials and DSN for your Oracle Database. Keep real credentials private and do not commit them to source control.

### 4. Prepare the Oracle schema

Run `PLSQL/punit.sql` using an Oracle SQL tool, such as SQL Developer, connected to the intended schema.

**Schema note:** `return_book_proc` updates a `fine_amount` column, but the table definition does not create that column. The SQL file contains a commented-out statement for it. Before compiling the return procedure, add the column if it does not already exist:

```sql
ALTER TABLE library_transactions
ADD fine_amount NUMBER DEFAULT 0;
```

### 5. Start the application

Run the main application from the project root:

```bash
python punittest.py
```

## Selected Code Snippets

These short snippets highlight the main implementation without reproducing the entire source code.

### Automatic due-date calculation

The interface calculates the due date 15 days after the entered issue date:

```python
issue_date = datetime.strptime(issue_date_str, "%Y-%m-%d")
due_date = issue_date + timedelta(days=15)
```

### Calling the issue procedure from Python

The application converts the entered dates for Oracle and calls the PL/SQL procedure:

```python
out_msg = cursor.var(oracledb.STRING)
cursor.callproc(
    "issue_book_proc",
    [member_id, book_id, issue_date_obj, due_date_obj, out_msg],
)
```

### Overdue fine calculation

The application calculates overdue charges at ₹10 per day:

```python
if today > due:
    days_late = (today - due).days
    fine = days_late * 10
else:
    fine = 0
```

### PL/SQL stock validation and issue transaction

The procedure checks stock before decreasing inventory and inserting an active transaction:

```sql
IF v_copies <= 0 THEN
    p_message := 'Error: Book is out of stock!';
ELSE
    UPDATE books
    SET available_copies = available_copies - 1
    WHERE book_id = p_book_id;

    INSERT INTO library_transactions (
        transaction_id, member_id, book_id, issue_date, due_date, status
    )
    VALUES (
        trans_seq.NEXTVAL, p_member_id, p_book_id,
        p_issue_date, p_due_date, 'ISSUED'
    );

    COMMIT;
    p_message := 'Success: Book issued successfully!';
END IF;
```

## Implementation Notes

- The application loads Oracle connection settings from environment variables using `python-dotenv`.
- Database errors and input validation messages are shown through the Tkinter interface.
- The SQL script includes sample book and member records for initial testing.
- The Python application calls PL/SQL procedures for issue, return, and reset operations.
- The reset procedure sets all book stock values to 5, regardless of their previous values.
- Although the main application file is named `punittest.py`, it launches the graphical application; it is not a standalone automated unit-test suite.

## Conclusion

The Smart Library Management System demonstrates integration of a Python desktop application with Oracle Database and PL/SQL. It provides a graphical workflow for managing book circulation and illustrates database concepts such as relational tables, foreign keys, sequences, stored procedures, and functions.
