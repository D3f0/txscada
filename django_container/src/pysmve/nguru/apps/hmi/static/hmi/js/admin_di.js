(function  ($) {


    function showGenerateEventDialog (event) {
        event.preventDefault();
        var $this = $(this),
            url = $this.attr('href');

        var $dlg = $('<div/>').dialog({
            modal: true,
            title: $this.attr('data-dialog-title') || 'No title',
            width: '50%',
            autoOpen: false,
            open: function () {
                $this.parents('tr').css('background', '#ccc');
            },
            close: function () {
                $this.parents('tr').css('background', '');
                $dlg.dialog('destroy');
            },
            buttons: [
                {
                    'text': 'Generar',
                    'click': function () {

                        var buttons = $dlg.parents('.ui-dialog').find('.ui-dialog-buttonpane button');
                        buttons.button('option', 'disabled', true);
                        var form_data = $dlg.find('form').serialize();
                        // Add CSRF token
                        form_data += '&csrfmiddlewaretoken=';
                        form_data += $('input[name=csrfmiddlewaretoken]').val();
                        //
                        $dlg.html('Generando evento de prueba...');
                        $.ajax({
                            url: url,
                            method: 'POST', // HTTP correct method
                            data: form_data,
                            success: function (response) {
                                $dlg.html(response);
                                buttons.button('option', 'disabled', false);
                                window.setTimeout(function () {
                                    $dlg.dialog('close');
                                }, 3000);
                            },
                            error: function (response, status, xhr) {
                                $dlg.html("Error", response, xhr);
                                window.setTimeout(function () {
                                    $dlg.dialog('close');
                                }, 500);
                            }
                        });

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
        $dlg.html('<p>Generar evento para <emph>'+$this.attr('data-dialog-description')+
                  '</emph></p>'+
                  '<form>'+
                  '<label for="new_event_value">value:&nbsp;</value>'+
                  '<select name="value" id="new_event_value">'+
                  '<option value="0">0</option>'+
                  '<option value="1">1</option>'+
                  '</select>'+
                  '</form>');
        $dlg.dialog('open');
        return false;
    }

    function init() {
        $('.generate_event').click(showGenerateEventDialog);
    }

    $(init);
})(window.jQuery || django.jQuery);