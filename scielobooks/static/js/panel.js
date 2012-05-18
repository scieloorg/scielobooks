$(document).ready(function(){
    $('.meetings').change(function(){
        var selected = $('option:selected', this).val();
        var sbid = selected.split('_')[0];
        var meeting = selected.split('_')[1];

        $('#meeting_load_icon_'+sbid).show();

        $.post("/staff/function/setmeeting/",
               {"sbid":sbid, "meeting":meeting}, function(res){
                   $('#meeting_load_icon_'+sbid).hide();
        });
    });

    $('.committee-decision').change(function(){
        var selected = $('option:selected', this).val();
        var sbid = selected.split('_')[0];
        var decision = selected.split('_')[1];

        $('#committee-decision_load_icon_'+sbid).show();

        $.post("/staff/function/setcommitteedecision/",
               {"sbid":sbid, "decision":decision}, function(res){
                   $('#committee-decision_load_icon_'+sbid).hide();
                   location.reload();
        });
    });

    $('.action_publish').click(function(){
        var selected = $(this).attr('id');
        var sbid = selected.split('_')[0];

        if(confirm("Please, confirm you are publishing the book SBID: "+sbid )){
          $('#actions_load_icon_'+sbid).show();
          $.post("/staff/function/actionpublish/",
                 {"sbid":sbid}, function(res){
                    $('#actions_load_icon_'+sbid).hide();
                    if(res == "insufficient params"){
                      alert("This book cannot yet be published. Check for missing data.");
                    }
                    location.reload();
          });
        }
    });

    $('.action_unpublish').click(function(){
        var selected = $(this).attr('id');
        var sbid = selected.split('_')[0];

        if(confirm("Please, confirm you are unpublishing the book SBID: "+sbid )){
          $('#actions_load_icon_'+sbid).show();
          $.post("/staff/function/actionunpublish/",
               {"sbid":sbid}, function(res){
                   $('#actions_load_icon_'+sbid).hide();
                   location.reload();
          });
        }
    });

    $('.action_delete').click(function(){
        var selected = $(this).attr('id');
        var sbid = selected.split('_')[0];

        if(confirm("Please, confirm you are deleting the book SBID: "+sbid )){
          $('#actions_load_icon_'+sbid).show();
          $.ajax({
            url: "/staff/book/id/"+sbid,
            type: "DELETE",
            success: function(res){
              $('#actions_load_icon_'+sbid).hide();
              location.reload();
            }
          });
        }
    });

    /* start tablesorter */
    $("#evaluation-table").tablesorter();
});