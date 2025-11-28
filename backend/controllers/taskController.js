// Controller functions for task-related operations in Project Puzzle.
// All handlers here are intentionally kept as placeholders and will
// later be expanded with real database queries, validation, and
// error handling.

const Task = require('../models/Task');

// GET /api/tasks
// For now this just returns a static placeholder payload.
const getTasks = async (req, res) => {
  try {
    const tasks = await Task.find({}).lean();
    return res.json({ data: tasks });
  } catch (err) {
    return res.status(500).json({ message: 'Failed to fetch tasks' });
  }
};

// POST /api/tasks
// Placeholder for creating a new task.
const createTask = async (req, res) => {
  try {
    const { title, description, status } = req.body || {};

    if (!title || typeof title !== 'string' || !title.trim()) {
      return res.status(400).json({ message: 'Title is required' });
    }

    const doc = await Task.create({
      title: title.trim(),
      description: description || '',
      status,
    });

    return res.status(201).json(doc);
  } catch (err) {
    if (err && err.name === 'ValidationError') {
      return res.status(400).json({ message: 'Invalid task data' });
    }
    return res.status(500).json({ message: 'Failed to create task' });
  }
};

// PUT /api/tasks/:id
// Placeholder for updating an existing task.
const updateTask = async (req, res) => {
  const { id } = req.params;
  try {
    const updates = req.body || {};
    const updated = await Task.findByIdAndUpdate(id, updates, {
      new: true,
      runValidators: true,
    }).lean();

    if (!updated) {
      return res.status(404).json({ message: 'Task not found' });
    }

    return res.json(updated);
  } catch (err) {
    if (err && err.name === 'ValidationError') {
      return res.status(400).json({ message: 'Invalid task data' });
    }
    return res.status(500).json({ message: 'Failed to update task' });
  }
};

// DELETE /api/tasks/:id
// Placeholder for deleting an existing task.
const deleteTask = async (req, res) => {
  const { id } = req.params;
  try {
    const deleted = await Task.findByIdAndDelete(id).lean();
    if (!deleted) {
      return res.status(404).json({ message: 'Task not found' });
    }
    return res.json({ message: 'Task deleted', taskId: id });
  } catch (err) {
    return res.status(500).json({ message: 'Failed to delete task' });
  }
};

// GET /api/tasks/:id
const getTaskById = async (req, res) => {
  const { id } = req.params;
  try {
    const task = await Task.findById(id).lean();
    if (!task) {
      return res.status(404).json({ message: 'Task not found' });
    }
    return res.json(task);
  } catch (err) {
    return res.status(500).json({ message: 'Failed to fetch task' });
  }
};

module.exports = {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
  getTaskById,
};
