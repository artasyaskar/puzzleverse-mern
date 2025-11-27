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
    const { status } = req.query || {};

    // When a status query parameter is provided, validate it against the
    // set of allowed statuses and apply a filtered query. If the value is
    // not allowed, return a 400 with a clear error message.
    if (typeof status !== 'undefined') {
      if (!ALLOWED_STATUSES.includes(status)) {
        return res.status(400).json({
          message: 'Status value is not valid.',
        });
      }

      const filteredTasks = await Task.find({ status }).sort({ createdAt: -1 });
      return res.json(filteredTasks);
    }

    // Default behaviour when no filter is provided: return all tasks,
    // ordered newest-first.
    const tasks = await Task.find().sort({ createdAt: -1 });
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

module.exports = {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
  getTaskStats,
  searchTasks,
};
