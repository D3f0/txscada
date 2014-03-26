(function($){
    function onCalculateOnClick(event) {
        event.preventDefault();
        var $this = $(this);
        try {
            var data = JSON.parse($(this).attr('data'));
        } catch (e) {
            console.error("Cannot read data from link", e);
            return;
        };

        var $dlg = $('<div/>').dialog({
            autoOpen: false,
            modal: true,
            title: data.title,
            buttons: [
                {
                    text: "Close",
                    click: function () {
                        $dlg.dialog('close');
                    }
                }
            ],
            close: function () {
                console.log("Destroy");
                $(this).dialog('destroy');
            }
        }).html('<p class="loading"/>');
        $dlg.dialog('open');
    }
    $(function(){
        $('.do_calculate').click(onCalculateOnClick);
    });
})(jQuery || django.jQuery);