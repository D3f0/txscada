$(function (){
    var URL_DATE_FORMAT = 'yyyy-MM-dd';

    var $date_from = $('#id_date_from'),
        $date_to = $('#id_date_to'),
        $comaster_select = $('#id_comaster'),
        $channel_select = $('#id_channel'),
        $ai_select = $('#id_ai'),
        $plot_button = $('#id_plot'),
        $export_button = $('#id_export');

    $date_from.datepicker({
        defaultDate: "+1d",
        changeMonth: true,
        numberOfMonths: 2,
        maxDate: new Date(),
        dateFormat: 'dd/mm/yy',
        onClose: function( selectedDate ) {
            $date_to.datepicker( "option", "minDate", selectedDate );
            if ($date_to.datepicker('getDate') == null) {
                $date_to.datepicker('setDate', selectedDate);
            }
        }
    });
    $date_to.datepicker({
        defaultDate: "+1d",
        changeMonth: true,
        numberOfMonths: 2,
        maxDate: new Date(),
        dateFormat: 'dd/mm/yy',
        onClose: function( selectedDate ) {
            $date_from.datepicker( "option", "maxDate", selectedDate );
        }
    });

    var all_ai_options = $ai_select.find('option').clone();

    function filter_ais() {
        var current_comaster = $comaster_select.val();
        var current_channel = $channel_select.val();
        console.log(current_comaster, current_channel);
        $ai_select.find('option').remove();
        var count = 0;
        $.each(all_ai_options, function () {
            var $opt = $(this);
            if ($opt.attr('data-channel') == current_channel &&
                $opt.attr('data-comaster-pk') == current_comaster
            ) {
                $ai_select.append($opt.clone());
                count += 1;
            }
        });
        if (count < 1) {
            $ai_select.attr('disabled', 'disabled');
        } else {
            $ai_select.removeAttr('disabled');
        }
    }

    $comaster_select.change(filter_ais);
    $channel_select.change(filter_ais);

    /* NVD3 Plot
    */
    var duration = 300;

    function redraw(data) {
       nv.addGraph(function () {
           chart = nv.models.lineChart()
                          .x(function (d) { return new XDate(d.x) })
                          .y(function (d) { return d.y })
                           .useInteractiveGuideline(true);
                          //.color(d3.scale.category10().range());
            chart.xAxis.tickFormat(function (d) {
                var date = new Date(d),
                    retval = '';
                    hour = date.getHours(),
                    minute = date.getMinutes();
                // Dates

                if (hour == 23 && minute == 59) {
                    retval = '00:00';
                } else {
                    retval = d3.time.format('%d/%m %H:%M')(date);
                }

                return retval;
            });

            chart.yAxis.tickFormat(function (v) {
                return v.toFixed(3) + data[0].unit;
            });
            // chart.yAxis
            //     .tickFormat(d3.format(',.1%'));

            var svg = d3.select('#plot svg');
            svg.datum(data);
            svg.transition().duration(duration);
            svg.call(chart);
            console.log(data);

            nv.utils.windowResize(chart.update);

            return chart;
        });
    }
    // Buttons

    $plot_button.click(function (event) {
        event.preventDefault();
        // $('form').block({message: "Processing"});
        // window.setTimeout(function () {
        //     $('form').unblock();
        // },1000);

        // Get date boundaries, correcting hour:minute:seconds.milliseconds
        var d1 = new XDate($date_from.datepicker('getDate')).setHours(0)
                            .setMinutes(0).setSeconds(0).setMilliseconds(0),
            d2 = new XDate($date_to.datepicker('getDate')).setHours(23)
                            .setMinutes(59).setSeconds(59).setMilliseconds(999);

        console.log('Date boundaries from: '+ d1 +' to:'+ d2);

        try {
            var from = d1.toString(URL_DATE_FORMAT);
            var to = d2.toString(URL_DATE_FORMAT);
        } catch (e) {
            alert("Fecha inválida");
            return;
        };

        var ai_pk = $ai_select.val();
        if (!ai_pk) {
            alert("Medidor inválido");
            return;
        } else {
            var url = Urls.max_energy_period(ai_pk, from, to);
            $.ajax({
                url: url,
                success: function (data, status, xhr) {
                    $('#max_energy_period').html(data.value+" MVA");

                },
                error: function () {
                    $('#max_energy_period').html("No se encontró valor valor");
                }
            });
        }

        var $dlg = $('<div>').dialog({
            modal: true,
            title: "Obteniendo datos",
        }).html('<p class="loading">Aguarde mientras se reucperan los datos...</p>');

        var url = Urls.api_dispatch_list('v1', 'energy');

        var queryUrl = new QueryObj({
            format: 'json',
            limit: 5000,
            order_by: 'timestamp',
            ai__id: $ai_select.val(),
            code: 0, // 1 Code is for totalizer measures
            timestamp__gte: d1.toISOString(),
            timestamp__lte: d2.toISOString()
        }, url);

        console.log("Querying "+unescape(queryUrl));
        $.ajax({
            url: queryUrl,
            success: function (data, xhr) {
                $dlg.dialog('close');
                // Trim select's option text
                var key = $.trim($ai_select.find('option:selected').text());
                redraw([
                    {
                        "key": key,
                        "values": energyResponseToPoints(data),
                        "unit": data.meta.unit
                    }
                ]);
            },
            error: function () {
                $dlg.dialog('close');
                SMVE.errors.showRESTErrorDialog(arguments); // XHR VAlues
            }
        });
    });

    function energyResponseToPoints(jsonResponse) {
        if (!jsonResponse.hasOwnProperty('objects')) {
            throw new Exception("Invalid Tastypie response");
        }
        return $.map(jsonResponse.objects, function (record, index) {
            return {
                x: new XDate(record.timestamp),
                y: record.eng_value
            }
        });
    }

    $export_button.click(function (event) {
        event.preventDefault();
        var d1 = new XDate($date_from.datepicker('getDate')),
            d2 = new XDate($date_to.datepicker('getDate'));
        try {
            var from = d1.toString(URL_DATE_FORMAT);
            var to = d2.toString(URL_DATE_FORMAT);
        } catch (e) {
            alert("Fecha inválida");
            return;
        };

        var ai_pk = $ai_select.val();
        if (!ai_pk) {
            alert("Medidor inválido");
            return;
        } else {
            var url = Urls.energy_export(ai_pk, from, to);
            window.open(url, '_blank');
        }
    });
    // Filter intial
    filter_ais();

    $('#id_form_fields_hide').click(function () {
        console.log("FUu");
        $('.span6.toggleable').toggle();
    })
});