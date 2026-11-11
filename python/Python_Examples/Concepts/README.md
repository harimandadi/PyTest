# Python Concepts: basic to advanced, with memory hooks

Each file teaches one topic in the same way:

- a **BIG HOOK** at the top, one line to remember the whole idea;
- a **HOOK** for every section;
- small code examples with comments on almost every line;
- **pytest tests** that prove each claim;
- a **SELF-CHECK** at the end, with questions and answers.

```bash
python -m pytest python/Python_Examples/Concepts -v
```
```bash
python -m pytest python/Python_Examples/Concepts/test_c07_exceptions.py -v
```

## Learning path

| # | Level | File | Big hook |
|---|-------|------|----------|
| C01 | Basic | `test_c01_variables_and_types.py` | A variable is a **name tag**, not a box |
| C02 | Basic | `test_c02_strings.py` | `[start:stop:step]`: start is IN, stop is OUT |
| C03 | Basic | `test_c03_control_flow.py` | Indentation IS the block |
| C04 | Basic → Intermediate | `test_c04_functions.py` | A function is a recipe; no return gives you None |
| C05 | Basic → Intermediate | `test_c05_data_structures.py` | List = shopping list, Tuple = GPS, Set = guest list, Dict = phone book |
| C06 | Intermediate | `test_c06_comprehensions_iterators.py` | `[WHAT for ITEM in WHERE if FILTER]` |
| C07 | Intermediate | `test_c07_exceptions.py` | T-E-E-F: Try, Except, Else, Finally |
| C08 | Intermediate | `test_c08_files_modules.py` | `with` = the door closes behind you |
| C09 | Intermediate | `test_c09_oop.py` | Class = cookie cutter, object = cookie, self = THIS cookie |
| C10 | Intermediate → Advanced | `test_c10_dataclasses_enums_typing.py` | Dataclasses write the boring parts; hints are labels, not locks |
| C11 | Advanced | `test_c11_closures_decorators.py` | A decorator is gift wrap |
| C12 | Advanced | `test_c12_context_managers_generators.py` | `with` = a hotel stay (check-in, stay, check-out) |
| C13 | Advanced | `test_c13_concurrency.py` | Threads for waiting, processes for thinking |
| C14 | Advanced | `test_c14_internals_and_performance.py` | Everything is an object with a type, an id and a refcount |
| C15 | Advanced | `test_c15_mocking_and_test_doubles.py` | Patch where it's USED, not where it's defined |

## Memory hooks cheat sheet (revise these the night before an interview)

| Topic | Hook |
|-------|------|
| Names | Two tags, one balloon: `y = x` doesn't copy |
| Mutability | **LDS** can change (List, Dict, Set); everything else is frozen |
| Input data | Convert at the door: UI text, environment variables and CSV values are always strings |
| Truthiness | Empty and zero are False; `bool("False")` is True |
| None | "No value yet"; test it with `is None` |
| Slicing | Negative counts from the end; slicing never raises, indexing does |
| Strings | Methods return NEW strings; collect in a list and join once |
| if / elif | The first True wins |
| and / or | `or` stops at the first truthy value, `and` at the first falsy value |
| Loop-else | `else` means "no break happened" |
| match | A switch with X-ray vision: it matches the shape of the data |
| Functions | print SHOWS, return GIVES |
| Defaults | Defaults are baked ONCE, so never use `=[]` |
| `*` and `**` | `*` packs a tuple, `**` packs a dict; in a call they unpack |
| Scope | LEGB: Local, Enclosing, Global, Built-in |
| Dict access | `[]` DEMANDS the key, `.get()` politely asks |
| Sets | `|` all, `&` both, `-` only mine, `^` not shared |
| Copying | A shallow copy copies the box; a deep copy copies everything inside |
| Iterators | Iterable = the book, iterator = the bookmark (used up after one pass) |
| Generators | `return` answers once; `yield` answers, pauses, and continues |
| any / all | `all([])` is True |
| itertools | chain JOINS, product COMBINES, groupby needs SORTED input |
| Exceptions | Name the problem: TypeError, ValueError, KeyError, IndexError, AttributeError |
| `raise ... from` | The paper trail: the new error keeps its cause |
| EAFP | Easier to Ask Forgiveness than Permission |
| Files | Modes: r, w (WIPES first), a, x, b. Always pass `encoding="utf-8"` |
| JSON | **s** = string: `loads`/`dumps`; no s = file: `load`/`dump` |
| Imports | A module is imported once and then cached |
| OOP | A PIE: Abstraction, Polymorphism, Inheritance, Encapsulation |
| Inheritance | `super()` calls the parent's version; HAS-A beats IS-A |
| Dunders | Dunders plug your class into Python's syntax |
| MRO | Left to right, children before parents |
| Dataclass | Fields in, free methods out; `frozen` = a laminated card |
| Enum | A dropdown in code: typos fail immediately |
| Closures | A function with a backpack |
| Decorators | Gift wrap. `@d` means `f = d(f)`; arguments need one more layer |
| Stacked decorators | The one closest to the function wraps first |
| Context managers | Before `yield` = enter, after `yield` = exit, inside try/finally |
| Concurrency | Threads for waiting, processes for thinking, asyncio for lots of waiting |
| Races | Shared + mutable + threads = a race; a Lock lets one person in the room at a time |
| Hashing | A dict is a warehouse, and `hash(key)` picks the shelf |
| Big-O | `in` on a dict or set is O(1); on a list it is O(n) |
| Mocking | Patch where it's used. `return_value` = what it SAYS, `assert_called_*` = what it HEARD |
| Test doubles | Dummy = placeholder, Stub = answers, Fake = working toy, Spy = recorder, Mock = recorder you question |
