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
