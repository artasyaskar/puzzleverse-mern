// Controller functions for task-related operations in Project Puzzle.
// All handlers here are intentionally kept as placeholders and will
// later be expanded with real database queries, validation, and
// error handling.
const mongoose = require('mongoose');
const Task = require('../models/Task');

// A small helper to keep the set of allowed status values in one place.
const ALLOWED_STATUSES = ['pending', 'in-progress', 'completed'];

// GET /api/tasks
// For now this just returns a static placeholder payload.
// Updated: this now returns the real list of tasks from MongoDB, ordered
// newest-first by createdAt so that the behaviour is predictable for tests
// and for anyone consuming the API. It also supports optional status-based
// filtering via the `status` query parameter.
const getTasks = async (req, res) => {
  try {
    const { status, includeArchived, label } = req.query || {};

    const filter = {};

    // By default we only return non-archived tasks. When includeArchived is
    // explicitly set to the string "true", we skip this filter and return all
    // tasks regardless of archive status.
    const includeArchivedFlag = includeArchived === 'true';
    if (!includeArchivedFlag) {
      filter.archived = false;
    }

    // When a status query parameter is provided, validate it against the
    // set of allowed statuses and apply a filtered query. If the value is
    // not allowed, return a 400 with a clear error message.
    if (typeof status !== 'undefined') {
      if (!ALLOWED_STATUSES.includes(status)) {
        return res.status(400).json({
          message: 'Status value is not valid.',
        });
      }

      filter.status = status;
    }

    if (typeof label !== 'undefined') {
      // We treat the label query as an exact match against the stored labels
      // array. Labels themselves are trimmed when stored, so we simply match
      // the provided value as-is here.
      filter.labels = label;
    }

    const tasks = await Task.find(filter).sort({ createdAt: -1 });
    return res.json(tasks);
  } catch (error) {
    // In case something unexpected goes wrong when talking to the database,
    // we return a generic 500 and keep the error details on the server side.
    return res.status(500).json({
      message: 'Failed to fetch tasks.',
    });
  }
};

// POST /api/tasks
// Placeholder for creating a new task.
// Updated: reads data from req.body, validates it, and persists a new Task
// document. Validation is intentionally straightforward but strict enough
// to catch obvious issues such as missing or whitespace-only titles.
const createTask = async (req, res) => {
  try {
    const { title, description, status } = req.body || {};

    const trimmedTitle = typeof title === 'string' ? title.trim() : '';
    if (!trimmedTitle) {
      return res.status(400).json({
        message: 'Title is required and must be a non-empty string.',
      });
    }

    if (status && !ALLOWED_STATUSES.includes(status)) {
      return res.status(400).json({
        message: 'Status value is not valid.',
      });
    }

    const task = await Task.create({
      title: trimmedTitle,
      description,
      status,
    });

    return res.status(201).json(task);
  } catch (error) {
    // If something unexpected happens while creating the task, surface a
    // generic server error instead of leaking the raw database error.
    return res.status(500).json({
      message: 'Failed to create task.',
    });
  }
};

// PUT /api/tasks/:id
// Placeholder for updating an existing task.
// Updated: performs basic validation, checks for a valid ObjectId, handles
// 404 when the task does not exist, and returns the updated document.
const updateTask = async (req, res) => {
  const { id } = req.params;

  if (!mongoose.isValidObjectId(id)) {
    return res.status(400).json({
      message: 'Invalid task id.',
    });
  }

  const { title, description, status } = req.body || {};

  if (typeof status !== 'undefined' && !ALLOWED_STATUSES.includes(status)) {
    return res.status(400).json({
      message: 'Status value is not valid.',
    });
  }

  if (typeof title === 'string' && !title.trim()) {
    return res.status(400).json({
      message: 'Title, when provided, must not be empty.',
    });
  }

  const update = {};
  if (typeof title === 'string') update.title = title.trim();
  if (typeof description !== 'undefined') update.description = description;
  if (typeof status !== 'undefined') update.status = status;

  try {
    const updated = await Task.findByIdAndUpdate(id, update, {
      new: true,
      runValidators: true,
    });

    if (!updated) {
      return res.status(404).json({
        message: 'Task not found.',
      });
    }

    return res.json(updated);
  } catch (error) {
    return res.status(500).json({
      message: 'Failed to update task.',
    });
  }
};

