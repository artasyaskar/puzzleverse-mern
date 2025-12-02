# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
COPY client/package*.json ./client/

# Install root dependencies
RUN npm install

# Install client dependencies and build
WORKDIR /app/client
RUN npm install

# Copy client source
WORKDIR /app
COPY client ./client

# Build React app
RUN cd client && npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install production dependencies
COPY package*.json ./
RUN npm install --only=production

# Copy built React app
COPY --from=builder /app/client/build ./client/build

# Copy server files
COPY server ./server
COPY server.js ./

# Environment variables
ENV NODE_ENV=production
ENV PORT=5000

# Expose port
EXPOSE 5000

# Start the app
CMD ["node", "server.js"]
