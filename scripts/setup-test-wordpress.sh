#!/bin/bash
set -e

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

echo -e "${YELLOW}🐳 Setting up WordPress test environment...${NC}"

# Start WordPress containers
echo "Starting WordPress containers..."
docker-compose -f docker-compose.test-wordpress.yml up -d

echo "Waiting for WordPress to be ready..."
sleep 30

# Check if WordPress is accessible
for i in {1..30}; do
    if curl -s http://localhost:8080 > /dev/null; then
        echo -e "${GREEN}✓ WordPress is accessible at http://localhost:8080${NC}"
        break
    fi
    echo "Waiting for WordPress... ($i/30)"
    sleep 2
done

# WordPress setup via WP-CLI in container
echo "Configuring WordPress..."
docker exec ytlite-wordpress-test wp core install \
    --url="http://localhost:8080" \
    --title="YTLite Test Site" \
    --admin_user="admin" \
    --admin_password="admin123" \
    --admin_email="admin@ytlite.test" \
    --skip-email || echo "WordPress might already be installed"

# Create application password for API access
echo "Setting up application password..."
docker exec ytlite-wordpress-test wp user application-password create admin ytlite-api \
    --porcelain > /tmp/wp-app-password.txt 2>/dev/null || echo "App password might already exist"

APP_PASSWORD=$(cat /tmp/wp-app-password.txt 2>/dev/null || echo "ytlite-test-password")

echo -e "${GREEN}✓ WordPress test environment ready!${NC}"
echo
echo -e "${YELLOW}WordPress Details:${NC}"
echo "URL: http://localhost:8080"
echo "Admin: http://localhost:8080/wp-admin"
echo "Username: admin"
echo "Password: admin123"
echo "App Password: $APP_PASSWORD"
echo
echo -e "${YELLOW}Database (phpMyAdmin):${NC}"
echo "URL: http://localhost:8081"
echo "Username: wordpress"
echo "Password: wordpress123"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Create example project: bash scripts/create-example-project.sh"
echo "2. Test publishing: make gui (then use WordPress section)"
echo "3. Stop containers: docker-compose -f docker-compose.test-wordpress.yml down"

# Save credentials to example project
mkdir -p output/projects/wordpress-test
cat > output/projects/wordpress-test/.env << EOF
# WordPress Test Environment Credentials
WORDPRESS_URL=http://localhost:8080
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=$APP_PASSWORD
UPLOAD_PRIVACY=public
PUBLIC_BASE_URL=http://localhost:5000
EOF

echo -e "${GREEN}✓ Credentials saved to output/projects/wordpress-test/.env${NC}"
