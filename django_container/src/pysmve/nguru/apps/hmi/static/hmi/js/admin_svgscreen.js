(function ($){
    $(function () {

        function showTagsInDialog (event) {
            console.log(this)
            event.preventDefault();
            var content = $(this).parents('span').find('ul').clone();
            var $dlg = $('<div/>').dialog({
                title: 'Tags',
                autoOpen: false
            });
            $dlg.html(content);
            $dlg.dialog('open');
            return false;
        }

        $('.show_tags').bind('click', showTagsInDialog);
    });
})(window.jQuery || django.jQuery);
