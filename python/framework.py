"""
A tiny, OFFLINE Python mirror of the TypeScript framework's lower layers (layers 3 and 4).

The prep guide (test_python_pytest_essentials.py) and conftest.py use it so every example
really runs under pytest, without a browser or network:

    test_python_pytest_essentials.py   LAYER 1  WHAT     (specs: business expectations only)
    conftest.py                        LAYER 2  WIRING   (fixtures = dependency injection)
    framework.py  (this file)          LAYER 3  HOW      (ApiClient, services, assertions)
                                       LAYER 4  WHERE    (environments, schemas, test data)

TypeScript original → Python equivalent used here
    api/automation-exercise/ApiClient.ts           → ApiClient
    api/automation-exercise/services/*Api.ts       → ProductsApi, AccountApi, AuthApi
    api/automation-exercise/schemas.ts (zod)       → pydantic models
    api/automation-exercise/assertions.ts          → expect_schema, expect_api_code
    api/automation-exercise/test-data/userBuilder  → build_user, UserBuilder
    config/environments.ts                         → ENVIRONMENTS, get_environment
"""

from __future__ import annotations

import itertools
import uuid
from dataclasses import asdict, dataclass, field, replace
from typing import Any, Literal, TypeVar

from pydantic import BaseModel, ValidationError

# ── LAYER 4: WHERE ─────────────────────────────────────────────────────────────────────────────
# STRATEGY pattern: one config object per environment; TEST_ENV / --env picks one at runtime.

EnvironmentName = Literal["local", "qa", "staging", "prod"]
PARABANK_URL = "https://parabank.parasoft.com/parabank"


@dataclass(frozen=True)  # frozen = read-only, like `as const`/readonly in TS → safe to share
class EnvironmentConfig:
    name: EnvironmentName
    base_url: str
    allow_data_changes: bool  # safety rule: prod must never create or delete data
    workers: int


ENVIRONMENTS: dict[str, EnvironmentConfig] = {
    "local": EnvironmentConfig("local", "http://127.0.0.1:8080", True, 4),
    "qa": EnvironmentConfig("qa", PARABANK_URL, True, 2),
    "staging": EnvironmentConfig("staging", PARABANK_URL, True, 2),
    "prod": EnvironmentConfig("prod", PARABANK_URL, False, 2),
}


def get_environment(name: str) -> EnvironmentConfig:
    """Fail fast with a helpful message instead of a KeyError deep inside a test."""
    try:
        return ENVIRONMENTS[name]
    except KeyError:
        raise ValueError(f"Unknown environment {name!r}. Use one of: {', '.join(ENVIRONMENTS)}") from None


# ── LAYER 4: SCHEMAS (pydantic = zod) ──────────────────────────────────────────────────────────


class ApiMessage(BaseModel):
    responseCode: int
    message: str


class Product(BaseModel):
    id: int
    name: str
    price: str  # the real API returns "Rs. 500" (a string), so the schema says str


class ProductsList(BaseModel):
    responseCode: int
    products: list[Product]


M = TypeVar("M", bound=BaseModel)  # generic: "any pydantic model" (TS: <T> with ZodType<T>)


def expect_schema(model: type[M], body: Any, schema_name: str | None = None) -> M:
    """TS expectSchema<T>: validate a raw body and return it typed as exactly `model`."""
    try:
        return model.model_validate(body)
    except ValidationError as error:
        details = "\n".join(
            f"  • {'.'.join(str(p) for p in issue['loc']) or '(root)'}: {issue['msg']}"
            for issue in error.errors()
        )
        raise AssertionError(f"Response does not match {schema_name or model.__name__} schema:\n{details}") from None


# ── LAYER 4: TEST DATA (Builder) ───────────────────────────────────────────────────────────────

_counter = itertools.count(1)


def unique_id() -> str:
    """Unique across parallel xdist workers too: uuid part differs per process."""
    return f"{next(_counter)}{uuid.uuid4().hex[:6]}"


@dataclass(frozen=True)
class NewUser:
    name: str
    email: str
    password: str
    title: str = "Mr"
    city: str = "Pune"
    country: str = "India"


def build_user(**overrides: Any) -> NewUser:
    """Valid by default; a test overrides only what it is about. TS: buildUser(overrides)."""
    uid = unique_id()
    defaults = NewUser(name=f"QA User {uid}", email=f"qa.api.{uid}@example.com", password=f"Pw_{uid}!")
    return replace(defaults, **overrides)  # replace() = { ...defaults, ...overrides }, still frozen


