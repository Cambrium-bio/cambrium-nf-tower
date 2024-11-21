# Stage 1: Build the Angular application using OpenJDK 11 and Node.js
FROM openjdk:11-jdk-slim AS builder

# Install dependencies required for Node.js and Angular CLI
RUN apt-get update && \
    apt-get install -y curl bash wget && \
    # Install Node.js 18.x from NodeSource
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    # Upgrade npm to the latest version
    npm install -g npm@latest && \
    # Install Angular CLI globally
    npm install -g @angular/cli@latest --unsafe-perm=true && \
    # Clean up to reduce image size
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variable to allow legacy OpenSSL algorithms (temporary workaround)
ENV NODE_OPTIONS=--openssl-legacy-provider

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy dependency definitions first for better caching
COPY package*.json ./

# Install npm dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the Angular application for production
RUN npm run build

# Stage 2: Serve the built Angular application using Nginx
FROM nginx:stable-alpine

# Label for versioning
LABEL version="1.0"

# Remove the default Nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy custom Nginx configuration (ensure you have a valid nginx.conf)
COPY nginx.conf /etc/nginx/nginx.conf

# Copy the Angular build output from the builder stage
COPY --from=builder /usr/src/app/dist/tower-web/ /usr/share/nginx/html/

# Optional: Add a health check to ensure Nginx is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# Expose port 80 (default for Nginx)
EXPOSE 80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]
