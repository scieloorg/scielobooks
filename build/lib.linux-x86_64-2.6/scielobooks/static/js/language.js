$(document).ready(function(){
    $("#lang_en").click(function() {
        $("#form_language input#language").val('en');
        $("#form_language").submit();
    });
    $("#lang_pt").click(function() {
        $("#form_language input#language").val('pt');
        $("#form_language").submit();
    });
});
