import os
import time
from typing import Dict, Any, List

import pytest
import requests


BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://backend:5000")


def wait_for_backend(timeout: float = 30.0) -> None:
    """Wait until the backend health check responds successfully or timeout."""

    deadline = time.time() + timeout
    url = f"{BACKEND_BASE_URL}/api/health"
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return
        except Exception as exc:  # noqa: BLE001 - broad by design for simple retry loop
            last_error = exc

        time.sleep(1)

    raise RuntimeError(f"Backend did not become healthy in time: {last_error}")


@pytest.fixture(scope="session", autouse=True)
def _ensure_backend_ready() -> None:
    """Session-level fixture to ensure the backend is ready before tests run."""

    wait_for_backend()


def _get_all_tasks() -> List[Dict[str, Any]]:
    response = requests.get(f"{BACKEND_BASE_URL}/api/tasks", timeout=5)
    assert response.status_code == 200, response.text
    return response.json()


def _post_bulk(tasks: List[Dict[str, Any]]) -> requests.Response:
    payload = {"tasks": tasks}
    return requests.post(f"{BACKEND_BASE_URL}/api/tasks/bulk", json=payload, timeout=10)


def test_bulk_create_success_creates_all_tasks() -> None:
    """A valid bulk request should create all tasks and return 201.

    Initially this test will fail with a 404 because /api/tasks/bulk does not
    exist yet. Once the endpoint is implemented, the test expects a 201
    response and an array of created task documents.
    """

    tasks_to_create = [
        {"title": "Bulk Task A", "description": "One", "status": "pending"},
        {"title": "Bulk Task B", "description": "Two", "status": "in-progress"},
        {"title": "Bulk Task C", "description": "Three", "status": "completed"},
    ]

    response = _post_bulk(tasks_to_create)
    assert response.status_code == 201, (
        "Expected POST /api/tasks/bulk to return 201 for a valid request. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(tasks_to_create)

    # Make sure titles and statuses round-trip correctly.
    returned_titles = [t["title"] for t in data]
    for t in tasks_to_create:
        assert t["title"] in returned_titles


def test_bulk_create_rejects_invalid_status_and_persists_nothing() -> None:
    """If any task has an invalid status, the whole batch should be rejected."""

    # Capture the current number of tasks so we can verify that it does not
    # change if the bulk request is rejected.
    before_tasks = _get_all_tasks()
    before_count = len(before_tasks)

    tasks_to_create = [
        {"title": "Okay Task", "status": "pending"},
        {"title": "Bad Task", "status": "not-a-real-status"},
    ]

    response = _post_bulk(tasks_to_create)
    assert response.status_code == 400, (
        "Expected POST /api/tasks/bulk with an invalid status to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert "message" in data

    after_tasks = _get_all_tasks()
    after_count = len(after_tasks)

    # No new tasks should have been inserted.
    assert after_count == before_count


def test_bulk_create_rejects_too_many_tasks() -> None:
    """A payload with more than 50 tasks should be rejected with 400."""

    big_list = [
        {"title": f"Task {i}", "status": "pending"}
        for i in range(60)
    ]

    response = _post_bulk(big_list)
    assert response.status_code == 400, (
        "Expected POST /api/tasks/bulk with more than 50 tasks to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert "message" in data
