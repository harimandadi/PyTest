pytest -v                 # run all, verbose
pytest -k "name"          # run by name
pytest -m smoke           # run by marker
pytest -x                 # stop at first failure
pytest --lf               # re-run last failures
pytest -s -vv             # debug: prints + full diff
pytest --collect-only -q  # verify which tests will run
pytest -n 4               # parallel (pytest-xdist)

-> -k = keyword, -m = marker, -x = exit on first failure, -s = show prints.
-> --lf = Last Failed, --ff = Failed First.
-> Compare with assert + Python operators: ==, !=, in, is None, pytest.approx, pytest.raises.
Floats: approx. Errors: raises. Everything else: assert.


TestNG / JUnit	                 pytest
assertEquals(a, b)	             assert a == b
assertNotEquals(a, b)	         assert a != b
assertTrue(x) / assertFalse(x)	 assert x / assert not x
assertNull(x)	                 assert x is None
assertTrue(list.contains(v))	 assert v in my_list
assertEquals(0.3, x, 0.0001)	 assert x == pytest.approx(0.3)
assertThrows(Ex.class, ...)	with pytest.raises(Ex):
SoftAssert	plugin pytest-check, or collect errors in a list and assert once



Scope	Created	Destroyed	In this practice	Real-world use
function (default)	Before each test	After each test	3 tests → 3 carts	Fresh test data, a new page, anything tests change
class	Once per test class	After the last test in the class	2 classes → 2 logins	Log in once for a group of related tests
module	Once per file	After the last test in the file	3 tests → 1 DB connection	DB connection, seeding a table for one file
session	Once per pytest run	After the very last test	2 files → 1 browser	Browser launch, config, auth token, mock server

“F-C-M-S: Function → Class → Module → Session = smallest box → biggest box.”

Function = a new plate for every meal.
Class = one table per family.
Module = one kitchen per restaurant floor.
Session = one restaurant open for the whole day.