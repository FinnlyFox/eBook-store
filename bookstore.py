############### Please note the file path is set up for my folder layout, you may have to change it to fit your system's layout ###############

import sqlite3
import sys
from tabulate import tabulate

# Main function so I can store my functions at the bottom (I just like it this way)
def main():
    # A try/except/finally block used to catch any exception regarding the db itself and close it if something goes wrong
    try:
        # Create the database
        # Open a connection to the DB and set a cursor
        db = sqlite3.connect('ebookstore')
        cursor = db.cursor()

        # Check if the "books" table exists since the table is never dropped when we finish
        cursor.execute('''
            SELECT count(*)
            FROM sqlite_master
            WHERE type='table' AND name='books'
        ''')
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            # Create the Table "books" if it does not exist
            cursor.execute('''
                CREATE TABLE books (
                    id INTEGER PRIMARY KEY,
                    Title TEXT(70),
                    Author TEXT(55),
                    Qty INTEGER(5)
                )
            ''')
            print("Table has been created.") ################

            # Create a list of tuples to use for populating the table once off
            book_info = [
                (3001, 'A Tale of Two Cities', 'Charles Dickens', 30),
                (3002, 'Harry Potter and the Philosopher\'s Stone', 'J.K. Rowling', 40),
                (3003, 'The Lion, the Witch and the Wardrobe', 'C. S. Lewis', 25),
                (3004, 'The Lord of the Rings', 'J.R.R Tolkien', 37),
                (3005, 'Alice in Wonderland', 'Lewis Carroll', 12),
                (3006, 'The Little Prince', 'Antoine de Saint-Exupéry', 54)
            ]

            # Add all the info in "book_info" into the table using executemany
            cursor.executemany('''
                INSERT INTO books(id, Title, Author, Qty)
                VALUES(?,?,?,?)''', book_info)
            print("Every book added correctly.") ###########

            db.commit()

        # Display the data to the user
        print("\nHello, here is the current information on every book in your database.\n")
        select_all(cursor)
        print("")
    
        # ====Menu Options====
        while True:
            # Presenting the menu to the user
            menu = input('''Select one of the following Options below:
            1 - Enter book
            2 - Update book
            3 - Delete book
            4 - Search books
            0 - Exit
            : ''')

            # Make calls to the appropriate functions
            if menu == '1':
                add_book(cursor, db)

            elif menu == '2':
                update_book(cursor, db)

            elif menu == '3':
                delete_book(cursor, db)

            elif menu == '4':
                search_for_book(cursor)

            elif menu == '0':
                print("\nGood Bye!!\n")

                # Close db connection and exit the program
                db.close()
                sys.exit()

            else:
                print("That is not a valid input.")
                continue


    # It is a catch all statement to handle obscure errors I may have missed
    except Exception as err:
        # Roll back if error occurs
        db.rollback()
        raise err


    finally:
        # Close db connection if something goes wrong (fail safe)
        db.close()


# Function used to display the table in a user-friendly manner
def select_all(temp_cursor):
    temp_cursor.execute('''
        SELECT *
        FROM books
    ''')

    rows = temp_cursor.fetchall()
    if not rows:
        print("No books found.")
    else:
        headers = ['id', 'Title', 'Author', 'Qty']
        print(tabulate(rows, headers=headers, tablefmt="grid"))


# Function used to add a book to the database (runs all required checks as well)
def add_book(cursor, db):
    print("\nPlease input all the required information of the new book:\n")

    while True:
        # Get all info
        try:
            book_id = int(input("ID:                         "))
            title = input("Title:                      ")
            author = input("Name of the Author:         ")
            quantity = int(input("Quantity of books in stock: "))
        except ValueError:
            print("\nThese are not valid inputs,\nplease type them as (interger)(string)(string)(interger).\n")
            break

        cursor.execute('''
            SELECT COUNT(*)
            FROM books
            WHERE id=? OR Title=?''', (book_id, title))
        book_exists = cursor.fetchone()[0]

        if not book_exists:
            cursor.execute('''
                INSERT INTO books(id, Title, Author, Qty)
                VALUES(?,?,?,?)''', (book_id, title, author, quantity))
            db.commit()

            print("\nHere is your new updated table.\n")
            select_all(cursor)
            print("")
            break

        else:
            print("\nThis ID or Title already exists, please try again.\n")
            break


