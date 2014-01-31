(function () {


    String.prototype.toProperCase = function () {
        return this.replace(/\w\S*/g, function(txt){
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        });
    };

    function objectsToTableInnerHTML(opts) {
        var obects = opts.objects || [],
            columns = opts.columns || [],
            formatters = opts.formatters || {},
            titles = opts.titles || {};
        var headers = [];

        for (var i=0; i<columns.length; i++) {
            var name = columns[i],
                title = null;
            if (name in titles) {
                title = titles[name];
            } else {
                title = name.toProperCase();
            }
            headers.push(title);
        }

        var body = '<tr><th>'+(headers.join('</th><th>'))+'</th></tr>';

        for (var i=0; i < obects.length; i++) {
            var row = [];
            var current = obects[i];
            if (columns.indexOf('index') > -1) {
                current['index'] = i + 1;
            }
            for (var j=0; j<columns.length; j++) {
                var column_name = columns[j];
                var column_value = current[column_name];
                if (formatters.hasOwnProperty(column_name)) {
                    column_value = formatters[column_name](column_value, current);
                }
                row.push(column_value);
            }
            body += '<tr><td>' + row.join('</td><td>') + '</td></tr>';
        }
        return body;

    }

    function createDialogForAIinDate() {
        var $this = $(this);
        var $tr = $this.parents('tr');
        var ai__id = $tr.attr('data-ai-pk'),
            ai__description = $tr.attr('data-ai-description');
        var start_date =  new XDate(XDate.parse($this.attr('data-ai-date')));
        var opts = {
            modal: true,
            width: "80%",
            height: 400,
            title: '%s: %s'.format(start_date.toString('dd-MM-yyyy'), ai__description),
            buttons: [
                {
                    text: "Cerar",
                    click: function () {
                        $(this).dialog('close').dialog('destroy');
                    }
                }

            ]
        };
        var $dlg = $('<div/>').dialog(opts);
        $dlg.html('<p class="loading">&nbsp;</p>');

        var url = Urls.api_dispatch_list('v1', 'energy');

        var end_date = new XDate(start_date).addDays(1).addMilliseconds(-1);

        var queryUrl = new QueryObj({
            format: 'json',
            limit: 200,
            ai__id: ai__id,
            order_by: 'timestamp',
            timestamp__gte: start_date.toString('yyyy-MM-dd HH:mm:ss'),
            timestamp__lte: end_date.toString('yyyy-MM-dd HH:mm:ss')
        }, url);

        console.log("Querying", queryUrl.toString());

        var request = $.ajax({
            method: 'GET',
            url: queryUrl.toString()
        });

        request.then(function (data, state, resp){
            $dlg.find('p.loading').remove();
            $dlg.css('max-height', '80%').css('overflow-y', 'scroll');
            var table = $('<table/>').addClass('day-measures-ai').html(
                objectsToTableInnerHTML({
                    objects: data.objects,
                    columns: ['index', 'timestamp', 'value', 'repr_value'],
                    titles: {
                        'index': '#',
                        'value': 'Cuentas',
                        'repr_value': 'Valor de Ingeniería'
                    },
                    formatters: {
                        'timestamp': function (text) {
                            return new XDate(text).toString('HH:mm:ss');
                        }
                    }
                })
            );
            $dlg.append(table);
            $dlg.dialog("option", "position", "center");
        }, function () {
            console.error("Plotting", arguments);
        });
    }

    $(function () {
        $('td.measure').hover(function () {
            $(this).addClass('hovered');
        }, function () {
            $(this).removeClass('hovered');
        }).click(createDialogForAIinDate);


        $('.comaster_title').click(function () {
            $(this).next('table').toggle();
        })
    });
})();