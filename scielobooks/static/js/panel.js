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
                   location.reload();
        });
    });

    $('.action_publish').click(function(){
        var selected = $(this).attr('id');
        var evaluation = selected.split('_')[0];

        if(confirm("Please, confirm you are publishing the book ISBN: "+evaluation )){
          $('#actions_load_icon_'+evaluation).show();
          $.post("/staff/function/actionpublish/",
                 {"evaluation":evaluation}, function(res){
                     $('#actions_load_icon_'+evaluation).hide();
                     location.reload();
          });
        }
    });

    $('.action_unpublish').click(function(){
        var selected = $(this).attr('id');
        var evaluation = selected.split('_')[0];

        if(confirm("Please, confirm you are unpublishing the book ISBN: "+evaluation )){
          $('#actions_load_icon_'+evaluation).show();
          $.post("/staff/function/actionunpublish/",
               {"evaluation":evaluation}, function(res){
                   $('#actions_load_icon_'+evaluation).hide();
                   location.reload();
          });
        }
    });

    $('.action_delete').click(function(){
        var selected = $(this).attr('id');
        var sbid = selected.split('_')[0];
        var evaluation = selected.split('_')[1];

        if(confirm("Please, confirm you are deleting the book ISBN: "+evaluation )){
          $('#actions_load_icon_'+evaluation).show();
          $.ajax({
            url: "/staff/book/id/"+sbid,
            type: "DELETE",
            success: function(res){
              $('#actions_load_icon_'+evaluation).hide();
              location.reload();
            }
          });
        }
    });

    /* start tablesorter */
    $("#evaluation-table").tablesorter({
      sortList: [[1,0]]
    });

    $('.filter-by-publisher').change(function(){
        var selected = $('option:selected', this).val();
        goto_url = location.pathname;
        if(selected !== 'nothing'){
          if(location.search.indexOf('publisher') === -1){
            if(location.search.length > 0){
              goto_url = goto_url+location.search+'&publisher='+selected;
            } else {
              goto_url = goto_url+'?publisher='+selected;
            }
          } else {
            goto_url = goto_url+location.search.replace(/publisher=[^&]+/, "publisher="+selected);
          }
        } else {
          new_search = location.search.replace(/[?&]publisher=[^&]+/, "");
          if (new_search[0] !== '?'){
            new_search='?'+new_search;
          }
          goto_url = goto_url+new_search;
        }

        location.href=goto_url;
    });

    $('.filter-by-meeting').change(function(){
        var selected = $('option:selected', this).val();
        goto_url = location.pathname;
        if(selected !== 'nothing'){
          if(location.search.indexOf('meeting') === -1){
            if(location.search.length > 0){
              goto_url = goto_url+location.search+'&meeting='+selected;
            } else {
              goto_url = goto_url+'?meeting='+selected;
            }
          } else {
            goto_url = goto_url+location.search.replace(/meeting=[^&]+/, "meeting="+selected);
          }
        } else {
          new_search = location.search.replace(/[?&]meeting=[^&]+/, "");
          if (new_search[0] !== '?'){
            new_search='?'+new_search;
          }
          goto_url = goto_url+new_search;
        }

        location.href=goto_url;
    });
});