// DELETE /api/tasks/:id
// Placeholder for deleting an existing task.
// Updated: deletes a task by id and clearly distinguishes between the
// successful delete case (200) and the not-found case (404). Invalid
// ObjectIds yield a 400.
const deleteTask = async (req, res) => {
  const { id } = req.params;

  if (!mongoose.isValidObjectId(id)) {
    return res.status(400).json({
      message: 'Invalid task id.',
    });
  }

  try {
    const deleted = await Task.findByIdAndDelete(id);

    if (!deleted) {
      return res.status(404).json({
        message: 'Task not found.',
      });
    }

    return res.json({
      message: 'Task deleted successfully.',
      id: deleted._id,
    });
  } catch (error) {
    return res.status(500).json({
      message: 'Failed to delete task.',
    });
  }
};

// GET /api/tasks/stats
// Lightweight aggregation endpoint that reports how many tasks exist in total
// and how many tasks fall under each allowed status. This keeps the logic
// simple and pushes heavy lifting down to MongoDB when needed.
const getTaskStats = async (req, res) => {
  try {
    // Fetch counts per status in a single pass using aggregation.
    const pipeline = [
      {
        $group: {
          _id: '$status',
          count: { $sum: 1 },
        },
      },
    ];

    const results = await Task.aggregate(pipeline);

    const byStatus = {};
    let total = 0;

    // Initialise all known statuses with zero so the shape is predictable
    // even when the collection is empty.
    ALLOWED_STATUSES.forEach((status) => {
      byStatus[status] = 0;
    });

    for (const row of results) {
      const status = row._id;
      const count = row.count || 0;

      if (ALLOWED_STATUSES.includes(status)) {
        byStatus[status] = count;
      }

      total += count;
    }

    return res.json({
      total,
      byStatus,
    });
  } catch (error) {
    return res.status(500).json({
      message: 'Failed to fetch task statistics.',
    });
  }
};

const searchTasks = async (req, res) => {
  try {
    const rawPage = req.query && req.query.page;
    const rawPageSize = req.query && req.query.pageSize;
    const rawStatus = req.query && req.query.status;
    const rawSortBy = req.query && req.query.sortBy;
    const rawSortDirection = req.query && req.query.sortDirection;

    let page = parseInt(rawPage, 10);
    if (Number.isNaN(page) || page <= 0) {
      page = 1;
    }

    let pageSize = parseInt(rawPageSize, 10);
    if (Number.isNaN(pageSize) || pageSize <= 0) {
      pageSize = 10;
    }

    if (pageSize < 1 || pageSize > 50) {
      return res.status(400).json({
        message: 'pageSize must be between 1 and 50.',
      });
    }

    let statusFilter = undefined;
    if (typeof rawStatus !== 'undefined') {
      if (!ALLOWED_STATUSES.includes(rawStatus)) {
        return res.status(400).json({
          message: 'Status value is not valid.',
        });
      }
      statusFilter = rawStatus;
    }

    const allowedSortFields = ['createdAt', 'title', 'status'];
    const sortBy = allowedSortFields.includes(rawSortBy) ? rawSortBy : 'createdAt';

    let sortDirection = 'desc';
    if (rawSortDirection === 'asc' || rawSortDirection === 'desc') {
      sortDirection = rawSortDirection;
    }

    const sortOrder = sortDirection === 'asc' ? 1 : -1;

    const filter = {};
    if (typeof statusFilter !== 'undefined') {
      filter.status = statusFilter;
    }

    const totalItems = await Task.countDocuments(filter);

    const skip = (page - 1) * pageSize;

    const items = await Task.find(filter)
      .sort({ [sortBy]: sortOrder })
      .skip(skip)
      .limit(pageSize);

    const totalPages = totalItems === 0 ? 0 : Math.ceil(totalItems / pageSize);

    const meta = {
      page,
      pageSize,
      totalItems,
      totalPages,
      hasNextPage: totalItems > page * pageSize,
      hasPreviousPage: page > 1,
    };

    return res.json({
      items,
      meta,
    });
  } catch (error) {
    return res.status(500).json({
      message: 'Failed to search tasks.',
    });
  }
};

