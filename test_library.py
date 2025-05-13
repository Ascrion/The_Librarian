from library import sql_controller
import json

def test_sql_controller(): 

    with open("config.json", "r") as config_file:
        settings = json.load(config_file)

    # To test transactions and overall integration
    user_data = {
        "User_Name": "KAREN",
        "Contact": 1234,
        'test': True,
    }
    book_data = {
        "Book_Name": "HARRY POTTER",
        "Author_Name": "JK Rowling",
        "Copies":5,
        "Available": 0,
        "Location":"R1C1",
        'test': True,
    }
    transactions_data = {
        "Book_Name": "HARRY POTTER",
        "Contact": 1234,
        'test': True,
    }
    # Check if previous books / users exist to prevent conflicts
    try:
        assert sql_controller("books", 2, book_data,settings) == "All Copies of HARRY POTTER Deleted"
    except:
        print("No previous copies")
    try:
        assert sql_controller("users", 3, user_data,settings) == "KAREN Deleted"
    except:
        print("No previous users")

    # Add books and verify its addition
    assert sql_controller("books", 1, book_data,settings) == "HARRY POTTER added"
    assert sql_controller("books", 3, book_data,settings) == {"Book_Name": "HARRY POTTER", "Copies": 5,"Available": 5,"Location": "R1C1","user_id": None}

    # Add user and verify their addition
    assert sql_controller("users", 1, user_data,settings) == "KAREN added"
    assert sql_controller("users", 4, user_data,settings) == {'User_Name': 'KAREN','Contact': 1234,'Books_Borrowed': None,'Fines':None}

    # Withdraw and verify the effect on the book and the user
    assert sql_controller("transactions", 1, transactions_data,settings) == "HARRY POTTER has been borrowed by KAREN"
    assert sql_controller("books", 3, book_data,settings) == {"Book_Name": "HARRY POTTER", "Copies": 5,"Available": 4,"Location": "R1C1","user_id": ['KAREN',]}
    assert sql_controller("users", 4, user_data,settings) == {'User_Name': 'KAREN','Contact': 1234,'Books_Borrowed': ['HARRY POTTER',],'Fines':None}

    # Return and verify the effect on the book and the user
    assert sql_controller("transactions", 2, transactions_data,settings) == "HARRY POTTER has been returned by KAREN with fine of 0.0"
    assert sql_controller("books", 3, book_data,settings) == {"Book_Name": "HARRY POTTER", "Copies": 5,"Available": 5,"Location": "R1C1","user_id": []}
    assert sql_controller("users", 4, user_data,settings) == {'User_Name': 'KAREN','Contact': 1234,'Books_Borrowed': [],'Fines': 0.0}

    # Finally Delete the book and the user
    assert sql_controller("books", 2, book_data,settings) == "All Copies of HARRY POTTER Deleted"
    assert sql_controller("users", 3, user_data,settings) == "KAREN Deleted"

#pytest test_library.py