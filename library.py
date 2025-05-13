"""The Script acts as a Library Database Management System using Python with Postgress SQL"""

import json
import datetime as dt
import csv
from decimal import Decimal
import os

import psycopg2


# SQL Control
def sql_controller(table, command, t_data, settings):
    """Used to Control the SQL Database"""
    with psycopg2.connect(
        dbname = settings['dbname'],
        user= settings['user'],
        password= settings['password'],
        host= settings['host'],
        port= settings['port'],
    ) as conn:
        with conn.cursor() as cur:

            # Test Mode
            test = t_data["test"]
            data = t_data.copy()
            data.pop("test")

            # Create table if it doesnt exist
            cur.execute(
                """CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        User_Name TEXT NOT NULL,
                        Contact INT UNIQUE NOT NULL,
                        Books_Borrowed JSONB,
                        Fines DECIMAL 
                        );"""
            )

            cur.execute(
                """CREATE TABLE IF NOT EXISTS books (
                        id SERIAL PRIMARY KEY,
                        Book_Name TEXT UNIQUE NOT NULL ,
                        Author_Name TEXT,
                        Copies INT NOT NULL,
                        Available INT,
                        Location TEXT,
                        user_id JSONB
                        );"""
            )

            cur.execute(
                """CREATE TABLE IF NOT EXISTS transactions (
                        id SERIAL PRIMARY KEY,
                        book_id INT REFERENCES books(id) ON DELETE CASCADE,
                        user_id INT REFERENCES users(id) ON DELETE CASCADE,
                        Issue_Date DATE NOT NULL,
                        Due_Date DATE,
                        Actual_Return_Date DATE,
                        Transaction TEXT NOT NULL
                        );"""
            )

            # User Operations
            if table == "users":
                # Check if user exists from before
                cur.execute(
                    f"SELECT * FROM users WHERE Contact = %s",
                    (data["Contact"],),
                )
                result = cur.fetchall()

                match command:
                    case 1:  # Insert
                        if result == []:
                            keys = ", ".join(data.keys())
                            placeholders = ", ".join(["%s"] * len(data))
                            values = list(data.values())
                            cur.execute(
                                f"INSERT INTO users ({keys}) VALUES ({placeholders})",
                                (values),
                            )
                            return f"{data['User_Name']} added"

                        else:
                            return "User already exists"

                    case 2:  # Update
                        if result == []:
                            return "User does not exist"
                        else:
                            new_name = str(data["User_Name"])
                            cur.execute(
                                "UPDATE users SET User_Name = %s WHERE id = %s",
                                (new_name, result[0][0]),
                            )
                            return f"{data['User_Name']} updated"

                    case 3:  # Delete
                        if result == []:
                            return "User does not exist"
                        else:
                            if not test:
                                if (
                                    result[0][4] == None or abs(result[0][4]) == 0
                                ) and (result[0][3] == None or len(result[0][3]) == 0):
                                    cur.execute(
                                        f"DELETE FROM users WHERE Contact = %s",(data['Contact'],)
                                    )
                                    return f"{data['User_Name']} Deleted"
                                else:
                                    return f"{data['User_Name']} has active fines / not returned books, cannot delete"
                            else:
                                cur.execute(
                                    f"DELETE FROM users WHERE Contact = %s",(data['Contact'],)
                                )
                                return f"{data['User_Name']} Deleted"
                    case 4:  # Read
                        if result == []:
                            return "User does not exist"
                        else:
                            note = {
                                "User_Name": result[0][1],
                                "Contact": result[0][2],
                                "Books_Borrowed": result[0][3],
                                "Fines": result[0][4],
                            }
                            return note

                    case 5:  # Pay Fines
                        if result == []:
                            return "User does not exist"
                        else:
                            print(f"{result[0][1]} has {result[0][4]} in fines.")
                            if not test:
                                if result[0][4] == None:
                                    prev_fine = 0
                                else:
                                    prev_fine = result[0][4]
                                x = Decimal(
                                    input(
                                        "How much of the fine do you want to pay now?"
                                    )
                                )
                                updated_fine = max(prev_fine - x, 0)
                                cur.execute(f"UPDATE users SET Fines = %s WHERE id = %s",(updated_fine,result[0][0]),)
                                return f"{result[0][1]} has paid off {x}, leaving {updated_fine} in fines."

                    case _:  # Default case
                        return "Invalid Operation"

            # Book Operations
            if table == "books":
                cur.execute(
                    f"SELECT Book_Name,Copies,Available,id,Location,user_id FROM books WHERE Book_Name = %s",
                    (data["Book_Name"],),
                )
                result = cur.fetchall()

                match command:
                    case 1:  # Add a copy
                        if result == []:
                            if not test:
                                additional_data = {
                                    "Author_Name": input("Enter Author Name "),
                                    "Copies": int(
                                        input(
                                            "Enter number of books (+ to add, - to delete) ex- (+3 / -5)"
                                        )
                                    ),
                                    "Available": 0,
                                    "Location": input(
                                        "Enter location of the copy (ex - R1C1) "
                                    ),
                                }
                                data.update(additional_data)
                            data["Available"] = data["Copies"]

                            keys = ", ".join(data.keys())
                            placeholders = ", ".join(["%s"] * len(data))
                            values = list(data.values())

                            cur.execute(
                                f"INSERT INTO books ({keys}) VALUES ({placeholders})",
                                (values),
                            )
                            return f"{data['Book_Name']} added"

                        else:
                            print("Book already exists, updating counts")
                            new_Copies = data["Copies"] + result[0][1]
                            new_Available = data["Available"] + result[0][2]

                            if new_Copies <= 0:
                                print(
                                    "Error! Too many deletions, Choose option to delete all Books"
                                )
                                return f"{data['Book_Name']} updated"
                            else:
                                cur.execute(
                                    f"UPDATE books SET Copies = %s, Available = %s WHERE id =%s ",(new_Copies,new_Available,result[0][3]),
                                )

                    case 2:  # Delete
                        if result == []:
                            return "Book does not exist"
                        else:
                            if not test:
                                if result[0][5] is None or len(result[0][5]) == 0:
                                    cur.execute(
                                        f"DELETE FROM books WHERE id = %s",(result[0][3],)
                                    )
                                    return f"All Copies of {data['Book_Name']} Deleted"
                                else:
                                    return "Some users still have the book, hence it cannot be deleted"
                            else:
                                cur.execute(
                                    f"DELETE FROM books WHERE id = %s",(result[0][3],)
                                )
                                return f"All Copies of {data['Book_Name']} Deleted"
                    case 3:  # Read
                        if result == []:
                            return "Book does not exist"
                        else:
                            note = {
                                "Book_Name": result[0][0],
                                "Copies": result[0][1],
                                "Available": result[0][2],
                                "Location": result[0][4],
                                "user_id": result[0][5],
                            }
                            return note

                    case _:
                        return "Invalid Input"

            # Transactions
            if table == "transactions":

                match command:

                    case 1:  # Borrow
                        cur.execute(
                            f"SELECT id,Available,user_id FROM books WHERE Book_Name = %s",
                            (data["Book_Name"],),
                        )
                        rows1 = cur.fetchone()
                        cur.execute(
                            f"SELECT id, User_Name,Books_Borrowed,Fines FROM users WHERE Contact = %s",
                            (data["Contact"],),
                        )
                        rows2 = cur.fetchone()

                        borrow_date = dt.date.today()
                        due_date = borrow_date + dt.timedelta(
                            days=settings["Issue_Duration"]
                        )
                        borrow_str = borrow_date.strftime("%Y-%m-%d")
                        return_str = due_date.strftime("%Y-%m-%d")

                        transaction = "Issue"

                        # Check constraints
                        if rows1 == None:
                            return "Book does not exist"

                        if rows2 == None:
                            return "User does not exist"

                        try:
                            books_borrowed = json.loads(rows2[2])
                        except:
                            books_borrowed = []

                        if data["Book_Name"] in books_borrowed:
                            return (
                                "User has already borrowed the same book. Issue Denied."
                            )

                        if rows1[1] < 1:
                            return "Book is not available to issue"

                        if len(books_borrowed) >= settings["Max_Book_Issues"]:
                            return "User has issued max number of books possible"

                        cur.execute(
                            "INSERT INTO transactions "
                            "(book_id, user_id,Issue_Date,Due_Date,Transaction)"
                            " VALUES (%s, %s,%s,%s,%s)",
                            (rows1[0], rows2[0], borrow_str, return_str, transaction),
                        )

                        available = rows1[1]
                        available = available - 1
                        books_borrowed.append(data["Book_Name"])

                        try:
                            book_users = json.loads(rows1[2])
                        except:
                            book_users = []
                        book_users.append(rows2[1])

                        cur.execute(
                            "UPDATE books SET Available = %s, user_id = %s WHERE id = %s",
                            (available, json.dumps(book_users), rows1[0]),
                        )
                        cur.execute(
                            "UPDATE users SET Books_Borrowed = %s WHERE id = %s",
                            (json.dumps(books_borrowed), rows2[0]),
                        )
                        return f"{data['Book_Name']} has been borrowed by {rows2[1]}"

                    case 2:  # Return
                        cur.execute(
                            f"SELECT id,Available,user_id FROM books WHERE Book_Name = %s",
                            (data["Book_Name"],),
                        )
                        rows1 = cur.fetchone()
                        cur.execute(
                            f"SELECT id, User_Name,Books_Borrowed,Fines FROM users WHERE Contact = %s",
                            (data["Contact"],),
                        )
                        rows2 = cur.fetchone()

                        if rows1 == None:
                            return "Book does not exist"

                        if rows2 == None:
                            return "User does not exist"

                        cur.execute(
                            "UPDATE transactions SET transaction = %s, Actual_Return_Date = %s WHERE book_id = %s AND user_id = %s",
                            ("return", dt.date.today(), rows1[0], rows2[0]),
                        )
                        try:  # handle error if rows2[2] is a list instead of json
                            books_borrowed = json.loads(rows2[2])
                        except:
                            books_borrowed = rows2[2]

                        try:
                            books_borrowed.remove(data["Book_Name"])
                        except:
                            return f"{data['Book_Name']} has not been issued or has already been returned."
                        available = rows1[1]
                        available = available + 1

                        try:  # handle error if rows2[2] is a list instead of json
                            book_users = json.loads(rows1[2])
                        except:
                            book_users = rows1[2]
                        book_users.remove(rows2[1])

                        cur.execute(
                            "UPDATE books SET Available = %s, user_id = %s WHERE id = %s",
                            (available, json.dumps(book_users), rows1[0]),
                        )
                        cur.execute(
                            "UPDATE users SET Books_Borrowed = %s WHERE id = %s",
                            (json.dumps(books_borrowed), rows2[0]),
                        )

                        # Fine Calculations
                        cur.execute(
                            f"SELECT Due_Date FROM transactions WHERE book_id = %s and user_id = %s",(rows1[0],rows2[0])
                        )
                        rows3 = cur.fetchone()

                        issue_date = rows3[0]
                        days_late = max((dt.date.today() - issue_date).days, 0)
                        fine = Decimal(str(days_late)) * Decimal(
                            str(settings["Fines_Per_Day"])
                        )

                        if rows2[3] == None:
                            prev_fine = 0
                        else:
                            prev_fine = rows2[3]
                        new_fine = prev_fine + fine

                        cur.execute(
                            f"UPDATE users SET Fines = %s WHERE id = %s",(new_fine,rows2[0],),
                        )
                        return f"{data['Book_Name']} has been returned by {rows2[1]} with fine of {fine}"

                    case _:
                        return "Invalid Input"


