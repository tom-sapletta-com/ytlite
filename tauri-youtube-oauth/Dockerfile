# Use a pre-built Tauri development image to speed up builds
FROM ivangabriele/docker-tauri:debian-bookworm-20

# Set up the working directory
WORKDIR /app

# Install Node.js dependencies (cached layer)
COPY package*.json ./
RUN npm install

# Dependencies will be handled by the first build command inside the container

# Copy the rest of the application source code
WORKDIR /app
COPY . .

# Default command to keep the container running
CMD ["tail", "-f", "/dev/null"]
