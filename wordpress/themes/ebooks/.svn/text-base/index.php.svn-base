<?php get_header(); ?>
		<div id="container">
			<div class="leftCol">
			    <?php if ( !function_exists('dynamic_sidebar') || !dynamic_sidebar('leftSlot') ) : ?>
        		<?php endif; ?>
            </div><!-- #leftCol -->
            <div id="content" role="main">
			    <?php if ( !function_exists('dynamic_sidebar') || !dynamic_sidebar('SearchBox') ) : ?>
        		<?php endif; ?>
                
                <?php if(function_exists("insert_post_highlights")) insert_post_highlights(); ?>
                
                <div class="onSpotlight">
	                <?php if ( !function_exists('dynamic_sidebar') || !dynamic_sidebar('OnSpotlight') ) : ?>
	                <?php endif; ?>
                </div>
                
               	<div class="spacer"></div>
                
			</div><!-- #content -->
			<div class="rightCol">
                <?php if ( !function_exists('dynamic_sidebar') || !dynamic_sidebar('rightSlot1') ) : ?>
        		<?php endif; ?>
			</div><!-- #rightCol -->
            <div class="spacer">&#160;</div>
		</div><!-- #container -->
<?php get_footer(); ?>
