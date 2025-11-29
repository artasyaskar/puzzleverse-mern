# Node.js multi-stage image for MERN repo and task testing
FROM node:20-alpine AS base
WORKDIR /app

# Install dependencies using workspaces
COPY package.json .
COPY client/package.json client/package.json
COPY server/package.json server/package.json
RUN npm install --ignore-scripts --workspaces --include-workspace-root

# Copy source and build client
COPY . .
RUN npm run build -w client

# Add Python and pytest tooling for task suites using pytest (use Alpine packages)
RUN apk add --no-cache bash python3 py3-pytest py3-requests

# Non-root user and permissions
RUN addgroup -S appgroup && adduser -S appuser -G appgroup \
  && chown -R appuser:appgroup /app \
  && find /app -type f -name "*.sh" -exec chmod +x {} +
USER appuser

# Default entrypoint runs the task tests; grader will pass <task-id>
ENTRYPOINT ["./run_tests.sh"]
