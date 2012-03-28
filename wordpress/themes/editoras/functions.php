<?php

    $current_language = strtolower(get_bloginfo('language'));

    if (function_exists('add_theme_support')) {
            add_theme_support('post-thumbnails');
            set_post_thumbnail_size(190, 140, true);
            add_image_size('mini_thumb', 85, 120, true);
    		add_image_size('video_thumb', 290, 170, true);
    }
    if ( function_exists('register_sidebar') )
    register_sidebar(array('name'=>'leftSlot' . $current_language, 
            'before_widget' => '<div id="%1$s" class="widget %2$s">',
            'after_widget' => '</div>',
            'before_title' => '<h2 class="widgettitle">',
            'after_title' => '</h2>',
        ));
    if ( function_exists('register_sidebar') )
    register_sidebar(array('name'=>'SearchBox' . $current_language, 
        'before_widget' => '<div id="%1$s" class="widget %2$s">',
        'after_widget' => '</div>',
        'before_title' => '<h2 class="widgettitle">',
        'after_title' => '</h2>',
    ));
    if ( function_exists('register_sidebar') )
    register_sidebar(array('name'=>'OnSpotlight' . $current_language, 
            'before_widget' => '<div id="%1$s" class="widget %2$s">',
            'after_widget' => '</div>',
            'before_title' => '<h2 class="widgettitle">',
            'after_title' => '</h2>',
        ));
    if ( function_exists('register_sidebar') )
    register_sidebar(array('name'=>'rightSlot1' . $current_language, 
            'before_widget' => '<div id="%1$s" class="widget %2$s">',
            'after_widget' => '</div>',
            'before_title' => '<h2 class="widgettitle">',
            'after_title' => '</h2>',
        ));
    if ( function_exists('register_sidebar') )
    register_sidebar(array('name'=>'rightSlot2' . $current_language, 
            'before_widget' => '<div id="%1$s" class="widget %2$s">',
            'after_widget' => '</div>',
            'before_title' => '<h2 class="widgettitle">',
            'after_title' => '</h2>',
        ));
    if ( function_exists('register_sidebar') )
    register_sidebar(array('name'=>'footer' . $current_language, 
            'before_widget' => '<div id="%1$s" class="widget %2$s">',
            'after_widget' => '</div>',
            'before_title' => '<h2 class="widgettitle">',
            'after_title' => '</h2>',
        ));
    add_theme_support( 'menus' );
    add_filter( 'wp_feed_cache_transient_lifetime', create_function( '$a', 'return 300;' ) );


$themename = "Site Logos";
$shortname = "theme";
$options = array (

   	array(    "name" => "Site",
            "type" => "titles",),
    	
	array(    "name" => "<span style='float: left;'>Main Logo URL PT:</span>",
            "id" => $shortname."_mainlogoURL_pt-br",
            "type" => "text",
            "std" => "/default.png",
            ),
        array(    "name" => "<span style='float: left;'>Main Logo URL ES:</span>",
            "id" => $shortname."_mainlogoURL_es-es",
            "type" => "text",
            "std" => "/default.png",
            ),
        array(    "name" => "<span style='float: left;'>Main Logo URL EN:</span>",
            "id" => $shortname."_mainlogoURL_en-us",
            "type" => "text",
            "std" => "/default.png",
            ),
        array(    "name" => "<span style='float: left;'>Sub Logo URL PT:</span>",
            "id" => $shortname."_sublogoURL_pt-br",
            "type" => "text",
            "std" => "/default.png",
            ),
        array(    "name" => "<span style='float: left;'>Sub Logo URL ES:</span>",
            "id" => $shortname."_sublogoURL_es-es",
            "type" => "text",
            "std" => "/default.png",
            ),
        array(    "name" => "<span style='float: left;'>Sub Logo URL EN:</span>",
            "id" => $shortname."_sublogoURL_en-us",
            "type" => "text",
            "std" => "/default.png",
            ),
);

function mytheme_add_admin() {

    global $themename, $shortname, $options;

    if ( $_GET['page'] == basename(__FILE__) ) {
    
        if ( 'save' == $_REQUEST['action'] ) {
$myOptions = array();
foreach ($options as $value) {
$myOptions[$value['id']]=$_REQUEST[ $value['id'] ];
}
update_option('myOptions', $myOptions);
if( isset( $_REQUEST[ $value['id'] ] ) ) {
update_option('myOptions', $myOptions);
} else {
delete_option( $value['id'] );
}

header("Location: themes.php?page=functions.php&saved=true");
die;
 
} else if( 'reset' == $_REQUEST['action'] ) {
 
foreach ($options as $value) {
delete_option( $value['id'] ); }
 
header("Location: themes.php?page=functions.php&reset=true");
die;
 
}
}

    add_theme_page($themename." Options", "Site Logos", 'edit_themes', basename(__FILE__), 'mytheme_admin');

}

