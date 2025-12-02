# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY client/package*.json ./client/

# Install dependencies
RUN npm install
RUN cd client && npm install && cd ..

# Copy source files
COPY . .

# Build React app
RUN cd client && npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Copy built React app
COPY --from=builder /app/client/build ./client/build

# Copy server files
COPY package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY server ./server

# Environment variables
ENV NODE_ENV=production
ENV PORT=5000

# Expose port
EXPOSE 5000

# Start the app
CMD ["node", "server.js"]
