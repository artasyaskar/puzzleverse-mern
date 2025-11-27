import datetime as dt
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


def _patch_due_date(task_id: str, due_date: Any) -> requests.Response:
    payload: Dict[str, Any] = {"dueDate": due_date}
    return requests.patch(
        f"{BACKEND_BASE_URL}/api/tasks/{task_id}/due-date",
        json=payload,
        timeout=5,
    )


def _get_overdue() -> requests.Response:
    return requests.get(f"{BACKEND_BASE_URL}/api/tasks/overdue", timeout=5)


def test_setting_valid_due_date_updates_task() -> None:
    """PATCH /api/tasks/:id/due-date with a valid ISO string should update dueDate."""

    task = _create_task("Task 008 - due date")
    task_id = task["_id"]

    due_date = "2030-01-01T12:00:00.000Z"
    response = _patch_due_date(task_id, due_date)
    assert response.status_code == 200, response.text

    updated = response.json()
    assert updated.get("dueDate") is not None


def test_clearing_due_date_sets_it_to_null() -> None:
    """Sending dueDate=null should clear the stored due date."""

    task = _create_task("Task 008 - clear due date")
    task_id = task["_id"]

    # First set a due date.
    response_set = _patch_due_date(task_id, "2030-01-01T12:00:00.000Z")
    assert response_set.status_code == 200, response_set.text

    # Now clear it.
    response_clear = _patch_due_date(task_id, None)
    assert response_clear.status_code == 200, response_clear.text

    updated = response_clear.json()
    assert updated.get("dueDate") is None


def test_invalid_due_date_string_returns_400() -> None:
    """An unparseable due date string should result in a 400 response."""

    task = _create_task("Task 008 - invalid due date")
    task_id = task["_id"]

    response = _patch_due_date(task_id, "not-a-real-date")
    assert response.status_code == 400, (
        "Expected PATCH /api/tasks/:id/due-date with an invalid date to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert "message" in data


def test_invalid_object_id_for_due_date_returns_400() -> None:
    """A non-ObjectId id for the due-date endpoint should return 400."""

    response = _patch_due_date("not-a-valid-objectid", "2030-01-01T12:00:00.000Z")
    assert response.status_code == 400, (
        "Expected PATCH /api/tasks/:id/due-date with an invalid id to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert "message" in data


def test_setting_past_due_date_makes_task_overdue() -> None:
    """Tasks with dueDate in the past should appear in the overdue list."""

    task = _create_task("Task 008 - overdue")
    task_id = task["_id"]

    past_date = (dt.datetime.utcnow() - dt.timedelta(days=1)).replace(microsecond=0)
    past_iso = past_date.isoformat() + "Z"

    response = _patch_due_date(task_id, past_iso)
    assert response.status_code == 200, response.text

    overdue_response = _get_overdue()
    assert overdue_response.status_code == 200, overdue_response.text

    overdue_items = overdue_response.json()
    ids = {item["_id"] for item in overdue_items}
    assert task_id in ids


def test_future_due_date_is_not_overdue() -> None:
    """Tasks with a dueDate in the future should not be returned by /api/tasks/overdue."""

    task = _create_task("Task 008 - future")
    task_id = task["_id"]

    future_date = (dt.datetime.utcnow() + dt.timedelta(days=2)).replace(microsecond=0)
    future_iso = future_date.isoformat() + "Z"

    response = _patch_due_date(task_id, future_iso)
    assert response.status_code == 200, response.text

    overdue_response = _get_overdue()
    assert overdue_response.status_code == 200, overdue_response.text

    overdue_items = overdue_response.json()
    ids = {item["_id"] for item in overdue_items}
    assert task_id not in ids


def test_overdue_endpoint_ignores_archived_tasks() -> None:
    """Archived tasks should not appear in the overdue list even if their dueDate is past."""

    task = _create_task("Task 008 - archived overdue")
    task_id = task["_id"]

    past_date = (dt.datetime.utcnow() - dt.timedelta(days=1)).replace(microsecond=0)
    past_iso = past_date.isoformat() + "Z"

    response_due = _patch_due_date(task_id, past_iso)
    assert response_due.status_code == 200, response_due.text

    # Archive the task using the existing archive endpoint from Task 007.
    archive_payload = {"archived": True}
    archive_response = requests.patch(
        f"{BACKEND_BASE_URL}/api/tasks/{task_id}/archive",
        json=archive_payload,
        timeout=5,
    )
    assert archive_response.status_code == 200, archive_response.text

    overdue_response = _get_overdue()
    assert overdue_response.status_code == 200, overdue_response.text

    overdue_items = overdue_response.json()
    ids = {item["_id"] for item in overdue_items}
    assert task_id not in ids


def test_overdue_endpoint_returns_empty_list_when_no_tasks_are_overdue() -> None:
    """When no tasks meet the overdue criteria, the endpoint should return an empty list."""

    response = _get_overdue()
    assert response.status_code == 200, response.text

    items = response.json()
    assert isinstance(items, list)
    assert items == [] or all("dueDate" in item for item in items)
