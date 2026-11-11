# python/: Python + pytest interview prep

| Item | What it is |
|------|------------|
| `Python-Pytest-Essentials.pdf` | The full guide as a PDF, with clickable bookmarks for each section |
| `test_python_pytest_essentials.py` | The guide as a runnable file: 13 sections plus 20 self-test questions, where every claim is a test |
| `conftest.py`, `framework.py` | The fixtures and the small offline "framework" that the guide uses (layers 2 to 4) |
| `Python_Examples/Concepts/` | 15 Python concept lessons from basic to advanced, with memory hooks and a cheat sheet |
| `Python_Examples/` | Essential practice programs for a QA Lead (strings, numbers, collections, OOP, QA utilities) |

```bash
py -3.15 -m venv python/.venv
```
```bash
python/.venv/Scripts/python -m pip install -r python/requirements.txt
```
```bash
python/.venv/Scripts/python -m pytest python
```

Useful variations: `-m smoke`, `--env prod` (tests that create data are skipped), and `--setup-show -k end_to_end`.
