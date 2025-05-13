from library import sql_controller
import json


def test_sql_controller(): 

    with open("config.json", "r") as config_file:
        settings = json.load(config_file)

    # To test users  
    user_test_data = {
        "User_Name": "KAREN",
        "Contact": 1234,
        'test': True,
    }
    try:
        # Delete data if previous copies exist
        assert sql_controller("users", 3, user_test_data,settings) == "KAREN Deleted"
    except:
        print("No previous copies")
    finally:
        # Test all operations
        assert sql_controller("users", 1, user_test_data,settings) == "KAREN added"
        assert sql_controller("users", 2, user_test_data,settings) == "KAREN updated"
        assert sql_controller("users", 4, user_test_data,settings) == {'User_Name': 'KAREN','Contact': 1234,'Books_Borrowed': None,'Fines':None}
        assert sql_controller("users", 3, user_test_data,settings) == "KAREN Deleted"

    # To test books 
    book_test_data = {
        "Book_Name": "HARRY POTTER",
        "Author_Name": "JK Rowling",
        "Copies":5,
        "Available": 0,
        "Location":"R1C1",
        'test': True,
    }
    
    try:
        # Delete data if previous copies exist
        assert sql_controller("books", 2, book_test_data,settings) == "All Copies of HARRY POTTER Deleted"
    except:
        print("No previous copies")
    finally:
        # Test all operations
        assert sql_controller("books", 1, book_test_data,settings) == "HARRY POTTER added"
        assert sql_controller("books", 3, book_test_data,settings) == {"Book_Name": "HARRY POTTER", "Copies": 5,"Available": 5,"Location": "R1C1","user_id": None}
        assert sql_controller("books", 2, book_test_data,settings) == "All Copies of HARRY POTTER Deleted"


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
    # Check if previous books / users exist to prevent conflicts
    try:
        assert sql_controller("books", 2, book_test_data,settings) == "All Copies of HARRY POTTER Deleted"
    except:
        print("No previous copies")
    try:
        assert sql_controller("users", 3, user_test_data,settings) == "KAREN Deleted"
    except:
        print("No previous books")

    # Add books and verify its addition
    assert sql_controller("books", 1, book_test_data,settings) == "HARRY POTTER added"
    assert sql_controller("books", 3, book_test_data,settings) == {"Book_Name": "HARRY POTTER", "Copies": 5,"Available": 5,"Location": "R1C1","user_id": None}

    # Add user and verify their addition
    assert sql_controller("users", 1, user_test_data,settings) == "KAREN added"
    assert sql_controller("users", 4, user_test_data,settings) == {'User_Name': 'KAREN','Contact': 1234,'Books_Borrowed': None,'Fines':None}

#pytest test_library.py