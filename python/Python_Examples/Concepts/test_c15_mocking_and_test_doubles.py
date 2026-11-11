"""
C15 · ADVANCED · MOCKING AND TEST DOUBLES (unittest.mock + pytest monkeypatch)
═══════════════════════════════════════════════════════════════════════════════════════════════
BIG HOOK  "Patch where it's USED, not where it's DEFINED."
          If notifier.py does `from requests import post`, you patch "notifier.post",
          not "requests.post". The name is looked up in the module that uses it.

Test doubles, by HOOK:
  Dummy  "a placeholder"        passed but never used
  Stub   "a puppet that ANSWERS"  returns canned data (return_value)
  Fake   "a working toy"        real logic, simplified (an in-memory DB)
  Spy    "a recorder"           real behaviour + remembers calls (wraps=)
  Mock   "a recorder you QUESTION"  you assert HOW it was called

Run:  python -m pytest python/Python_Examples/Concepts/test_c15_mocking_and_test_doubles.py -v
"""

import time
from unittest.mock import MagicMock, Mock, call, patch

import pytest


# ── CODE UNDER TEST ─────────────────────────────────────────────────────────────────────────
class SlackClient:
    def post(self, channel: str, text: str) -> dict:
        raise RuntimeError("real network call: must not run in unit tests")


class RunNotifier:
    def __init__(self, slack: SlackClient) -> None:  # dependency INJECTED → easy to replace
        self.slack = slack

    def notify(self, passed: int, failed: int) -> bool:
        if failed == 0:
            return False  # no message for green runs
        response = self.slack.post("#qa-alerts", f"{failed} failed, {passed} passed")
        return response.get("ok", False)


def wait_for_job(get_status, timeout_s: float = 5) -> str:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        status = get_status()
        if status in ("done", "error"):
            return status
        time.sleep(1)
    raise TimeoutError


# ── 1. STUB + MOCK: control the answer, check the call ──────────────────────────────────────
# HOOK  "return_value = what it SAYS; assert_called_* = what it HEARD."
def test_mock_answers_and_records():
    slack = Mock(spec=SlackClient)  # spec: only real SlackClient methods exist (typo-safe)
    slack.post.return_value = {"ok": True}
    assert RunNotifier(slack).notify(passed=47, failed=3) is True
    slack.post.assert_called_once_with("#qa-alerts", "3 failed, 47 passed")


def test_mock_not_called_for_green_runs():
    slack = Mock(spec=SlackClient)
    RunNotifier(slack).notify(passed=50, failed=0)
    slack.post.assert_not_called()


def test_spec_catches_typos():
    slack = Mock(spec=SlackClient)
    with pytest.raises(AttributeError):
        slack.pots("#x", "typo")  # without spec this would silently "work"


# ── 2. side_effect: SEQUENCES AND ERRORS ────────────────────────────────────────────────────
# HOOK  "side_effect = a SCRIPT": a list plays one answer per call; an exception is RAISED.
def test_side_effect_sequence_and_errors():
    status = Mock(side_effect=["queued", "running", "done"])
    with patch("time.sleep") as fake_sleep:  # don't really wait 2 seconds
        assert wait_for_job(status) == "done"
    assert status.call_count == 3 and fake_sleep.call_count == 2

    slack = Mock(spec=SlackClient)
    slack.post.side_effect = ConnectionError("Slack down")
    with pytest.raises(ConnectionError):
        RunNotifier(slack).notify(1, 1)


# ── 3. patch(): REPLACE A NAME FOR ONE TEST ─────────────────────────────────────────────────
# HOOK  "patch = a temporary costume": on for the with-block/test, off afterwards automatically.
def test_patch_object_method():
    with patch.object(SlackClient, "post", return_value={"ok": True}) as fake_post:
        assert RunNotifier(SlackClient()).notify(1, 2) is True
    fake_post.assert_called_once()
    with pytest.raises(RuntimeError):
        SlackClient().post("#x", "y")  # costume removed: the real method is back


# This module does `import time` and calls time.monotonic() → the lookup happens on the `time`
# module at call time, so "time.monotonic" is the right target. Had it done
# `from time import monotonic`, the target would be f"{__name__}.monotonic" (where it's USED).
@patch("time.monotonic")
def test_patch_as_decorator(fake_monotonic):
    fake_monotonic.side_effect = [0, 0, 10]  # deadline set at 0, loop check at 0, then 10 s later
    with patch("time.sleep"):
        with pytest.raises(TimeoutError):
            wait_for_job(lambda: "running", timeout_s=5)


# ── 4. MagicMock AND CALL HISTORY ───────────────────────────────────────────────────────────
# HOOK  "MagicMock also fakes the DUNDERS": len(), with, iteration, [ ]…
def test_magicmock_and_call_list():
    conn = MagicMock()
    conn.__enter__.return_value = conn  # usable in `with`
    conn.query.return_value = [{"id": 1}]
    with conn as c:
        c.query("SELECT 1")
        c.query("SELECT 2")
    assert conn.query.call_args_list == [call("SELECT 1"), call("SELECT 2")]
    assert conn.__exit__.called


# ── 5. SPY: REAL BEHAVIOUR + RECORDING ──────────────────────────────────────────────────────
def test_spy_with_wraps():
    def real_discount(price: float) -> float:
        return round(price * 0.9, 2)

    spy = Mock(wraps=real_discount)
    assert spy(100) == 90.0  # real logic ran
    spy.assert_called_once_with(100)


# ── 6. FAKE: A SIMPLE WORKING STAND-IN ──────────────────────────────────────────────────────
# HOOK  "Prefer a fake over a mountain of mocks": less coupling to call details.
class FakeSlack:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def post(self, channel: str, text: str) -> dict:
        self.messages.append((channel, text))
        return {"ok": True}


def test_fake():
    fake = FakeSlack()
    RunNotifier(fake).notify(9, 1)  # type: ignore[arg-type]  duck typing
    assert fake.messages == [("#qa-alerts", "1 failed, 9 passed")]


# ── 7. pytest monkeypatch: THE PYTEST WAY ───────────────────────────────────────────────────
# HOOK  "monkeypatch = patch with automatic undo, as a fixture."
def test_monkeypatch(monkeypatch):
    monkeypatch.setattr(SlackClient, "post", lambda self, ch, txt: {"ok": True})
    monkeypatch.setenv("SLACK_CHANNEL", "#qa-alerts")
    assert RunNotifier(SlackClient()).notify(0, 5) is True


"""
 WHEN NOT TO MOCK
   • Don't mock what you own and can run fast (use the real class or a fake).
   • Don't mock the thing under test.
   • Mocks that assert every internal call make refactoring painful: assert OUTCOMES first,
     interactions only when the interaction IS the requirement (e.g. "alert is sent").
   • UI/API end-to-end tests shouldn't mock the system; mock 3rd parties (payment, SMS) instead,
     e.g. Playwright's page.route() for network mocking.

SELF-CHECK
  1. Module a.py does `from b import f`. Patch which name?   → "a.f"
  2. Mock vs stub?                                          → stub answers; mock is also verified
  3. side_effect=[1, 2] vs side_effect=ValueError?          → answers in turn vs raises
  4. Why spec=?                                             → typos on the mock fail loudly
  5. Fake vs mock?                                          → working simplified logic vs recorder
"""
