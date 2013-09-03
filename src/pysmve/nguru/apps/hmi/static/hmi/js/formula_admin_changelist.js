(function($){
    $(function(){
        //alert($.fn.jquery);
        $('.svg_popup').click(function (event){
            event.preventDefault();
            var $this = $(this),
                title = $this.attr('tag'),
                options = {
                    modal: true,
                    title: title,
                    autoOpen: false,
                    close: function(){
                        $(this).dialog('destroy');
                    }
                },
                $dlg = $('<div/>').dialog(options);
                $dlg.dialog('open');

        });
    });
})(jQuery || django.jQuery);