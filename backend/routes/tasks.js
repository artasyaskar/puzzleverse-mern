// Express router for task-related endpoints in Project Puzzle.
// All routes here are wired to placeholder controller functions for now.
// Once the actual task logic is ready, these routes will become the main
// entry points for the task API.

const express = require('express');
const router = express.Router();

const {
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
} = require('../controllers/taskController');

// GET /api/tasks
// Returns a placeholder list of tasks for the time being.
router.get('/', getTasks);

// GET /api/tasks/stats
// Returns aggregate information about tasks by status.
router.get('/stats', getTaskStats);

router.get('/search', searchTasks);

router.get('/export', exportTasksCsv);

router.get('/overdue', getOverdueTasks);

// POST /api/tasks
// Will be used to create a new task.
router.post('/', createTask);

router.post('/bulk', createTasksBulk);

// PUT /api/tasks/:id
// Placeholder endpoint for updating an existing task.
router.put('/:id', updateTask);

// DELETE /api/tasks/:id
// Placeholder endpoint for removing a task.
router.delete('/:id', deleteTask);

router.patch('/:id/status', updateTaskStatus);

router.patch('/:id/archive', archiveTask);

router.patch('/:id/due-date', updateTaskDueDate);

module.exports = router;
