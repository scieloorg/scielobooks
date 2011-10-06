$(document).ready(function(){

    var inputText = $("[type='text']");

    for (var i=0; i < inputText.length; i++)
        if (inputText[i].value == 'None')
            inputText[i].value = ''

});
