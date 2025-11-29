# Node.js multi-stage image for MERN repo and task testing
FROM node:20-alpine AS base
WORKDIR /app

# Install dependencies using workspaces
COPY package.json .
COPY client/package.json client/package.json
COPY server/package.json server/package.json
RUN npm ci --ignore-scripts

# Copy source and build client
COPY . .
RUN npm run build -w client

# Add Python and pytest tooling for task suites using pytest
RUN apk add --no-cache bash python3 py3-pip \
  && python3 -m pip install --no-cache-dir --upgrade pip \
  && python3 -m pip install --no-cache-dir pytest requests

# Non-root user and permissions
RUN addgroup -S appgroup && adduser -S appuser -G appgroup \
  && chown -R appuser:appgroup /app \
  && chmod +x /app/run_tests.sh
USER appuser

# Default entrypoint runs the task tests; grader will pass <task-id>
ENTRYPOINT ["./run_tests.sh"]
