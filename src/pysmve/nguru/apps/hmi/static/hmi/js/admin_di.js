(function  ($) {


    function showGenerateEventDialog (event) {
        event.preventDefault();
        var $this = $(this);

        var $dlg = $('<div/>').dialog({
            modal: true,
            title: $this.attr('data-dialog-title') || 'No title',
            width: '50%',
            autoOpen: false,
            close: function () {
                $dlg.dialog('destroy');
            },
            buttons: [
                {
                    'text': 'Generar',
                    'click': function () {
                        $dlg.html('Generando...');
                        //debugger;
                        var buttons = $dlg.parents('.ui-dialog').find('.ui-dialog-buttonpane button');
                        buttons.button('option', 'disabled', true);

                    }
                },
                {
                    'text': 'Cerrar',
                    'click': function () {
                        $dlg.dialog('close');
                    }
                }
            ]
        });
        $dlg.html('Generar evento para <emph>'+$this.attr('data-dialog-description')+
                  '</emph>');
        $dlg.dialog('open');
        return false;
    }

    function init() {
        $('.generate_event').click(showGenerateEventDialog);
    }

    $(init);
})(window.jQuery || django.jQuery);