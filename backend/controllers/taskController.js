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
// and for anyone consuming the API.
const getTasks = async (req, res) => {
  try {
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

module.exports = {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
};
