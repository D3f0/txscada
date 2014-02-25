(function (window){
    // Define NS
    if (window.SMVE === undefined) {
        window.SMVE = {}
    }

    if (window.SMVE.errors === undefined) {
        window.SMVE.errors = {};
    }

    function showRESTErrorDialog(xhr, error, status){
        var data = jQuery.parseJSON(xhr.responseText),
            html_content;
        if (data.traceback) {
            html_content = data.traceback;
        } else {
            html_content = data.error;
        }
        html_content = html_content.replace('<', '[').replace('>', ']');
        // Disable connection
        //SMVE.updateButton.click();
        var dlg = $('<div>').dialog({
            title: data.error_message || status,
            width: "70%",
            modal: true,
            autoOpen: false,
            close: function (){
                $(this).dialog('destroy');
            },
            buttons: [
                {
                    text: "Close",
                    click: function() {
                        dlg.dialog('close');
                    }
                }

            ]
        }).html('<pre>'+html_content+'</pre>');
        dlg.dialog('open');
        return dlg;
    }

    window.SMVE.errors.showRESTErrorDialog = showRESTErrorDialog;
})(window);