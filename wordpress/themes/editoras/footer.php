<?
$current_language = strtolower(get_bloginfo('language'));
?>
	</div><!-- #main -->

	<div id="footer" role="contentinfo">
		<div id="colophon">

            <?php if ( !function_exists('dynamic_sidebar') || !dynamic_sidebar('footer' . $current_language) ) : ?>
    		<?php endif; ?>
			
		</div><!-- #colophon -->
	</div><!-- #footer -->
</div><!-- #wrapper -->
<?php wp_footer(); ?>
</body>
</html>