# Function used to update the information on a book in the database
def update_book(cursor, db):
    print("\nPlease enter all required information about the updated book:\n")
    while True:
        try:
            temp_id = int(input("Current ID of the book you would like to change: "))
            book_id = int(input("ID:                                      "))
            title = input("Title:                                   ")
            author = input("Name of the Author:                      ")
            quantity = int(input("Quantity of books in stock:              "))

        except ValueError:
            print("\nThat is not a valid ID, please enter an Integer only.\n")
            break

        # Check if the book exists to be updated
        cursor.execute('''
            SELECT COUNT(*)
            FROM books
            WHERE id=?''', (temp_id,))
        book_exists = cursor.fetchone()[0]

        # Check if new info is duplicated
        cursor.execute('''
            SELECT COUNT(*)
            FROM books
            WHERE id=? OR Title=?''', (book_id, title))
        is_duplicate = cursor.fetchone()[0]

        if not is_duplicate:
            if book_exists:
                cursor.execute('''
                    UPDATE books
                    SET id = ?,
                        Title = ?,
                        Author = ?,
                        Qty = ?
                    WHERE id=?''', (book_id, title, author, quantity, temp_id))
                db.commit()

                print("\nHere is your new updated table.\n")
                select_all(cursor)
                print("")
                break

            else:
                print("\nThis book does not exist yet, please go add it to the database instead.\n")
                break

        else:
            print("\nThis ID or Title already exists, please try again.\n")
            break


# Function used to delete a book from the database
def delete_book(cursor, db):
    print("\nPlease enter all required information on the book you wish to delete.\n")

    while True:
        # Get all info
        try:
            book_id = int(input("ID:                         "))
            title = input("Title:                      ")

        except ValueError:
            print("\nThat is not a valid ID, please enter only and Integer for the ID.\n")
            break

        # Check that the book exists
        cursor.execute('''
            SELECT COUNT(*)
            FROM books
            WHERE id=? AND Title=?''', (book_id, title))
        book_exists = cursor.fetchone()[0]

        # Delete the book
        if book_exists:
            cursor.execute('''
                DELETE FROM books
                WHERE id=? AND Title=?''', (book_id, title))
            db.commit()

            print("\nHere is your new updated table.\n")
            select_all(cursor)
            print("")
            break

        else:
            print("\nNo such book exists and thus cannot be deleted, please try again.\n(Make sure you entered the ID and Title correctly)\n")
            break


# Function to search if there are any books with the desired Title
def search_for_book(cursor):
    unknown_title = input("Enter the title of the book you are looking for: ")

    # Check if the book exists
    cursor.execute('''
        SELECT COUNT(*)
        FROM books
        WHERE Title=?''', (unknown_title,))
    book_exists = cursor.fetchone()[0]

    # Print the relevant info to the user
    if book_exists:
        # Get the Quantity for the print statement
        cursor.execute('''
            SELECT Qty
            FROM books
            WHERE Title=?''', (unknown_title,))
        Quantity = cursor.fetchone()[0]

        print(f"\nGood news! We do have \"{unknown_title}\", and have {Quantity} copies in stock.\n")

    else:
        print(f"\nI am sorry, we do not have \"{unknown_title}\" in stock.\n")


# Call for the "main()" function
if __name__ == "__main__":
    main()


# Cites:
"""
https://renenyffenegger.ch/notes/development/databases/SQLite/internals/schema-objects/sqlite_master/index#:~:text=sqlite_master%20is%20an%20internal%20table,with%20the%20SQLite%20shell%20command%20.
^ Information on sqlite_master

Rest of my work is from past experiance so nothing more to cite.
"""
