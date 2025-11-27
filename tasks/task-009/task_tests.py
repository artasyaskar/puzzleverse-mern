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


def _create_task(title: str, status: str = "pending", description: str = "") -> Dict[str, Any]:
    payload = {
        "title": title,
        "status": status,
        "description": description,
    }
    response = requests.post(f"{BACKEND_BASE_URL}/api/tasks", json=payload, timeout=5)
    assert response.status_code == 201, response.text
    return response.json()


def _patch_labels(task_id: str, labels: List[Any]) -> requests.Response:
    payload: Dict[str, Any] = {"labels": labels}
    return requests.patch(
        f"{BACKEND_BASE_URL}/api/tasks/{task_id}/labels",
        json=payload,
        timeout=5,
    )


def _get_tasks(params: Dict[str, Any] | None = None) -> requests.Response:
    return requests.get(f"{BACKEND_BASE_URL}/api/tasks", params=params, timeout=5)


def test_setting_labels_replaces_existing_array_and_trims_values() -> None:
    """Setting labels should replace the array, trim strings, and drop empties."""

    task = _create_task("Task 009 - labels basic")
    task_id = task["_id"]

    response = _patch_labels(task_id, [" frontend ", "backend", "", "frontend"])
    assert response.status_code == 200, response.text

    updated = response.json()
    labels = updated.get("labels")
    assert isinstance(labels, list)
    # Empty string should be dropped, duplicates removed, whitespace trimmed.
    assert "frontend" in labels
    assert "backend" in labels
    assert "" not in labels
    assert len(labels) == len(set(labels))


def test_label_filter_returns_only_matching_tasks() -> None:
    """GET /api/tasks?label=foo should only return tasks that have that label."""

    task1 = _create_task("Task 009 - A")
    task2 = _create_task("Task 009 - B")

    _patch_labels(task1["_id"], ["frontend", "urgent"])
    _patch_labels(task2["_id"], ["backend"])

    response = _get_tasks({"label": "frontend"})
    assert response.status_code == 200, response.text

    items = response.json()
    ids = {item["_id"] for item in items}
    assert task1["_id"] in ids
    assert task2["_id"] not in ids


def test_label_filter_combines_with_status_filter() -> None:
    """Label filter should work together with status-based filtering."""

    task1 = _create_task("Task 009 - C", status="pending")
    task2 = _create_task("Task 009 - D", status="completed")

    _patch_labels(task1["_id"], ["frontend"])
    _patch_labels(task2["_id"], ["frontend"])

    response = _get_tasks({"label": "frontend", "status": "pending"})
    assert response.status_code == 200, response.text

    items = response.json()
    ids = {item["_id"] for item in items}
    assert task1["_id"] in ids
    assert task2["_id"] not in ids


def test_invalid_labels_payload_returns_400() -> None:
    """Non-array labels payloads should be rejected with 400."""

    task = _create_task("Task 009 - invalid labels payload")
    task_id = task["_id"]

    # labels should be an array, not a string.
    response = _patch_labels(task_id, "not-an-array")  # type: ignore[arg-type]
    assert response.status_code == 400, (
        "Expected PATCH /api/tasks/:id/labels with a non-array payload to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert "message" in data


def test_invalid_object_id_for_labels_returns_400() -> None:
    """A non-ObjectId id for the labels endpoint should return 400."""

    response = _patch_labels("not-a-valid-objectid", ["frontend"])
    assert response.status_code == 400, (
        "Expected PATCH /api/tasks/:id/labels with an invalid id to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert "message" in data


def test_missing_labels_field_returns_400() -> None:
    """Omitting the labels field should yield a 400 response."""

    task = _create_task("Task 009 - missing labels field")
    task_id = task["_id"]

    # Send an empty object, no labels key.
    response = requests.patch(
        f"{BACKEND_BASE_URL}/api/tasks/{task_id}/labels",
        json={},
        timeout=5,
    )
    assert response.status_code == 400, (
        "Expected PATCH /api/tasks/:id/labels without labels field to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert "message" in data
