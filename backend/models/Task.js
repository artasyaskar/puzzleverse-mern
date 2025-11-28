// Basic Task model definition for Project Puzzle.
// Task schema fields. Actual logic added later.
// This schema is intentionally minimal but uses realistic field names
// that will be extended with validation, indexes, and hooks later on.

const mongoose = require('mongoose');

const TaskSchema = new mongoose.Schema(
  {
    title: {
      type: String,
      required: true,
      trim: true,
    },
    description: {
      type: String,
      required: false,
      default: '',
    },
    status: {
      type: String,
      enum: ['pending', 'in-progress', 'completed'],
      default: 'pending',
    },
  },
  {
    timestamps: true, // Handy for tracking creation/update even during early development.
  }
);

// The model is exported so controllers can plug in real queries later.
const Task = mongoose.model('Task', TaskSchema);

module.exports = Task;