const createTasksBulk = async (req, res) => {
  try {
    const { tasks } = req.body || {};

    if (!Array.isArray(tasks)) {
      return res.status(400).json({
        message: 'The "tasks" field is required and must be an array.',
      });
    }

    if (tasks.length === 0) {
      return res.status(400).json({
        message: 'The tasks array must contain at least one task.',
      });
    }

    if (tasks.length > 50) {
      return res.status(400).json({
        message: 'The tasks array cannot contain more than 50 tasks.',
      });
    }

    const documentsToInsert = [];

    for (const rawTask of tasks) {
      const title = typeof rawTask.title === 'string' ? rawTask.title.trim() : '';
      const description =
        typeof rawTask.description === 'string' ? rawTask.description : '';
      const status = rawTask.status;

      if (!title) {
        return res.status(400).json({
          message: 'Each task must have a non-empty title.',
        });
      }

      if (typeof status !== 'undefined' && !ALLOWED_STATUSES.includes(status)) {
        return res.status(400).json({
          message: 'One or more tasks have an invalid status.',
        });
      }

      const doc = {
        title,
        description,
      };

      if (typeof status !== 'undefined') {
        doc.status = status;
      }

      documentsToInsert.push(doc);
    }

    const created = await Task.insertMany(documentsToInsert);

    return res.status(201).json(created);
  } catch (error) {
    return res.status(500).json({
      message: 'Failed to create tasks in bulk.',
    });
  }
};

