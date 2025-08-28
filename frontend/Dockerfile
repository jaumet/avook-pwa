# Stage 1: Build the React application
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve the application with a Node.js server
FROM node:20-alpine

WORKDIR /app

# Copy built assets from the build stage
COPY --from=build /app/dist ./dist

# Copy dependencies needed to run `serve`
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json .

# Make port 5173 available
EXPOSE 5173

# Serve the production build, correctly handling SPA routing
CMD ["./node_modules/.bin/serve", "-s", "dist", "-l", "5173"]
