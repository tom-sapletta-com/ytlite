# Use a pre-built Tauri development image to speed up builds
FROM ivangabriele/tauri:debian-bookworm-20

# Set up the working directory
WORKDIR /app

# Copy dependency definitions
COPY package.json package-lock.json ./

# Install dependencies using npm ci for a clean, reproducible build
RUN npm ci

# Copy the rest of the application source code
COPY . .

# Default command to keep the container running
CMD ["tail", "-f", "/dev/null"]
