# Project Puzzle

This repository contains a **MERN stack skeleton** for a project called **Project Puzzle**. The goal of this setup is to provide a clean, realistic starting point that feels like it was put together by a human developer, while intentionally leaving out any task-specific business logic.

Both the backend and frontend are wired just enough to start up, respond with placeholder data, and give you clear spots where real task logic can be added later.

---

## Stack Overview

- **Backend**: Node.js, Express, MongoDB (via Mongoose)
- **Frontend**: React with React Router
- **Utilities**: Lightweight Python script placeholder for future automation

---

## Project Structure

```text
backend/
  config/
    db.js
  controllers/
    taskController.js
  models/
    Task.js
  routes/
    tasks.js
  server.js
  package.json

frontend/
  public/
    index.html
  src/
    components/
      Header.js
      Footer.js
      Dashboard.js
    pages/
      Home.js
      Tasks.js
    styles/
      index.css
    App.js
    index.js
  package.json

utilities/
  run_all_tasks.py

.gitignore
.env.example
README.md
```

Each file contains comments explaining what it does and where real logic should be added later.

---

## Getting Started

### 1. Prerequisites

- Node.js (LTS recommended)
- npm or yarn
- Python 3 (for the utilities script, used later)
- A running MongoDB instance (local or hosted) for when you are ready to replace the placeholder configuration

---

## Backend Setup (Express + MongoDB)

1. Navigate into the backend folder:

   ```bash
   cd backend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Create a `.env` file based on `.env.example` in the project root, and make sure `MONGO_URI` is set to a valid MongoDB connection string.

4. Start the backend in development mode (with nodemon):

   ```bash
   npm run dev
   ```

5. Once running, you can hit the placeholder endpoints:

   - Health check: `GET http://localhost:5000/api/health`
   - Tasks placeholder routes under: `http://localhost:5000/api/tasks`

These routes only return static placeholder JSON responses for now.

---

## Frontend Setup (React)

1. Navigate into the frontend folder:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the React development server:

   ```bash
   npm start
   ```

4. Open your browser at `http://localhost:3000` to see the placeholder UI.

   - **Home Page**: simple welcome text
   - **Tasks Page**: placeholder for where the task list will eventually be rendered
   - **Dashboard**: minimal shell where high-level task overview will live

No real API calls are being made yet; the UI is intentionally static.

---

## Utilities

Inside `utilities/run_all_tasks.py` you will find a minimal Python script with a single `run_all_tasks` function. For now it just prints a placeholder message, but the structure is ready for future automation or scripting around project tasks.

You can run it with:

```bash
python utilities/run_all_tasks.py
```

---

## Next Steps

This repository is intentionally focused on structure and clarity rather than features. Some natural follow-up steps once you are ready to implement real logic:

- Wire the `Task` model into `taskController.js` and replace placeholder responses with real queries.
- Introduce validation and error handling middleware for the Express API.
- Connect the React `Tasks` page to the backend using Axios and display real data.
- Build more interactive components in `Dashboard` to surface puzzle progress.
- Replace the minimal CSS in `src/styles/index.css` with a full design system or a component library.

Until then, the current state should serve as a solid, human-readable foundation for Project Puzzle.
