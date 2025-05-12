"""The Script acts as a Library Database Management System using Python with Postgress SQL"""

import datetime as dt

import psycopg2


# SQL Control
def sql_controller(table, command, t_data):
    """Used to Control the SQL Database"""
    with psycopg2.connect(
        dbname="library",
        user="postgres",
        password="postgress",
        host="localhost",
        port="5432",
    ) as conn:
        with conn.cursor() as cur:

            # Test Mode 
            test = t_data['test']
            data = t_data.copy()
            data.pop('test')

            # Create table if it doesnt exist
            cur.execute(
                """CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        User_Name TEXT NOT NULL,
                        Contact INT UNIQUE NOT NULL
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

            # cur.execute(
            #     """CREATE TABLE IF NOT EXISTS transactions (
            #             id SERIAL PRIMARY KEY,
            #             book_id INT REFERENCES books(id),
            #             user_id INT REFERENCES users(id),
            #             Borrow_Date DATE NOT NULL,
            #             Return_Date DATE
            #             );"""
            # )

            # cur.execute(
            #     """CREATE TABLE IF NOT EXISTS fines (
            #             id SERIAL PRIMARY KEY,
            #             book_id INT REFERENCES books(id),
            #             user_id INT REFERENCES users(id),
            #             borrow_date INT REFERENCES books(Borrow_Date),
            #             return_date INT REFERENCES users(Return_Date),
            #             Amount INT
            #             );"""
            # )

            # User Operations
            if table == "users":
                # Check if user exists from before
                cur.execute(
                    f"SELECT id,User_Name FROM users WHERE Contact = %s",
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
                                (new_name, result[0][0])
                            )
                            return f"{data['User_Name']} updated"

                    case 3:  # Delete
                        if result == []:
                            return("User does not exist")
                        else:
                            cur.execute(
                                f"DELETE FROM users WHERE Contact = ({data['Contact']})"
                            )
                            return(f"{data['User_Name']} Deleted")
                    case 4:  # Read
                        if result == []:
                            return("User does not exist")
                        else:
                            return(result[0][1])

                    case _:  # Default case
                        return("Invalid Operation")

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
                                additional_data["Available"] = additional_data["Copies"]
                                data.update(additional_data)

                            keys = ", ".join(data.keys())
                            placeholders = ", ".join(["%s"] * len(data))
                            values = list(data.values())

                            cur.execute(
                                f"INSERT INTO books ({keys}) VALUES ({placeholders})",
                                (values),
                            )
                            return(f"{data['Book_Name']} added")

                        else:
                            print("Book already exists, updating counts")
                            new_Copies = data["Copies"] + result[0][1]
                            new_Available = data["Availiable"] + result[0][2]

                            if new_Copies <= 0:
                                print(
                                    "Error! Too many deletions, Choose option to delete all Books"
                                )
                            else:
                                cur.execute(
                                    f"UPDATE books SET Copies = {new_Copies}, Available = {new_Available} WHERE id = {result[0][3]}"
                                )

                    case 2:  # Delete
                        if result == []:
                            return("Book does not exist")
                        else:
                            cur.execute(f"DELETE FROM books WHERE id = {result[0][3]}")
                            return(f"All Copies of {data['Book_Name']} Deleted")

                    case 3:  # Read
                        if result == []:
                            return("Book does not exist")
                        else:
                            note = {
                                "Book_Name": result[0][0],
                                "Copies": result[0][1],
                                "Available": result[0][2],
                                "id": result[0][3],
                                "Location": result[0][4],
                                "user_id": result[0][5],
                            }
                            return(note)

                    case _:
                        return("Invalid Input")


# Librarian Menu
print(" Welcome to the Librarian Command Line Interface \n")
while __name__=="__main__":
    print(
        "\n What do you want to do?"
        "\n 1. Issue / Return a book"
        "\n 2. Manage Books"
        "\n 3. Manage Users"
        "\n 4. Manage Fines "
        "\n 5. Export Records"
        "\n 6. Settings"
        "\n 0. Exit"
    )

    admin = int(input("What is your Choice? (Enter number): "))

    match admin:
        case 2:
            table = "books"
            command = int(
                input(
                    "1. Add / Modify number of Books , 2. Delete All Books, 3. Read Books "
                )
            )
            data = {
                "Book_Name": input("Enter Book Name "),
                'test': False,
            }
            print(sql_controller(table, command, data))
        case 3:
            table = "users"
            command = int(
                input("1. Add User, 2. Modify User, 3. Delete User 4. Read User ")
            )
            data = {
                "User_Name": input("Enter User Name "),
                "Contact": input("Enter Contact "),
                'test': False,
            }
            print(sql_controller(table, command, data))

        case 0:
            print("\n Exiting")
            break

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