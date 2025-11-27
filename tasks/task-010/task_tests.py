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


def _post_comment(task_id: str, message: Any) -> requests.Response:
    payload = {"message": message}
    return requests.post(
        f"{BACKEND_BASE_URL}/api/tasks/{task_id}/comments",
        json=payload,
        timeout=5,
    )


def _get_comments(task_id: str) -> requests.Response:
    return requests.get(f"{BACKEND_BASE_URL}/api/tasks/{task_id}/comments", timeout=5)


def test_posting_valid_comment_appends_to_task_and_trims_message() -> None:
    """A valid comment should be stored with trimmed message and returned by the list endpoint."""

    task = _create_task("Task 010 - comments basic")
    task_id = task["_id"]

    response = _post_comment(task_id, "  First update from QA  ")
    assert response.status_code == 201, response.text

    created = response.json()
    assert isinstance(created.get("message"), str)
    assert created["message"] == "First update from QA"

    list_response = _get_comments(task_id)
    assert list_response.status_code == 200, list_response.text

    comments = list_response.json()
    assert isinstance(comments, list)
    assert any(c.get("message") == "First update from QA" for c in comments)


def test_comments_are_returned_in_chronological_order() -> None:
    """GET /api/tasks/:id/comments should return comments ordered by createdAt ascending."""

    task = _create_task("Task 010 - ordering")
    task_id = task["_id"]

    messages = ["First", "Second", "Third"]
    for msg in messages:
        response = _post_comment(task_id, msg)
        assert response.status_code == 201, response.text

    list_response = _get_comments(task_id)
    assert list_response.status_code == 200, list_response.text

    comments = list_response.json()
    texts = [c.get("message") for c in comments]
    # We expect the messages back in the same order they were created.
    assert texts[:3] == messages


def test_invalid_comment_payload_returns_400() -> None:
    """Missing or non-string/blank message values should be rejected with 400."""

    task = _create_task("Task 010 - invalid comment payload")
    task_id = task["_id"]

    # Missing message field entirely.
    response_missing = requests.post(
        f"{BACKEND_BASE_URL}/api/tasks/{task_id}/comments",
        json={},
        timeout=5,
    )
    assert response_missing.status_code == 400, response_missing.text

    # Non-string message.
    response_non_string = _post_comment(task_id, 12345)
    assert response_non_string.status_code == 400, response_non_string.text

    # Blank-after-trim message.
    response_blank = _post_comment(task_id, "   ")
    assert response_blank.status_code == 400, response_blank.text


def test_invalid_object_id_for_comments_returns_400() -> None:
    """A non-ObjectId id for the comment endpoints should return 400."""

    response_post = _post_comment("not-a-valid-objectid", "Hello")
    assert response_post.status_code == 400, response_post.text

    response_get = _get_comments("not-a-valid-objectid")
    assert response_get.status_code == 400, response_get.text


def test_get_comments_for_nonexistent_task_returns_404() -> None:
    """GET comments for a valid-but-nonexistent id should return 404."""

    # Use a valid ObjectId-shaped string that is unlikely to exist.
    fake_id = "64b7f1f1f1f1f1f1f1f1f1f1"

    response = _get_comments(fake_id)
    assert response.status_code == 404, response.text

    data = response.json()
    assert "message" in data


def test_new_task_initially_has_no_comments() -> None:
    """A freshly created task should return an empty list of comments."""

    task = _create_task("Task 010 - empty comments")
    task_id = task["_id"]

    response = _get_comments(task_id)
    assert response.status_code == 200, response.text

    comments = response.json()
    assert isinstance(comments, list)
    assert comments == []
