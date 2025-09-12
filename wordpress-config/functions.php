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
