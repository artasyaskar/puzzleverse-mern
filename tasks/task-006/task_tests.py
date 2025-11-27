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


def _create_task(title: str, status: str = "pending", description: str = "") -> Dict[str, Any]:
    payload = {
        "title": title,
        "status": status,
        "description": description,
    }
    response = requests.post(f"{BACKEND_BASE_URL}/api/tasks", json=payload, timeout=5)
    assert response.status_code == 201, response.text
    return response.json()


def _patch_status(task_id: str, status: str | None) -> requests.Response:
    payload: Dict[str, Any] = {}
    if status is not None:
        payload["status"] = status
    return requests.patch(
        f"{BACKEND_BASE_URL}/api/tasks/{task_id}/status",
        json=payload,
        timeout=5,
    )


def test_pending_to_in_progress_is_allowed() -> None:
    """A task should be able to move from pending to in-progress."""

    task = _create_task("Task 006 - pending")
    task_id = task["_id"]

    response = _patch_status(task_id, "in-progress")
    assert response.status_code == 200, response.text

    updated = response.json()
    assert updated["status"] == "in-progress"


def test_in_progress_to_completed_is_allowed() -> None:
    """A task should be able to move from in-progress to completed."""

    task = _create_task("Task 006 - in-progress", status="in-progress")
    task_id = task["_id"]

    response = _patch_status(task_id, "completed")
    assert response.status_code == 200, response.text

    updated = response.json()
    assert updated["status"] == "completed"


def test_completed_cannot_move_back_to_pending() -> None:
    """Once completed, a task should not be able to move back to pending."""

    task = _create_task("Task 006 - completed", status="completed")
    task_id = task["_id"]

    response = _patch_status(task_id, "pending")
    assert response.status_code == 409, (
        "Expected a 409 Conflict when trying to move from completed back to pending. "
        f"Got {response.status_code} with body: {response.text!r}"
    )


def test_invalid_status_value_returns_400() -> None:
    """An unsupported status value should result in a 400 response."""

    task = _create_task("Task 006 - invalid status test")
    task_id = task["_id"]

    response = _patch_status(task_id, "not-a-real-status")
    assert response.status_code == 400, (
        "Expected PATCH /api/tasks/:id/status with an invalid status to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert "message" in data


def test_invalid_object_id_returns_400() -> None:
    """A non-ObjectId id should result in a 400 response."""

    response = _patch_status("not-a-valid-objectid", "in-progress")
    assert response.status_code == 400, (
        "Expected PATCH /api/tasks/:id/status with an invalid id to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert "message" in data


def test_missing_status_field_returns_400() -> None:
    """Omitting the status field in the body should yield a 400."""

    task = _create_task("Task 006 - missing status field")
    task_id = task["_id"]

    response = _patch_status(task_id, None)
    assert response.status_code == 400, (
        "Expected PATCH /api/tasks/:id/status without a status field to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert "message" in data