@dataclass
class UserBuilder:
    """FLUENT builder (the class version interviewers ask for)."""

    _role: Literal["admin", "user"] = "user"
    _overrides: dict[str, Any] = field(default_factory=dict)  # NOT `= {}`: mutable default trap

    def with_role(self, role: Literal["admin", "user"]) -> UserBuilder:
        self._role = role
        return self  # returning self allows chaining

    def with_email(self, email: str) -> UserBuilder:
        self._overrides["email"] = email
        return self

    def build(self) -> dict[str, Any]:
        return {**asdict(build_user(**self._overrides)), "role": self._role}  # a fresh dict each time


# ── LAYER 3: HOW (an in-memory fake server + client + services) ────────────────────────────────


class FakeAutomationExerciseServer:
    """Stands in for automationexercise.com. Quirk kept on purpose: ALWAYS HTTP 200."""

    def __init__(self) -> None:
        self.users: dict[str, NewUser] = {}
        self.products = [
            {"id": 1, "name": "Blue Top", "price": "Rs. 500"},
            {"id": 2, "name": "Men Tshirt", "price": "Rs. 400"},
            {"id": 3, "name": "Sleeveless Dress", "price": "Rs. 1000"},
        ]
        self.request_count = 0

    def handle(self, method: str, path: str, form: dict[str, str] | None) -> tuple[int, dict[str, Any]]:
        self.request_count += 1
        form = form or {}
        if (method, path) == ("GET", "productsList"):
            return 200, {"responseCode": 200, "products": self.products}
        if (method, path) == ("POST", "searchProduct"):
            if "search_product" not in form:
                return 200, {"responseCode": 400, "message": "Bad request, search_product parameter is missing in POST request."}
            term = form["search_product"].lower()
            return 200, {"responseCode": 200, "products": [p for p in self.products if term in p["name"].lower()]}
        if (method, path) == ("POST", "createAccount"):
            if form["email"] in self.users:
                return 200, {"responseCode": 400, "message": "Email already exists!"}
            self.users[form["email"]] = NewUser(**{k: form[k] for k in ("name", "email", "password")})
            return 200, {"responseCode": 201, "message": "User created!"}
        if (method, path) == ("DELETE", "deleteAccount"):
            if self.users.pop(form["email"], None) is None:
                return 200, {"responseCode": 404, "message": "Account not found!"}
            return 200, {"responseCode": 200, "message": "Account deleted!"}
        if (method, path) == ("POST", "verifyLogin"):
            user = self.users.get(form.get("email", ""))
            if user and user.password == form.get("password"):
                return 200, {"responseCode": 200, "message": "User exists!"}
            return 200, {"responseCode": 404, "message": "User not found!"}
        return 200, {"responseCode": 405, "message": "This request method is not supported."}


@dataclass(frozen=True)
class ApiResult:
    http_status: int
    body: Any


class ApiClient:
    """The ONE place that does 'HTTP'. With real HTTP this would wrap a requests.Session."""

    def __init__(self, server: FakeAutomationExerciseServer) -> None:
        self._server = server

    def send(self, method: str, path: str, form: dict[str, str] | None = None) -> ApiResult:
        status, body = self._server.handle(method, path, form)
        return ApiResult(status, body)


class ProductsApi:  # FACADE: tests say "search", the service knows method, path, form encoding
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def list(self) -> ApiResult:
        return self.client.send("GET", "productsList")

    def search(self, term: str | None) -> ApiResult:
        form = None if term is None else {"search_product": term}  # None → omit the parameter
        return self.client.send("POST", "searchProduct", form)


class AccountApi:
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def create(self, user: NewUser) -> ApiResult:
        return self.client.send("POST", "createAccount", asdict(user))

    def delete(self, email: str, password: str) -> ApiResult:
        return self.client.send("DELETE", "deleteAccount", {"email": email, "password": password})


class AuthApi:
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def verify_login(self, email: str, password: str) -> ApiResult:
        return self.client.send("POST", "verifyLogin", {"email": email, "password": password})


def expect_api_code(result: ApiResult, response_code: int, message: str | None = None) -> ApiMessage:
    """ADAPTER: this API always says HTTP 200, the real result is in the body."""
    assert result.http_status == 200, f"expected HTTP 200, got {result.http_status}"
    body = expect_schema(ApiMessage, result.body)
    assert body.responseCode == response_code, f"responseCode {body.responseCode} ({body.message!r}), expected {response_code}"
    if message is not None:
        assert body.message == message
    return body
