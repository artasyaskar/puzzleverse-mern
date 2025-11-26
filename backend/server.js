// Entry point for the Project Puzzle backend.
// This file wires up the basic Express server, middleware, and placeholder routes.
// Real task-specific logic, validation, and error handling will be added later.

const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const mongoose = require('mongoose');

// Load environment variables from .env file during development
dotenv.config();

const connectDB = require('./config/db');
const taskRoutes = require('./routes/tasks');

const app = express();

// Basic middleware setup for JSON parsing and CORS.
app.use(cors());
app.use(express.json());

// Connect to MongoDB using a placeholder URI for now.
// The actual connection string will be configured in the .env file.
connectDB();

// Simple health check route to quickly verify that the backend is up.
app.get('/api/health', (req, res) => {
  return res.json({ status: 'ok', message: 'Project Puzzle backend placeholder is running.' });
});

// Mount placeholder task routes under /api/tasks.
// These will later be replaced with real task handling logic.
app.use('/api/tasks', taskRoutes);

// Fallback route for anything that does not match existing endpoints.
app.use((req, res) => {
  return res.status(404).json({ message: 'Route not implemented yet. This is a placeholder response.' });
});

// Use PORT from environment when available, otherwise fall back to a sensible default.
const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  // Logging kept simple and developer-friendly, can be replaced with a proper logger later.
  console.log(`Project Puzzle backend listening on port ${PORT}`);
});
