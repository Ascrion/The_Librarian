from library import sql_controller

# pytest test_library.py
def test_sql_controller(): 

    # To test users  
    test_data = {
        "User_Name": "KAREN",
        "Contact": 1234,
        'test': True,
    }
    assert sql_controller("users", 1, test_data) == "KAREN added"
    assert sql_controller("users", 2, test_data) == "KAREN updated"
    assert sql_controller("users", 4, test_data) == "KAREN"
    assert sql_controller("users", 3, test_data) == "KAREN Deleted"