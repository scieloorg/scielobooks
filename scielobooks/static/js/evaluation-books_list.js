$(document).ready(function(){
    /* start tablesorter */
    $("#evaluation-table").tablesorter({
      sortList: [[0,0]]
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