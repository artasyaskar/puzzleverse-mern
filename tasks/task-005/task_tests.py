import csv
import io
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


def _export_tasks(params: Dict[str, Any] | None = None) -> requests.Response:
    return requests.get(f"{BACKEND_BASE_URL}/api/tasks/export", params=params, timeout=10)


def _parse_csv(text: str) -> list[list[str]]:
    # Use csv.reader on a StringIO wrapper to parse the CSV into rows.
    reader = csv.reader(io.StringIO(text))
    return [row for row in reader]


def test_export_endpoint_returns_csv_with_header() -> None:
    """Basic smoke test for the /api/tasks/export endpoint.

    Initially this test will fail because the /api/tasks/export route does not
    exist yet. Once implemented, the endpoint should return a 200, a CSV
    content type, and at least the header row.
    """

    response = _export_tasks()
    assert response.status_code == 200, (
        "Expected GET /api/tasks/export to return 200 once implemented. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    content_type = response.headers.get("Content-Type", "")
    assert content_type.startswith("text/csv"), content_type

    disposition = response.headers.get("Content-Disposition", "")
    assert "attachment" in disposition and "tasks" in disposition

    rows = _parse_csv(response.text)
    assert rows, "Expected at least one row (the header) in the CSV output"

    header = rows[0]
    assert header == ["id", "title", "description", "status", "createdAt", "updatedAt"]


def test_export_includes_created_tasks_and_respects_status_filter() -> None:
    """CSV export should include tasks and support an optional status filter."""

    # Create a few tasks with different statuses.
    pending_task = _create_task("CSV Pending", "pending", "Will be exported")
    completed_task = _create_task("CSV Completed", "completed", "Also exported")
    _create_task("CSV In-progress", "in-progress", "Will be filtered out later")

    # Export all tasks without a filter.
    response_all = _export_tasks()
    assert response_all.status_code == 200, response_all.text

    rows_all = _parse_csv(response_all.text)
    header_all = rows_all[0]
    data_rows_all = rows_all[1:]

    # Make sure at least one of the created titles appears in the CSV.
    titles_all = [row[1] for row in data_rows_all] if data_rows_all else []
    assert pending_task["title"] in titles_all
    assert completed_task["title"] in titles_all

    # Now export only completed tasks.
    response_completed = _export_tasks({"status": "completed"})
    assert response_completed.status_code == 200, response_completed.text

    rows_completed = _parse_csv(response_completed.text)
    data_rows_completed = rows_completed[1:]

    statuses_completed = [row[3] for row in data_rows_completed] if data_rows_completed else []
    # All exported rows should have status "completed" when filtered.
    assert statuses_completed
    assert all(status == "completed" for status in statuses_completed)


def test_export_with_invalid_status_returns_400() -> None:
    """An invalid status filter should yield a 400 response with JSON."""

    response = _export_tasks({"status": "not-a-real-status"})
    assert response.status_code == 400, (
        "Expected GET /api/tasks/export with an invalid status to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert "message" in data
