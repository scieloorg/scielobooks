$(document).ready(function(){
    $('.meetings').change(function(){
        var selected = $('option:selected', this).val();
        var evaluation = selected.split('_')[0];
        var meeting = selected.split('_')[1];
        
        $('#meeting_load_icon_'+evaluation).show();

        $.post("/staff/function/setmeeting/",
               {"evaluation":evaluation, "meeting":meeting}, function(res){
                   $('#meeting_load_icon_'+evaluation).hide();
        });                    
    });

    $('.committee-decision').change(function(){
        var selected = $('option:selected', this).val();                    
        var evaluation = selected.split('_')[0];
        var decision = selected.split('_')[1];
        
        $('#committee-decision_load_icon_'+evaluation).show();

        $.post("/staff/function/setcommitteedecision/",
               {"evaluation":evaluation, "decision":decision}, function(res){
                   $('#committee-decision_load_icon_'+evaluation).hide();
        });                                   
    });
    
    $('.action_publish').click(function(){        
        var selected = $(this).attr('id');
        var evaluation = selected.split('_')[0];

        $('#actions_load_icon_'+evaluation).show();

        $.post("/staff/function/actionpublish/",
               {"evaluation":evaluation}, function(res){
                   $('#actions_load_icon_'+evaluation).hide();
                   location.reload();
        });
    });

    $('.action_unpublish').click(function(){
        var selected = $(this).attr('id');
        var evaluation = selected.split('_')[0];

        $('#actions_load_icon_'+evaluation).show();

        $.post("/staff/function/actionunpublish/",
               {"evaluation":evaluation}, function(res){
                   $('#actions_load_icon_'+evaluation).hide();
                   location.reload();
        });
    });    
    /* start tablesorter */
    $("#evaluation-table").tablesorter({
      sortList: [[1,0],[2,0]]
    });

});