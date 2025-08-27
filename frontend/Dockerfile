# Use an official Node.js runtime as a parent image
FROM node:20-alpine

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

# Make port 5173 available
EXPOSE 5173

# Serve the production build
CMD ["./node_modules/.bin/serve", "-s", "dist", "-l", "5173"]
