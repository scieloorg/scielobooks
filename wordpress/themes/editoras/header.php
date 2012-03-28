<?php
/**
 * The Header for our theme.
 *
 * Displays all of the <head> section and everything up till <div id="main">
 *
 * @package WordPress
 * @subpackage Twenty_Ten
 * @since Twenty Ten 1.0
 */
?><!DOCTYPE html>
<?php $myOptions = get_option('myOptions'); 
$current_language = strtolower(get_bloginfo('language'));
?>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>" />
<title><?php
	/*
	 * Print the <title> tag based on what is being viewed.
	 */
	global $page, $paged;

	wp_title( '|', true, 'right' );

	// Add the blog name.
	bloginfo( 'name' );

	// Add the blog description for the home/front page.
	$site_description = get_bloginfo( 'description', 'display' );
	if ( $site_description && ( is_home() || is_front_page() ) )
		echo " | $site_description";

	// Add a page number if necessary:
	if ( $paged >= 2 || $page >= 2 )
		echo ' | ' . sprintf( __( 'Page %s', 'twentyten' ), max( $paged, $page ) );

	?></title>
<link rel="profile" href="http://gmpg.org/xfn/11" />
<link rel="stylesheet" type="text/css" media="all" href="<?php bloginfo( 'stylesheet_url' ); ?>" />
<link rel="pingback" href="<?php bloginfo( 'pingback_url' ); ?>" />
<?php
	/* We add some JavaScript to pages with the comment form
	 * to support sites with threaded comments (when in use).
	 */
	if ( is_singular() && get_option( 'thread_comments' ) )
		wp_enqueue_script( 'comment-reply' );

	/* Always have wp_head() just before the closing </head>
	 * tag of your theme, or you will break many plugins, which
	 * generally use this hook to add elements to <head> such
	 * as styles, scripts, and meta tags.
	 */
	wp_head();
?>
<style type="text/css">
	html { margin-top: 0px !important; }
	* html body { margin-top: 0px !important; }
</style>
<?php wp_head(); ?>
</head>
<style>
#site-title-mainlogo {
        <?php $background_url = $myOptions['theme_mainlogoURL_'.$current_language]; ?>
        <?php if(substr($background_url, 0, 1) != '/') {
            //Gambs. A função get_option altera o valor, retirando a barra inicial para o valor en.
            $background_url = '/'.$background_url;
	}?>
        background: url(<?php echo $background_url ;?>) top left no-repeat;
}

#site-title-sublogo {
        background: url(<?php echo $myOptions['theme_sublogoURL_'.$current_language];?>) top left no-repeat;
        width: 250px;
        height: 80px;
}
</style>

<body <?php body_class(); ?>>
<div id="wrapper" class="hfeed">
        <div id="header">
        <!--SciELO Language bar -->
                <div id="language_bar">
                        <?php if (function_exists('mlf_links_to_languages')) mlf_links_to_languages(); ?>
                </div>
                <div id="masthead">
                        <div id="branding" role="banner">                                <div class="logo"><a href="/" id="site-title-mainlogo"></a></div>
                                <a href="<?php bloginfo('wpurl'); ?>"> 
                                        <div class="siteDesc">
                                        <?php $heading_tag = ( is_home() || is_front_page() ) ? 'h1' : 'div'; ?>
                                                <<?php echo $heading_tag; ?> id="site-title-sublogo">
                                                </<?php echo $heading_tag; ?>>
                                        </div><!--siteDesc-->
                                </a>
                        </div><!-- #branding -->

			<!--div id="access" role="navigation">
			  <?php /*  Allow screen readers / text browsers to skip the navigation menu and get right to the good stuff */ ?>
				<div class="skip-link screen-reader-text"><a href="#content" title="<?php esc_attr_e( 'Skip to content', 'twentyten' ); ?>"><?php _e( 'Skip to content', 'twentyten' ); ?></a></div>
				<?php /* Our navigation menu.  If one isn't filled out, wp_nav_menu falls back to wp_page_menu.  The menu assiged to the primary position is the one used.  If none is assigned, the menu with the lowest ID is used.  */ ?>
				<?php wp_nav_menu( array( 'container_class' => 'menu-header', 'theme_location' => 'primary' ) ); ?>
			</div--><!-- #access -->
		</div><!-- #masthead -->
	</div><!-- #header -->
	
	<div id="main">
