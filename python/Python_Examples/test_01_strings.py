"""
01. STRING PROGRAMS: the most-asked coding round questions, each with pytest proof.

Run:  python -m pytest python/Python_Examples/test_01_strings.py -v
Tip for the interview: say the time complexity, then mention the edge cases you'd test
(empty string, one char, spaces, case, unicode). That is what makes it a QA LEAD answer.
"""

from collections import Counter

import pytest


# ── 1. Reverse a string ─────────────────────────────────────────────────────────────────────
def reverse_string(text: str) -> str:
    """Slicing: O(n). Interviewers often ask for the manual loop too (see below)."""
    return text[::-1]


def reverse_string_manual(text: str) -> str:
    result = ""
    for ch in text:
        result = ch + result  # prepend each char
    return result


@pytest.mark.parametrize("text, expected", [("qa", "aq"), ("", ""), ("a", "a"), ("Lead QA", "AQ daeL")])
def test_reverse_string(text, expected):
    assert reverse_string(text) == expected
    assert reverse_string_manual(text) == expected


# ── 2. Palindrome (ignore case, spaces and punctuation) ─────────────────────────────────────
def is_palindrome(text: str) -> bool:
    cleaned = [ch.lower() for ch in text if ch.isalnum()]
    return cleaned == cleaned[::-1]


@pytest.mark.parametrize(
    "text, expected",
    [("madam", True), ("Madam", True), ("A man, a plan, a canal: Panama", True), ("qa", False), ("", True)],
)
def test_is_palindrome(text, expected):
    assert is_palindrome(text) is expected


# ── 3. Anagram ──────────────────────────────────────────────────────────────────────────────
def is_anagram(a: str, b: str) -> bool:
    """Counter compares character counts: O(n). sorted(a) == sorted(b) is O(n log n)."""
    normalise = lambda s: Counter(s.replace(" ", "").lower())  # noqa: E731
    return normalise(a) == normalise(b)


@pytest.mark.parametrize("a, b, expected", [("listen", "silent", True), ("Dormitory", "dirty room", True), ("test", "tset", True), ("qa", "qq", False)])
def test_is_anagram(a, b, expected):
    assert is_anagram(a, b) is expected


# ── 4. Character frequency ──────────────────────────────────────────────────────────────────
def char_frequency(text: str) -> dict[str, int]:
    freq: dict[str, int] = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1  # the manual version; Counter(text) does the same
    return freq


def test_char_frequency():
    assert char_frequency("banana") == {"b": 1, "a": 3, "n": 2}
    assert char_frequency("banana") == dict(Counter("banana"))


# ── 5. First non-repeating character ────────────────────────────────────────────────────────
def first_non_repeating(text: str) -> str | None:
    counts = Counter(text)
    return next((ch for ch in text if counts[ch] == 1), None)  # dicts keep insertion order


@pytest.mark.parametrize("text, expected", [("swiss", "w"), ("aabbcc", None), ("automation", "u"), ("", None)])
def test_first_non_repeating(text, expected):
    assert first_non_repeating(text) == expected


# ── 6. Count vowels and consonants ──────────────────────────────────────────────────────────
def count_vowels_consonants(text: str) -> tuple[int, int]:
    vowels = sum(1 for ch in text.lower() if ch in "aeiou")
    letters = sum(1 for ch in text if ch.isalpha())
    return vowels, letters - vowels


def test_count_vowels_consonants():
    assert count_vowels_consonants("Quality Assurance") == (7, 9)
    assert count_vowels_consonants("123 !") == (0, 0)


# ── 7. Reverse the words in a sentence ──────────────────────────────────────────────────────
def reverse_words(sentence: str) -> str:
    return " ".join(reversed(sentence.split()))  # split() with no args also collapses spaces


def test_reverse_words():
    assert reverse_words("I am a QA Lead") == "Lead QA a am I"
    assert reverse_words("  extra   spaces  ") == "spaces extra"


# ── 8. Remove duplicate characters, keep order ──────────────────────────────────────────────
def remove_duplicate_chars(text: str) -> str:
    return "".join(dict.fromkeys(text))  # dict keys are unique AND ordered


def test_remove_duplicate_chars():
    assert remove_duplicate_chars("programming") == "progamin"


# ── 9. Count words (case-insensitive) and find the most common ──────────────────────────────
def most_common_word(text: str) -> tuple[str, int]:
    words = [w.strip(".,!?").lower() for w in text.split()]
    return Counter(words).most_common(1)[0]


def test_most_common_word():
    assert most_common_word("Test early. Test often. test automatically!") == ("test", 3)


# ── 10. String compression (aaabb → a3b2) ───────────────────────────────────────────────────
def compress(text: str) -> str:
    if not text:
        return ""
    out, run_char, run_len = [], text[0], 1
    for ch in text[1:]:
        if ch == run_char:
            run_len += 1
        else:
            out.append(f"{run_char}{run_len}")
            run_char, run_len = ch, 1
    out.append(f"{run_char}{run_len}")
    return "".join(out)


@pytest.mark.parametrize("text, expected", [("aaabbc", "a3b2c1"), ("", ""), ("a", "a1"), ("aabbaa", "a2b2a2")])
def test_compress(text, expected):
    assert compress(text) == expected


# ── 11. Balanced brackets (stack) ───────────────────────────────────────────────────────────
def is_balanced(text: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack


@pytest.mark.parametrize("text, expected", [("{[()]}", True), ('{"a": [1, 2]}', True), ("(]", False), ("((", False), ("", True)])
def test_is_balanced(text, expected):
    assert is_balanced(text) is expected
