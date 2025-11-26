// Basic MongoDB connection helper for the Project Puzzle backend.
// This connects to MongoDB. Replace with real URI later.

const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    // In a real setup, this would come from process.env.MONGO_URI.
    // For now we keep a sensible default so that the app can still start
    // even if a concrete connection string is not provided.
    const mongoUri = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/project-puzzle-placeholder';

    await mongoose.connect(mongoUri, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });

    console.log('Connected to MongoDB for Project Puzzle (placeholder).');
  } catch (error) {
    console.error('Failed to connect to MongoDB (placeholder config).', error.message);
    // For now we simply log the error and exit. In a real project we might
    // implement retry logic or a more graceful shutdown.
    process.exit(1);
  }
};

module.exports = connectDB;
