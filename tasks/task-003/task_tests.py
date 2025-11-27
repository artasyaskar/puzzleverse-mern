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


def _search_tasks(params: Dict[str, Any] | None = None) -> requests.Response:
    return requests.get(f"{BACKEND_BASE_URL}/api/tasks/search", params=params, timeout=5)


def test_search_endpoint_returns_expected_shape() -> None:
    """Basic smoke test for the /api/tasks/search endpoint.

    Initially this test will fail because the /api/tasks/search route does not
    exist yet and the backend will likely return a 404. Once implemented, the
    endpoint should return a 200 and a JSON object with `items` and `meta`
    keys, where `items` is a list.
    """

    response = _search_tasks()
    assert response.status_code == 200, (
        "Expected GET /api/tasks/search to return 200 once implemented. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    data = response.json()
    assert set(data.keys()) == {"items", "meta"}
    assert isinstance(data["items"], list)
    assert isinstance(data["meta"], dict)

    meta = data["meta"]
    for key in ("page", "pageSize", "totalItems", "totalPages", "hasNextPage", "hasPreviousPage"):
        assert key in meta


def test_pagination_and_sorting_behaviour() -> None:
    """Pagination and sorting should behave as described in the task.

    This test creates several tasks, then uses /api/tasks/search to fetch
    different pages and verify that ordering and metadata are correct.
    """

    # Create tasks with titles that have a clear alphabetical order
    titles = [
        "Alpha task",
        "Bravo task",
        "Charlie task",
        "Delta task",
        "Echo task",
    ]
    for t in titles:
        _create_task(t, "pending")

    # Request the first page with a pageSize of 2, sorted by title ascending.
    response_page1 = _search_tasks({
        "page": 1,
        "pageSize": 2,
        "sortBy": "title",
        "sortDirection": "asc",
    })
    assert response_page1.status_code == 200, response_page1.text

    data1 = response_page1.json()
    items1 = data1["items"]
    meta1 = data1["meta"]

    assert meta1["page"] == 1
    assert meta1["pageSize"] == 2
    assert meta1["totalItems"] >= 5
    assert meta1["totalPages"] >= 3

    # With ascending title order, the first page should start with Alpha and Bravo.
    returned_titles_page1 = [item["title"] for item in items1]
    assert returned_titles_page1[:2] == ["Alpha task", "Bravo task"]

    # Request the second page with the same settings.
    response_page2 = _search_tasks({
        "page": 2,
        "pageSize": 2,
        "sortBy": "title",
        "sortDirection": "asc",
    })
    assert response_page2.status_code == 200, response_page2.text

    data2 = response_page2.json()
    items2 = data2["items"]

    returned_titles_page2 = [item["title"] for item in items2]
    # Across the first two pages we expect to see at least the next titles
    # from the sorted list.
    all_seen = returned_titles_page1 + returned_titles_page2
    assert "Charlie task" in all_seen
    assert "Delta task" in all_seen


def test_invalid_query_parameters_are_rejected_with_400() -> None:
    """Invalid pageSize and status values should result in 400 responses."""

    # pageSize too large
    response = _search_tasks({"page": 1, "pageSize": 999})
    assert response.status_code == 400, (
        "Expected pageSize above the allowed maximum to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )

    # Invalid status filter
    response = _search_tasks({"status": "not-a-real-status"})
    assert response.status_code == 400, (
        "Expected an invalid status filter to return 400. "
        f"Got {response.status_code} with body: {response.text!r}"
    )