const exportTasksCsv = async (req, res) => {
  try {
    const { status } = req.query || {};

    if (typeof status !== 'undefined') {
      if (!ALLOWED_STATUSES.includes(status)) {
        return res.status(400).json({
          message: 'Status value is not valid.',
        });
      }
    }

    const filter = {};
    if (typeof status !== 'undefined') {
      filter.status = status;
    }

    const tasks = await Task.find(filter).sort({ createdAt: -1 });

    const header = ['id', 'title', 'description', 'status', 'createdAt', 'updatedAt'];

    const escapeCsvField = (value) => {
      if (value === null || typeof value === 'undefined') {
        return '';
      }

      const str = String(value);
      if (str.includes('"') || str.includes(',') || str.includes('\n')) {
        return '"' + str.replace(/"/g, '""') + '"';
      }
      return str;
    };

    const rows = [header.join(',')];

    tasks.forEach((task) => {
      const row = [
        escapeCsvField(task._id),
        escapeCsvField(task.title),
        escapeCsvField(task.description),
        escapeCsvField(task.status),
        escapeCsvField(task.createdAt && task.createdAt.toISOString()),
        escapeCsvField(task.updatedAt && task.updatedAt.toISOString()),
      ];

      rows.push(row.join(','));
    });

    const csv = rows.join('\n');

    res.setHeader('Content-Type', 'text/csv; charset=utf-8');
    res.setHeader('Content-Disposition', 'attachment; filename="tasks.csv"');

    return res.status(200).send(csv);
  } catch (error) {
    return res.status(500).json({
      message: 'Failed to export tasks as CSV.',
    });
  }
};

const updateTaskStatus = async (req, res) => {
  const { id } = req.params;

  if (!mongoose.isValidObjectId(id)) {
    return res.status(400).json({
      message: 'Invalid task id.',
    });
  }

  const { status } = req.body || {};

  if (typeof status !== 'string') {
    return res.status(400).json({
      message: 'Status field is required and must be a string.',
    });
  }

  if (!ALLOWED_STATUSES.includes(status)) {
    return res.status(400).json({
      message: 'Status value is not valid.',
    });
  }

  try {
    const task = await Task.findById(id);

    if (!task) {
      return res.status(404).json({
        message: 'Task not found.',
      });
    }

    const currentStatus = task.status;

    // Disallow changing away from completed.
    if (currentStatus === 'completed' && status !== 'completed') {
      return res.status(409).json({
        message: 'Cannot change status once a task is completed.',
      });
    }

    // Disallow moving backwards from in-progress to pending.
    if (currentStatus === 'in-progress' && status === 'pending') {
      return res.status(409).json({
        message: 'Cannot move a task from in-progress back to pending.',
      });
    }

    // If the requested status is the same as the current status, we treat it
    // as a no-op but still return the current document.
    if (currentStatus === status) {
      return res.json(task);
    }

    task.status = status;
    await task.save();

    return res.json(task);
  } catch (error) {
    return res.status(500).json({
      message: 'Failed to update task status.',
    });
  }
};

const archiveTask = async (req, res) => {
  const { id } = req.params;

  if (!mongoose.isValidObjectId(id)) {
    return res.status(400).json({
      message: 'Invalid task id.',
    });
  }

  const { archived } = req.body || {};

  if (typeof archived !== 'boolean') {
    return res.status(400).json({
      message: 'The archived field is required and must be a boolean.',
    });
  }

  try {
    const task = await Task.findById(id);

    if (!task) {
      return res.status(404).json({
        message: 'Task not found.',
      });
    }

    const now = new Date();

    if (archived) {
      if (!task.archived) {
        task.archived = true;
        task.archivedAt = now;
      }
    } else {
      if (task.archived) {
        task.archived = false;
        task.archivedAt = null;
      }
    }

    await task.save();

    return res.json(task);
  } catch (error) {
    return res.status(500).json({
      message: 'Failed to update archive state for task.',
    });
  }
};

const updateTaskDueDate = async (req, res) => {
  const { id } = req.params;

  if (!mongoose.isValidObjectId(id)) {
    return res.status(400).json({
      message: 'Invalid task id.',
    });
  }

  const { dueDate } = req.body || {};

  // Allow explicit null to clear the due date. For any non-null value we
  // require a valid ISO-8601 string that can be parsed into a Date.
  let parsedDate;

  if (dueDate === null) {
    parsedDate = null;
  } else {
    if (typeof dueDate === 'undefined') {
      return res.status(400).json({
        message: 'dueDate field is required (use null to clear it).',
      });
    }

    if (typeof dueDate !== 'string') {
      return res.status(400).json({
        message: 'dueDate must be an ISO 8601 string or null.',
      });
    }

    const candidate = new Date(dueDate);
    if (Number.isNaN(candidate.getTime())) {
      return res.status(400).json({
        message: 'dueDate value is not a valid date.',
      });
    }

    parsedDate = candidate;
  }

  try {
    const task = await Task.findById(id);

    if (!task) {
      return res.status(404).json({
        message: 'Task not found.',
      });
    }

    task.dueDate = parsedDate;
    await task.save();

    return res.json(task);
  } catch (error) {
    return res.status(500).json({
      message: 'Failed to update task due date.',
    });
  }
};

const getOverdueTasks = async (req, res) => {
  try {
    const now = new Date();

    const overdueTasks = await Task.find({
      dueDate: { $ne: null, $lt: now },
      archived: false,
    }).sort({ dueDate: 1 });

    return res.json(overdueTasks);
  } catch (error) {
    return res.status(500).json({
      message: 'Failed to fetch overdue tasks.',
    });
  }
};

const updateTaskLabels = async (req, res) => {
  const { id } = req.params;

  if (!mongoose.isValidObjectId(id)) {
    return res.status(400).json({
      message: 'Invalid task id.',
    });
  }

  const body = req.body || {};

  if (!Object.prototype.hasOwnProperty.call(body, 'labels')) {
    return res.status(400).json({
      message: 'The labels field is required and must be an array of strings.',
    });
  }

  const { labels } = body;

  if (!Array.isArray(labels)) {
    return res.status(400).json({
      message: 'The labels field is required and must be an array of strings.',
    });
  }

  const cleaned = [];
  const seen = new Set();

  for (const raw of labels) {
    if (typeof raw !== 'string') {
      return res.status(400).json({
        message: 'The labels field is required and must be an array of strings.',
      });
    }

    const trimmed = raw.trim();
    if (!trimmed) {
      continue;
    }

    if (seen.has(trimmed)) {
      continue;
    }

    seen.add(trimmed);
    cleaned.push(trimmed);
  }

  try {
    const task = await Task.findById(id);

    if (!task) {
      return res.status(404).json({
        message: 'Task not found.',
      });
    }

    task.labels = cleaned;
    await task.save();

    return res.json(task);
  } catch (error) {
    return res.status(500).json({
      message: 'Failed to update task labels.',
    });
  }
};

module.exports = {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
  getTaskStats,
  searchTasks,
  createTasksBulk,
  exportTasksCsv,
  updateTaskStatus,
  archiveTask,
  updateTaskDueDate,
  getOverdueTasks,
  updateTaskLabels,
};
