$(document).ready(function(){
    /* start tablesorter */
    $("#evaluation-table").tablesorter({
      sortList: [[0,0]]
    });

    $('.action_delete').click(function(){
        var selected = $(this).attr('id');
        var id = selected.split('_')[0];

        if(confirm("Please, confirm you are deleting a meeting")){
          // $('#actions_load_icon_'+slug).show();
          $.ajax({
            url: "/staff/meeting/"+id,
            type: "DELETE",
            success: function(res){
              // $('#actions_load_icon_'+slug).hide();
              location.reload();
            }
          });
        }
    });

});