# Stage 1: Build the React application
FROM node:20-alpine AS build

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application's source code
COPY . .

# Build the application for production
RUN npm run build

# Stage 2: Serve the static files with a Python server
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the built assets from the build stage
COPY --from=build /app/dist .

# Make port 5173 available
EXPOSE 5173

# Serve the application
CMD ["python", "-m", "http.server", "5173"]