# Librarian Menu
print(" Welcome to the Librarian Command Line Interface \n")
while __name__ == "__main__":
    print(
        "\n What do you want to do?"
        "\n 1. Issue / Return a book"
        "\n 2. Manage Books"
        "\n 3. Manage Users"
        "\n 4. Settings "
        "\n 5. Export Records"
        "\n 0. Exit"
    )

    admin = int(input("What is your Choice? (Enter number): "))

    with open("./config.json", "r") as config_file:
        settings = json.load(config_file)

    match admin:
        case 1:  # Manage Transactions
            table = "transactions"
            command = int(input("1. Issue Books, 2. Return Books "))
            data = {
                "Book_Name": input("Enter Book Name "),
                "Contact": input("Enter Contact Number "),
                "test": False,
            }
            print(sql_controller(table, command, data, settings))
        case 2:  # Manage Book Data
            table = "books"
            command = int(
                input(
                    "1. Add / Modify number of Books , 2. Delete All Books, 3. Read Books "
                )
            )
            data = {
                "Book_Name": input("Enter Book Name "),
                "test": False,
            }
            print(sql_controller(table, command, data, settings))

        case 3:  # Manage User Data
            table = "users"
            command = int(
                input(
                    "1. Add User, 2. Modify User, 3. Delete User, 4. Read User, 5. Pay Fines "
                )
            )
            data = {
                "User_Name": input("Enter User Name "),
                "Contact": input("Enter Contact "),
                "test": False,
            }
            print(sql_controller(table, command, data, settings))

        case 0:  # Exit out of CLI
            print("\n Exiting")
            break

        case 4:  # Settings Management
            with psycopg2.connect(
                dbname = settings['dbname'],
                user= settings['user'],
                password= settings['password'],
                host= settings['host'],
                port= settings['port'],
            ) as conn:
                with conn.cursor() as cur:

                    cur.execute(
                        """CREATE TABLE IF NOT EXISTS settings (
                            id SERIAL PRIMARY KEY,
                            Librarian_Name TEXT NOT NULL,
                            Issue_Duration INT NOT NULL,
                            Fines_Per_Day DECIMAL NOT NULL,
                            Max_Book_Issues_Per_User INT NOT NULL,
                            Password TEXT NOT NULL,
                            Date_Time TIMESTAMP NOT NULL
                            );"""
                    )

                    # Get last settings to compare passwords for authentication
                    cur.execute("SELECT * FROM settings ORDER BY id DESC LIMIT 1")
                    row = cur.fetchone()

                    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    if row is None:
                        # Default settings
                        cur.execute(
                            "INSERT INTO settings "
                            "(Librarian_Name, Issue_Duration,Fines_Per_Day,Max_Book_Issues_Per_User,Password,Date_Time)"
                            " VALUES (%s, %s,%s,%s,%s,%s)",
                            ("Default", 15, 0.1, 3, "Testing", now),
                        )
                        print("Default Settings created")

                        # Update config.json
                        new_settings = {
                            "Issue_Duration": 15,
                            "Fines_Per_Day": 0.1,
                            "Max_Book_Issues": 3,
                        }
                        with open("config.json", "w") as f:
                            json.dump(new_settings, f, indent=4)

                    else:
                        while True:
                            temp_password = input("Enter Previous Password ")
                            if temp_password == row[5]:
                                print("Authorized")

                                # Enter new details
                                Librarian_Name = input("Enter your name: ")
                                Issue_Duration = int(input("Enter issue duration: "))
                                Fines_Per_Day = float(input("Enter Fines Per Day: "))
                                Max_Issues_Per_User = int(
                                    input("Enter Max Book Issues Per User: ")
                                )
                                x = input("Do you want to reset password?(Y/N): ")
                                if x == "Y" or x == "y":
                                    pwd = input("Enter New Password: ")
                                else:
                                    pwd = row[5]

                                cur.execute(
                                    "INSERT INTO settings "
                                    "(Librarian_Name, Issue_Duration,Fines_Per_Day,Max_Book_Issues_Per_User,Password,Date_Time)"
                                    " VALUES (%s, %s,%s,%s,%s,%s)",
                                    (
                                        Librarian_Name,
                                        Issue_Duration,
                                        Fines_Per_Day,
                                        Max_Issues_Per_User,
                                        pwd,
                                        now,
                                    ),
                                )

                                print("Settings Updated")

                                # Update config.json
                                new_settings = {
                                    "Issue_Duration": Issue_Duration,
                                    "Fines_Per_Day": Fines_Per_Day,
                                    "Max_Book_Issues": Max_Issues_Per_User,
                                }
                                with open("config.json", "w") as f:
                                    json.dump(new_settings, f, indent=4)

                                break
                            else:
                                print("Wrong Password")
                                continue

        case 5:  # Export to CSV
            conn = psycopg2.connect(
                dbname = settings['dbname'],
                user= settings['user'],
                password= settings['password'],
                host= settings['host'],
                port= settings['port'],
            )

            tables = ["users", "books", "transactions"]

            # Create data folder to host CSV files
            if not os.path.isdir("data"):
                os.mkdir("data")

            for table in tables:
                with conn.cursor() as cur:
                    cur.execute(f"SELECT * FROM {table}")
                    rows = cur.fetchall()
                    colnames = [desc[0] for desc in cur.description]

                         
                    with open(f"./data/{table}.csv", "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(colnames)
                        writer.writerows(rows)

            print("Exported all data tables to CSV")
            conn.close()

        case _:
            print("Invalid Input")
            continue

    admin = input("Do you want to continue? (Y/N) ")
    if admin == "Y" or admin == "y":
        continue
    elif admin == "N" or admin == "n":
        break
    else:
        print("Invalid Entry")
        continue
