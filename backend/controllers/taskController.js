// Controller functions for task-related operations in Project Puzzle.
// All handlers here are intentionally kept as placeholders and will
// later be expanded with real database queries, validation, and
// error handling.

// GET /api/tasks
// For now this just returns a static placeholder payload.
const getTasks = async (req, res) => {
  // In the future, this will fetch tasks from MongoDB using the Task model.
  return res.json({
    message: 'getTasks placeholder - task list will be returned from the database later.',
    data: [],
  });
};

// POST /api/tasks
// Placeholder for creating a new task.
const createTask = async (req, res) => {
  // Real implementation will read data from req.body, validate it,
  // and persist a new Task document.
  return res.status(201).json({
    message: 'createTask placeholder - new task will be created and saved later.',
  });
};

// PUT /api/tasks/:id
// Placeholder for updating an existing task.
const updateTask = async (req, res) => {
  const { id } = req.params;

  // Actual update logic will go here: finding a task by ID and applying updates.
  return res.json({
    message: 'updateTask placeholder - task will be updated later.',
    taskId: id,
  });
};

// DELETE /api/tasks/:id
// Placeholder for deleting an existing task.
const deleteTask = async (req, res) => {
  const { id } = req.params;

  // Future logic will remove the specified task from the database.
  return res.json({
    message: 'deleteTask placeholder - task will be deleted later.',
    taskId: id,
  });
};

module.exports = {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
};
