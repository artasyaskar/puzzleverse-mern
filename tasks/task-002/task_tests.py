import os
import time
from typing import Dict, Any

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


def _create_task(title: str, status: str, description: str = "") -> Dict[str, Any]:
    payload = {
        "title": title,
        "status": status,
        "description": description,
    }
    response = requests.post(f"{BACKEND_BASE_URL}/api/tasks", json=payload, timeout=5)
    assert response.status_code == 201, response.text
    return response.json()


def _get_stats() -> requests.Response:
    return requests.get(f"{BACKEND_BASE_URL}/api/tasks/stats", timeout=5)


def test_stats_endpoint_exists_and_returns_zero_counts_initially() -> None:
    """GET /api/tasks/stats should return a 200 and zero counts when empty.

    With a fresh database that has no tasks, the stats endpoint is expected to
    return a payload with total=0 and all known statuses present in the
    byStatus object, each with a value of 0.

    At the time this task is introduced, the `/api/tasks/stats` route does not
    exist, so this test will initially fail with a 404 response until the
    endpoint is implemented.
    """

    response = _get_stats()
    assert response.status_code == 200, (
        "Expected GET /api/tasks/stats to return 200 once implemented. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert set(data.keys()) == {"total", "byStatus"}
    assert data["total"] == 0

    by_status = data["byStatus"]
    assert isinstance(by_status, dict)

    # All allowed statuses should be present with a count of 0.
    for status in ("pending", "in-progress", "completed"):
        assert status in by_status
        assert by_status[status] == 0


def test_stats_reflects_counts_of_created_tasks() -> None:
    """Stats must correctly count tasks per status after inserts.

    This test creates several tasks with different statuses and then checks
    that `/api/tasks/stats` returns the correct aggregates. Initially this
    will fail because the stats endpoint is not yet implemented.
    """

    # Create some tasks across different statuses
    _create_task("Pending A", "pending")
    _create_task("Pending B", "pending")
    _create_task("In-progress A", "in-progress")
    _create_task("Completed A", "completed")
    _create_task("Completed B", "completed")

    response = _get_stats()
    assert response.status_code == 200, (
        "Expected GET /api/tasks/stats to return 200 after implementation. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert data["total"] >= 5

    by_status = data["byStatus"]
    assert by_status["pending"] >= 2
    assert by_status["in-progress"] >= 1
    assert by_status["completed"] >= 2

    # Sanity check: total should be at least the sum of the minimum expected counts.
    assert data["total"] >= (
        by_status["pending"] + by_status["in-progress"] + by_status["completed"]
    )
