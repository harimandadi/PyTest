class TestThird:

    def test_third(self):
        assert "hello" == "hello"
        assert "hari" in "Hyderabad"
        print ("the third test passed")

    def test_first(self):
     assert 1 + 1 == 2
     print ("the first test passed")
     users = ["hari", "sai", "kumar"]
     assert "hari" in users
     users1 = {"hari": 1, "sai": 2, "kumar": 3}
     users2= {"hari": 1, "sai": 2, "kumar": 3}
     assert users1 == users2