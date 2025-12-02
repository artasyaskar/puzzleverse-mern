# PuzzleVerse - MERN Stack Project

A full-stack web application built with the MERN stack (MongoDB, Express.js, React.js, Node.js). This project serves as a base for implementing 10 challenging programming tasks for LLM training.

## Prerequisites

- Node.js (v16+)
- npm or yarn
- MongoDB (or Docker for containerized MongoDB)
- Git

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd puzzleverse-mern
   ```

2. Install dependencies:
   ```bash
   # Install server dependencies
   npm install
   
   # Install client dependencies
   cd client
   npm install
   cd ..
   ```

3. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your environment variables (see `.env.example`)

4. Start the development servers:
   ```bash
   # Start backend server (from root directory)
   npm run server
   
   # In a new terminal, start frontend (from root directory)
   npm run client
   ```

## Available Scripts

- `npm run server` - Start the backend server
- `npm run client` - Start the frontend development server
- `npm run dev` - Run both frontend and backend concurrently
- `npm test` - Run tests

## Task Implementation

This repository includes 10 independent tasks, each with its own description and test suite. To work on a task:

1. Read the task description in `tasks/task-X/task_description.txt`
2. Implement the required changes
3. Run tests: `npm test task-X`
4. Verify your implementation
5. Create a diff: `git diff -- . ':!task/' > tasks/task-X/task_diff.txt`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