function mytheme_admin() {

    global $themename, $shortname, $options;

    if ( $_REQUEST['saved'] ) echo '<div id="message" class="updated fade"><p><strong>'.$themename.' opções salvas.</strong></p></div>';
    if ( $_REQUEST['reset'] ) echo '<div id="message" class="updated fade"><p><strong>'.$themename.' opções resetadas.</strong></p></div>';
    
?>

<div class="wrap">
<h2><?php echo $themename; ?> opções</h2>

<form method="post">



<?php 
//print_r($myOptions);
foreach ($options as $value) {
$myOptions = get_option('myOptions');
 
    
if ($value['type'] == "text") { ?>

<div style="float: left; width: 880px; background-color:#f9f9f9; border-left: 1px solid #C6C6C6; border-right: 1px solid #C6C6C6;  border-bottom: 1px solid #C6C6C6; padding: 10px;">     
<div style="width: 80px; float: left;"><?php echo $value['name']; ?></div>
<div style="width: 500px; float: left;">
<input style="width: 400px;" name="<?php echo $value['id']; ?>" id="<?php echo $value['id']; ?>" type="<?php echo $value['type']; ?>" value="<?php if ( $myOptions[$value['id']] != "") { echo $myOptions[$value['id']]; } else { echo $value['std']; } ?>" />
</div>
<div class="logo" style="width: 220px; float: left;">
	<div style=" padding: 10px; border: 1px solid #cecece; background: #f2f2f2;">
		<img src="<?php if ( $myOptions[$value['id']] != "") { echo $myOptions[$value['id']]; } else { echo $value['std']; } ?>"/>
	</div>
</div>
</div>
 
<?php } elseif ($value['type'] == "text2") { ?>
        
<div style="float: left; width: 880px; background-color:#f9f9f9; border-left: 1px solid #C6C6C6; border-right: 1px solid #C6C6C6;  border-bottom: 1px solid #C6C6C6; padding: 10px;">     
<div style="width: 200px; float: left;"><?php echo $value['name']; ?></div>
<div style="width: 680px; float: left;"><textarea name="<?php echo $value['id']; ?>" id="<?php echo $value['id']; ?>" style="width: 400px; height: 200px;" type="<?php echo $value['type']; ?>"><?php if ( get_settings( $value['id'] ) != "") { echo get_settings( $value['id'] ); } else { echo $value['std']; } ?></textarea></div>
</div>

<?php } elseif ($value['type'] == "imageURL") { ?>
        
<div style="float: left; width: 880px; background-color:#f9f9f9; border-left: 1px solid #C6C6C6; border-right: 1px solid #C6C6C6;  border-bottom: 1px solid #C6C6C6; padding: 10px;">     
<div style="width: 200px; float: left;"><?php echo $value['name']; ?></div>
<div style="width: 680px; float: left;"><textarea name="<?php echo $value['id']; ?>" id="<?php echo $value['id']; ?>" style="width: 400px; height: 200px;" type="<?php echo $value['type']; ?>"><?php if ( get_settings( $value['id'] ) != "") { echo get_settings( $value['id'] ); } else { echo $value['std']; } ?></textarea></div>
</div>

<?php } elseif ($value['type'] == "textarea") { ?>
        
<div style="float: left; width: 880px; background-color:#f9f9f9; border-left: 1px solid #C6C6C6; border-right: 1px solid #C6C6C6;  border-bottom: 1px solid #C6C6C6; padding: 10px;">     
<div style="width: 200px; float: left;"><?php echo $value['name']; ?></div>
<div style="width: 680px; float: left;"><textarea name="<?php echo $value['id']; ?>" id="<?php echo $value['id']; ?>" style="width: 400px; height: 200px;" type="<?php echo $value['type']; ?>"><?php if ( get_settings( $value['id'] ) != "") { echo get_settings( $value['id'] ); } else { echo $value['std']; } ?></textarea></div>
</div>

<?php } elseif ($value['type'] == "select") { ?>

<div style="float: left; width: 880px; background-color:#f9f9f9; border-left: 1px solid #C6C6C6; border-right: 1px solid #C6C6C6;  border-bottom: 1px solid #C6C6C6; padding: 10px;">   
<div style="width: 200px; float: left;"><?php echo $value['name']; ?></div>
<div style="width: 680px; float: left;"><select name="<?php echo $value['id']; ?>" id="<?php echo $value['id']; ?>" style="width: 400px;">
<?php foreach ($value['options'] as $option) { ?>
<option<?php if ( get_settings( $value['id'] ) == $option) { echo ' selected="selected"'; } elseif ($option == $value['std']) { echo ' selected="selected"'; } ?>><?php echo $option; ?></option>
<?php } ?>
</select></div>
</div>

<?php } elseif ($value['type'] == "titles") { ?>

<div style="float: left; width: 870px; padding: 15px; background-color:#464646; border: 1px solid #C6C6C6; ; font-size: 16px; font-weight: bold; margin-top: 25px;color:#fff">   
<?php echo $value['name']; ?>
</div>

<?php 
} 
}
?>

<div style="clear: both;"></div>

<p class="submit">
<input name="save" type="submit" value="Save changes" />    
<input type="hidden" name="action" value="save" />
</p>
</form>
<form method="post">
<p class="submit">
<input name="reset" type="submit" value="Reset" />
<input type="hidden" name="action" value="reset" />
</p>
</form>

<?php
}

function mytheme_wp_head() { ?>

<?php }

add_action('wp_head', 'mytheme_wp_head');
add_action('admin_menu', 'mytheme_add_admin'); ?>
