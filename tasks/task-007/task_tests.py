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


def _patch_archive(task_id: str, archived: Any) -> requests.Response:
    payload: Dict[str, Any] = {"archived": archived}
    return requests.patch(
        f"{BACKEND_BASE_URL}/api/tasks/{task_id}/archive",
        json=payload,
        timeout=5,
    )


def _get_tasks(params: Dict[str, Any] | None = None) -> requests.Response:
    return requests.get(f"{BACKEND_BASE_URL}/api/tasks", params=params, timeout=5)


def test_archiving_a_task_sets_flags_and_keeps_it_out_of_default_list() -> None:
    """Archiving a task should flip its flags and hide it from GET /api/tasks."""

    task = _create_task("Task 007 - archive me")
    task_id = task["_id"]

    response = _patch_archive(task_id, True)
    assert response.status_code == 200, response.text

    updated = response.json()
    assert updated.get("archived") is True
    assert updated.get("archivedAt") is not None

    # Archived task should not appear in the default list.
    list_response = _get_tasks()
    assert list_response.status_code == 200, list_response.text

    items = list_response.json()
    assert isinstance(items, list)
    ids = {item["_id"] for item in items}
    assert task_id not in ids


def test_include_archived_true_returns_archived_tasks() -> None:
    """includeArchived=true should bring archived tasks back into the listing."""

    task = _create_task("Task 007 - show in includeArchived")
    task_id = task["_id"]

    # Archive the task first.
    response = _patch_archive(task_id, True)
    assert response.status_code == 200, response.text

    # Now fetch with includeArchived=true and ensure the task is present.
    list_response = _get_tasks({"includeArchived": "true"})
    assert list_response.status_code == 200, list_response.text

    items = list_response.json()
    ids = {item["_id"] for item in items}
    assert task_id in ids


def test_unarchiving_task_resets_flags_and_brings_it_back() -> None:
    """Setting archived=false should clear flags and make the task visible again."""

    task = _create_task("Task 007 - unarchive flow")
    task_id = task["_id"]

    # Archive it first.
    response_archive = _patch_archive(task_id, True)
    assert response_archive.status_code == 200, response_archive.text

    # Now unarchive.
    response_unarchive = _patch_archive(task_id, False)
    assert response_unarchive.status_code == 200, response_unarchive.text

    updated = response_unarchive.json()
    assert updated.get("archived") is False
    assert updated.get("archivedAt") is None

    # After unarchiving, the task should appear again in the default list.
    list_response = _get_tasks()
    assert list_response.status_code == 200, list_response.text

    items = list_response.json()
    ids = {item["_id"] for item in items}
    assert task_id in ids


def test_invalid_archived_value_returns_400() -> None:
    """Non-boolean archived values should be rejected with a 400 error."""

    task = _create_task("Task 007 - invalid archived value")
    task_id = task["_id"]

    response = _patch_archive(task_id, "not-a-boolean")
    assert response.status_code == 400, (
        "Expected PATCH /api/tasks/:id/archive with a non-boolean archived value to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert "message" in data


def test_invalid_object_id_returns_400_for_archive_endpoint() -> None:
    """A non-ObjectId id should result in a 400 response for the archive endpoint."""

    response = _patch_archive("not-a-valid-objectid", True)
    assert response.status_code == 400, (
        "Expected PATCH /api/tasks/:id/archive with an invalid id to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert "message" in data


def test_archiving_nonexistent_task_returns_404() -> None:
    """Archiving a well-formed but nonexistent id should return 404."""

    # This assumes a well-formed but unlikely ObjectId.
    nonexistent_id = "64b7c1f5e13f5f2a9f0c1234"
    response = _patch_archive(nonexistent_id, True)
    assert response.status_code == 404, (
        "Expected PATCH /api/tasks/:id/archive for a nonexistent id to return 404. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert "message" in data
