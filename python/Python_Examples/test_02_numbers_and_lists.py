"""
02. NUMBERS AND LISTS: classic logic programs, each with pytest proof.

Run:  python -m pytest python/Python_Examples/test_02_numbers_and_lists.py -v
"""

import math

import pytest


# ── 1. Fibonacci (iterative, O(n)) ──────────────────────────────────────────────────────────
def fibonacci(n: int) -> list[int]:
    seq, a, b = [], 0, 1
    for _ in range(n):
        seq.append(a)
        a, b = b, a + b  # tuple swap, no temp variable
    return seq


def test_fibonacci():
    assert fibonacci(8) == [0, 1, 1, 2, 3, 5, 8, 13]
    assert fibonacci(0) == []


# ── 2. Prime check (only up to √n) ──────────────────────────────────────────────────────────
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    return all(n % d for d in range(2, math.isqrt(n) + 1))


@pytest.mark.parametrize("n, expected", [(2, True), (17, True), (1, False), (0, False), (21, False), (97, True)])
def test_is_prime(n, expected):
    assert is_prime(n) is expected


# ── 3. Factorial (iterative and recursive) ──────────────────────────────────────────────────
def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("factorial is undefined for negative numbers")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def factorial_recursive(n: int) -> int:
    return 1 if n <= 1 else n * factorial_recursive(n - 1)


def test_factorial():
    assert factorial(5) == factorial_recursive(5) == 120
    assert factorial(0) == 1
    with pytest.raises(ValueError, match="negative"):
        factorial(-1)


# ── 4. Armstrong number (153 = 1³ + 5³ + 3³) ────────────────────────────────────────────────
def is_armstrong(n: int) -> bool:
    digits = str(n)
    return n == sum(int(d) ** len(digits) for d in digits)


@pytest.mark.parametrize("n, expected", [(153, True), (370, True), (9474, True), (123, False)])
def test_is_armstrong(n, expected):
    assert is_armstrong(n) is expected


# ── 5. Largest and second largest WITHOUT sorting (one pass) ───────────────────────────────
def second_largest(nums: list[int]) -> int | None:
    first = second = None
    for n in nums:
        if first is None or n > first:
            first, second = n, first
        elif n != first and (second is None or n > second):
            second = n
    return second


@pytest.mark.parametrize("nums, expected", [([10, 5, 20, 8], 10), ([5, 5, 5], None), ([1], None), ([-1, -5, -3], -3), ([20, 20, 10], 10)])
def test_second_largest(nums, expected):
    assert second_largest(nums) == expected


# ── 6. Missing number in 1..n ───────────────────────────────────────────────────────────────
def missing_number(nums: list[int], n: int) -> int:
    return n * (n + 1) // 2 - sum(nums)  # expected sum − actual sum, O(n)


def test_missing_number():
    assert missing_number([1, 2, 4, 5, 6], 6) == 3


# ── 7. Find duplicates ──────────────────────────────────────────────────────────────────────
def find_duplicates(items: list) -> list:
    seen, dups = set(), []
    for item in items:
        if item in seen and item not in dups:
            dups.append(item)
        seen.add(item)
    return dups


def test_find_duplicates():
    assert find_duplicates([1, 2, 3, 2, 4, 1, 2]) == [2, 1]
    assert find_duplicates(["TC-1", "TC-2", "TC-1"]) == ["TC-1"]  # duplicate test-case ids


# ── 8. Two sum (hash map, O(n)) ─────────────────────────────────────────────────────────────
def two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    index_of: dict[int, int] = {}
    for i, n in enumerate(nums):
        if target - n in index_of:
            return index_of[target - n], i
        index_of[n] = i
    return None


def test_two_sum():
    assert two_sum([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum([1, 2], 10) is None


# ── 9. Move zeros to the end, keep order ────────────────────────────────────────────────────
def move_zeros(nums: list[int]) -> list[int]:
    non_zero = [n for n in nums if n != 0]
    return non_zero + [0] * (len(nums) - len(non_zero))


def test_move_zeros():
    assert move_zeros([0, 1, 0, 3, 12]) == [1, 3, 12, 0, 0]


# ── 10. Rotate a list by k ──────────────────────────────────────────────────────────────────
def rotate(nums: list[int], k: int) -> list[int]:
    if not nums:
        return []
    k %= len(nums)  # k larger than the list still works
    return nums[-k:] + nums[:-k] if k else nums[:]


@pytest.mark.parametrize("k, expected", [(2, [4, 5, 1, 2, 3]), (0, [1, 2, 3, 4, 5]), (7, [4, 5, 1, 2, 3])])
def test_rotate(k, expected):
    assert rotate([1, 2, 3, 4, 5], k) == expected


# ── 11. Binary search (on sorted data) ──────────────────────────────────────────────────────
def binary_search(sorted_nums: list[int], target: int) -> int:
    lo, hi = 0, len(sorted_nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if sorted_nums[mid] == target:
            return mid
        if sorted_nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


@pytest.mark.parametrize("target, expected", [(7, 3), (1, 0), (11, 5), (4, -1)])
def test_binary_search(target, expected):
    assert binary_search([1, 3, 5, 7, 9, 11], target) == expected


# ── 12. Bubble sort (know it, never ship it) ────────────────────────────────────────────────
def bubble_sort(nums: list[int]) -> list[int]:
    data = nums[:]  # don't mutate the caller's list
    for end in range(len(data) - 1, 0, -1):
        swapped = False
        for i in range(end):
            if data[i] > data[i + 1]:
                data[i], data[i + 1] = data[i + 1], data[i]
                swapped = True
        if not swapped:  # already sorted → O(n) best case
            break
    return data


def test_bubble_sort():
    original = [5, 1, 4, 2, 8]
    assert bubble_sort(original) == sorted(original) == [1, 2, 4, 5, 8]
    assert original == [5, 1, 4, 2, 8]  # input untouched


# ── 13. FizzBuzz ────────────────────────────────────────────────────────────────────────────
def fizzbuzz(n: int) -> list[str]:
    return ["FizzBuzz" if i % 15 == 0 else "Fizz" if i % 3 == 0 else "Buzz" if i % 5 == 0 else str(i) for i in range(1, n + 1)]


def test_fizzbuzz():
    assert fizzbuzz(15)[-1] == "FizzBuzz"
    assert fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]


# ── 14. Floating point: why tests use pytest.approx ─────────────────────────────────────────
def test_float_comparison():
    assert 0.1 + 0.2 != 0.3  # binary floating point!
    assert 0.1 + 0.2 == pytest.approx(0.3)
    balance = 100.10 - 0.10
    assert balance == pytest.approx(100.0)  # money in real code: decimal.Decimal
