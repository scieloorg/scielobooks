$(document).ready(function(){
    $('.action_activate').click(function(){
        var selected = $(this).attr('id');
        $('#actions_load_icon_'+selected).show();
        $.post("/users/function/setactive/",
             {"id":selected}, function(res){
                 $('#actions_load_icon_'+selected).hide();
                 location.reload();
        });        
    });
    $('.action_deactivate').click(function(){
        var selected = $(this).attr('id');
        $('#actions_load_icon_'+selected).show();
        $.post("/users/function/setinactive/",
             {"id":selected}, function(res){
                 $('#actions_load_icon_'+selected).hide();
                 location.reload();
        });        
    });
    /* start tablesorter */
    $("#users-list-table").tablesorter({
      sortList: [[0,0],[1,0]]
    });

});