#!/bin/bash
# WordPress Docker Setup Script for YTLite

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🐳 Setting up WordPress Docker environment for YTLite..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Create .env.wordpress if it doesn't exist
if [[ ! -f "$PROJECT_ROOT/.env.wordpress" ]]; then
    echo "📝 Creating .env.wordpress from example..."
    cp "$PROJECT_ROOT/.env.wordpress.example" "$PROJECT_ROOT/.env.wordpress"
    echo "⚠️  Please edit .env.wordpress with your configuration!"
fi

# Create wordpress-config directory
mkdir -p "$PROJECT_ROOT/wordpress-config"

# Create custom WordPress theme for YTLite
THEME_DIR="$PROJECT_ROOT/wordpress-config"
mkdir -p "$THEME_DIR"

cat > "$THEME_DIR/index.php" << 'EOF'
<?php
/**
 * YTLite WordPress Theme - Main Template
 * Optimized for SVG project display
 */
get_header(); ?>

<div id="primary" class="content-area">
    <main id="main" class="site-main">
        <?php if (have_posts()) : ?>
            <?php while (have_posts()) : the_post(); ?>
                <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                    <header class="entry-header">
                        <h1 class="entry-title"><?php the_title(); ?></h1>
                    </header>
                    
                    <div class="entry-content">
                        <?php 
                        // Display SVG projects if available
                        $svg_content = get_post_meta(get_the_ID(), 'ytlite_svg_content', true);
                        if ($svg_content) {
                            echo '<div class="ytlite-svg-container">';
                            echo $svg_content;
                            echo '</div>';
                        }
                        ?>
                        
                        <?php the_content(); ?>
                    </div>
                </article>
            <?php endwhile; ?>
        <?php endif; ?>
    </main>
</div>

<?php get_footer(); ?>
EOF

cat > "$THEME_DIR/style.css" << 'EOF'
/*
Theme Name: YTLite Theme
Description: Custom theme for YTLite SVG projects
Version: 1.0.0
*/

body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background: #f5f5f5;
}

.ytlite-svg-container {
    width: 100%;
    max-width: 1200px;
    margin: 20px auto;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    overflow: hidden;
}

.ytlite-svg-container svg {
    width: 100%;
    height: auto;
    display: block;
}

.entry-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.entry-title {
    text-align: center;
    color: #333;
    margin-bottom: 30px;
}
EOF

cat > "$THEME_DIR/functions.php" << 'EOF'
<?php
/**
 * YTLite Theme Functions
 */

// Add SVG support
function ytlite_allow_svg_upload($mimes) {
    $mimes['svg'] = 'image/svg+xml';
    return $mimes;
}
add_filter('upload_mimes', 'ytlite_allow_svg_upload');

// Add custom meta box for SVG content
function ytlite_add_svg_meta_box() {
    add_meta_box(
        'ytlite_svg_content',
        'YTLite SVG Content',
        'ytlite_svg_content_callback',
        'post'
    );
}
add_action('add_meta_boxes', 'ytlite_add_svg_meta_box');

function ytlite_svg_content_callback($post) {
    wp_nonce_field('ytlite_save_svg_content', 'ytlite_svg_nonce');
    $value = get_post_meta($post->ID, 'ytlite_svg_content', true);
    echo '<textarea name="ytlite_svg_content" rows="10" cols="80" style="width:100%;">' . esc_textarea($value) . '</textarea>';
    echo '<p><em>Paste your YTLite SVG project content here.</em></p>';
}

// Save SVG content
function ytlite_save_svg_content($post_id) {
    if (!isset($_POST['ytlite_svg_nonce']) || !wp_verify_nonce($_POST['ytlite_svg_nonce'], 'ytlite_save_svg_content')) {
        return;
    }
    
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
        return;
    }
    
    if (isset($_POST['ytlite_svg_content'])) {
        update_post_meta($post_id, 'ytlite_svg_content', sanitize_textarea_field($_POST['ytlite_svg_content']));
    }
}
add_action('save_post', 'ytlite_save_svg_content');
EOF

# Start WordPress containers
echo "🚀 Starting WordPress containers..."
cd "$PROJECT_ROOT"
docker-compose -f docker-compose.wordpress.yml up -d

# Wait for WordPress to be ready
echo "⏳ Waiting for WordPress to start..."
timeout=60
while [ $timeout -gt 0 ]; do
    if curl -s http://localhost:8080 >/dev/null 2>&1; then
        break
    fi
    sleep 2
    ((timeout-=2))
done

if [ $timeout -le 0 ]; then
    echo "❌ WordPress failed to start within 60 seconds"
    exit 1
fi

echo "✅ WordPress Docker environment is ready!"
echo ""
echo "🌐 Access URLs:"
echo "   WordPress: http://localhost:8080"
echo "   phpMyAdmin: http://localhost:8081"
echo ""
echo "📋 Default credentials:"
echo "   WordPress admin: admin / admin_password"
echo "   Database: wordpress / wordpress_password"
echo ""
echo "⚠️  Remember to:"
echo "   1. Complete WordPress setup at http://localhost:8080"
echo "   2. Create Application Password for API access"
echo "   3. Update .env.wordpress with your credentials"
echo ""
echo "🔧 Manage containers:"
echo "   Stop: docker-compose -f docker-compose.wordpress.yml down"
echo "   View logs: docker-compose -f docker-compose.wordpress.yml logs -f"
