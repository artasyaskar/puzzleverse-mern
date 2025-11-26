// Automated tests for Project Puzzle — Task 001
// These tests assume that the backend server is already running on
// http://localhost:5000 and that MongoDB is reachable.
//
// The goal here is not to be clever with the test runner, but to
// describe the contract that the Task API is expected to honour.

const http = require('http');
const assert = require('assert');

const BASE_URL = 'localhost';
const PORT = 5000;

function request(method, path, body) {
  const payload = body ? JSON.stringify(body) : null;

  const options = {
    hostname: BASE_URL,
    port: PORT,
    path,
    method,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  };

  if (payload) {
    options.headers['Content-Length'] = Buffer.byteLength(payload);
  }

  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        let parsed;
        try {
          parsed = data ? JSON.parse(data) : null;
        } catch (err) {
          return reject(new Error(`Failed to parse JSON response for ${method} ${path}: ${err.message}`));
        }
        resolve({ statusCode: res.statusCode, body: parsed });
      });
    });

    req.on('error', (err) => {
      reject(err);
    });

    if (payload) {
      req.write(payload);
    }

    req.end();
  });
}

async function run() {
  console.log('Running Task 001 tests against http://localhost:5000 ...');

  // We keep references to ids as we go so that later tests can
  // exercise update and delete behaviour on real documents.
  let firstTaskId = null;
  let secondTaskId = null;

  // 1. Sanity check: health endpoint should be alive and honest.
  {
    const { statusCode, body } = await request('GET', '/api/health');
    assert.strictEqual(statusCode, 200, 'Health endpoint should return HTTP 200');
    assert.ok(body && body.status === 'ok', 'Health endpoint should include a status of "ok"');
  }

  // 2. Creating a valid task should yield 201 and a well-formed document.
  {
    const payload = {
      title: 'Write first backend test',
      description: 'Make sure the Task API can actually create a real task.',
    };

    const { statusCode, body } = await request('POST', '/api/tasks', payload);

    assert.strictEqual(statusCode, 201, 'Creating a valid task should return HTTP 201');
    assert.ok(body && body._id, 'Created task should contain a MongoDB _id');
    assert.strictEqual(body.title, payload.title, 'Created task should echo back the title');
    assert.strictEqual(body.description, payload.description, 'Created task should echo back the description');
    assert.ok(['pending', 'in-progress', 'completed'].includes(body.status), 'Created task should have a recognised status value');

    firstTaskId = body._id;
  }

  // 3. Creating a second task with an explicit non-default status.
  {
    const payload = {
      title: 'Mark something as completed',
      description: 'This one should not start as pending.',
      status: 'completed',
    };

    const { statusCode, body } = await request('POST', '/api/tasks', payload);

    assert.strictEqual(statusCode, 201, 'Creating a second valid task should return HTTP 201');
    assert.ok(body && body._id, 'Second created task should contain a MongoDB _id');
    assert.strictEqual(body.status, 'completed', 'Second task should preserve the explicit status value');

    secondTaskId = body._id;
  }

  // 4. Creating a task with a missing or whitespace-only title should fail.
  {
    const payloads = [
      { description: 'Missing title entirely' },
      { title: '   ', description: 'Whitespace-only title' },
    ];

    for (const payload of payloads) {
      const { statusCode } = await request('POST', '/api/tasks', payload);
      assert.strictEqual(statusCode, 400, 'Invalid task payloads should return HTTP 400');
    }
  }

  // 5. Listing tasks should return them in newest-first order.
  {
    const { statusCode, body } = await request('GET', '/api/tasks');

    assert.strictEqual(statusCode, 200, 'Listing tasks should return HTTP 200');
    assert.ok(Array.isArray(body), 'Task list response should be a JSON array');
    assert.ok(body.length >= 2, 'Task list should contain at least the two tasks created earlier');

    // We created firstTaskId before secondTaskId, so if the list is
    // sorted by createdAt descending, the second one should appear
    // before the first in the returned array.
    const ids = body.map((t) => t._id);
    const firstIndex = ids.indexOf(firstTaskId);
    const secondIndex = ids.indexOf(secondTaskId);

    assert.ok(firstIndex !== -1 && secondIndex !== -1, 'Both created tasks should be present in the list');
    assert.ok(secondIndex < firstIndex, 'Newer task should appear before older task in the list');
  }

  // 6. Updating a task with a valid payload should work as expected.
  {
    const update = {
      status: 'in-progress',
      description: 'This task has now been started.',
    };

    const { statusCode, body } = await request('PUT', `/api/tasks/${firstTaskId}`, update);

    assert.strictEqual(statusCode, 200, 'Updating an existing task should return HTTP 200');
    assert.strictEqual(body._id, firstTaskId, 'Updated task should keep the same id');
    assert.strictEqual(body.status, 'in-progress', 'Updated task should reflect the new status');
    assert.strictEqual(body.description, update.description, 'Updated task should reflect the new description');
  }

  // 7. Updating a task with an invalid status should be rejected.
  {
    const update = { status: 'archived' }; // not part of the allowed enum
    const { statusCode } = await request('PUT', `/api/tasks/${firstTaskId}`, update);
    assert.strictEqual(statusCode, 400, 'Updating with an invalid status value should return HTTP 400');
  }

  // 8. Deleting an existing task should succeed, and deleting it again should yield 404.
  {
    const { statusCode: firstDeleteStatus } = await request('DELETE', `/api/tasks/${secondTaskId}`);
    assert.strictEqual(firstDeleteStatus, 200, 'Deleting an existing task should return HTTP 200');

    const { statusCode: secondDeleteStatus } = await request('DELETE', `/api/tasks/${secondTaskId}`);
    assert.strictEqual(secondDeleteStatus, 404, 'Deleting the same task again should return HTTP 404');
  }

  // 9. Using an obviously invalid ObjectId should not crash the server.
  {
    const invalidId = 'not-a-valid-object-id';

    const { statusCode } = await request('PUT', `/api/tasks/${invalidId}`, { status: 'completed' });
    assert.strictEqual(statusCode, 400, 'Updating with an invalid ObjectId should return HTTP 400, not 500');
  }

  console.log('All Task 001 tests passed successfully.');
}

run().catch((err) => {
  console.error('Test run failed:');
  console.error(err && err.stack ? err.stack : err);
  process.exit(1);
});
