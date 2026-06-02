# Use official Node image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files first (caching)
COPY package*.json ./
RUN npm install

# Copy app code
COPY . .

# Build the app (we'll serve with serve package
RUN npm run build

# Expose port
EXPOSE 3000

# Install serve to serve static build
RUN npm install -g serve

# Serve
CMD ["serve", "-s", "dist", "-l", "3000"]
