import os
import time
from typing import Dict, Any, List

import pytest
import requests


BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://backend:5000")


def wait_for_backend(timeout: float = 30.0) -> None:
    """Wait until the backend health check responds successfully or timeout.

    The docker-compose setup for this task starts MongoDB and the backend in
    separate containers. The tests should not run until the `/api/health`
    endpoint is reachable.
    """

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


def _create_task(title: str, status: str, description: str = "") -> Dict[str, Any]:
    payload = {
        "title": title,
        "status": status,
        "description": description,
    }
    response = requests.post(f"{BACKEND_BASE_URL}/api/tasks", json=payload, timeout=5)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["title"] == title
    assert data["status"] == status
    return data


def _get_tasks(params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    response = requests.get(f"{BACKEND_BASE_URL}/api/tasks", params=params, timeout=5)
    return response


def test_get_tasks_without_status_still_returns_list() -> None:
    """Baseline check: GET /api/tasks without status returns a 200 and a JSON list.

    This verifies that the existing behaviour remains in place even after
    status-based filtering is implemented.
    """

    response = _get_tasks()
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_filter_tasks_by_valid_status_returns_only_matching_tasks() -> None:
    """GET /api/tasks?status=pending should only return tasks with status=pending.

    The current implementation of `getTasks` in `taskController.js` ignores the
    `status` query parameter entirely and always returns all tasks. As a result,
    this test is expected to **fail** until the filtering logic is implemented.
    """

    created_pending = _create_task("Pending task", "pending")
    _create_task("In-progress task", "in-progress")
    _create_task("Completed task", "completed")

    response = _get_tasks({"status": "pending"})
    assert response.status_code == 200

    tasks = response.json()
    assert isinstance(tasks, list)
    assert tasks, "Expected at least one task in the filtered response"

    for task in tasks:
        assert task["status"] == "pending", (
            "All tasks returned when filtering by status=pending must have status 'pending'"
        )

    returned_ids = {task["_id"] for task in tasks}
    assert created_pending["_id"] in returned_ids, "The specifically created pending task must be present"


def test_filter_tasks_with_invalid_status_yields_400() -> None:
    """GET /api/tasks?status=invalid should return a 400 error.

    The tests expect the API to reject any status value that is not one of the
    allowed statuses (`pending`, `in-progress`, `completed`). At the moment, the
    backend does not validate the query parameter, so it will incorrectly
    succeed and return a list, causing this test to fail until fixed.
    """

    response = _get_tasks({"status": "not-a-valid-status"})
    assert response.status_code == 400, (
        "Expected GET /api/tasks with an invalid status to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert "message" in data
    assert "status" in data["message"].lower() or "invalid" in data["message"].lower()
