# Python Examples: essential practice programs for a QA Lead

Every program comes with pytest tests in the same file, so you can show that it works.

```bash
python -m pytest python/Python_Examples -v
```

| File | Programs |
|------|----------|
| `test_01_strings.py` | reverse, palindrome, anagram, character frequency, first non-repeating, vowels, reverse words, remove duplicates, most common word, compression, balanced brackets |
| `test_02_numbers_and_lists.py` | Fibonacci, prime, factorial, Armstrong, second largest, missing number, duplicates, two sum, move zeros, rotate, binary search, bubble sort, FizzBuzz, float comparison with `pytest.approx` |
| `test_03_collections.py` | merge and deep-merge dicts, flatten list and dict, group results by status, `groupby` trap, sort by key, set comparison, invert a dict, safe nested lookup, chunking, first mismatch |
| `test_04_oop.py` | encapsulation (`BankAccount` with `Decimal`), abstract `BasePage` and inheritance, polymorphism, dataclasses with ordering, `classmethod` and `staticmethod`, stack, LRU cache, singleton |
| `test_05_qa_utilities.py` | log parsing, JSON diff, masking secrets, email validation, CSV and JSON test data, JUnit XML summary, `wait_until` polling, UI sort validation, unique test data, business-day dates, flaky-test detection, URL parsing |

## How to answer a coding question like a QA Lead

1. Repeat the problem back and **ask about edge cases** (empty input, duplicates, case, negatives, very large input).
2. Write the simple, correct version first, then say its **time complexity** (for example O(n) with a set, or O(n log n) with sorting).
3. **Write the tests out loud** with `@pytest.mark.parametrize`, putting the edge cases in their own rows.
4. Mention what you would do in a real framework: type hints, no mutable default arguments, don't mutate the caller's input, and use clear error messages.
