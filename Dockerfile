# Base Docker image for the Project Puzzle backend.
# This container focuses on running the Node/Express API. The frontend is
# expected to be run separately in development, or built and served by a
# dedicated frontend image if needed later.

FROM node:18-bullseye

# Create and switch to the app directory
WORKDIR /app

# Copy only backend package files first to take advantage of Docker layer caching
COPY backend/package*.json ./backend/

# Install backend dependencies
RUN cd backend \
  && npm install --production

# Copy the rest of the repository (including backend source)
COPY . .

# Expose the backend port
EXPOSE 5000

# Default environment variables; can be overridden at runtime
ENV PORT=5000 \
    MONGO_URI=mongodb://mongo:27017/project-puzzle

# Start the backend server
CMD ["sh", "-c", "cd backend && npm start"]
