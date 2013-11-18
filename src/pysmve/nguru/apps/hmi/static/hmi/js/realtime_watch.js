(function ($){
    $(function (){

        function showDialogForNode(node) {
            var tag = $(node).attr('tag');
            var buttons = [
                {
                    text: "Close",
                    click: function (){
                        $(this).dialog('close').dialog('destroy');
                    }
                }
            ];
            var toggle_89 = /([\d\w]{3})89([SI])([\w\d]{2})/;
            var match = toggle_89.exec(tag);
            if (match !== null) {
                buttons.unshift({
                    text: "Toggle",
                    click: function(){

                    }
                });
            }

            var dlg = $('<div/>').dialog({
                autoOpen: false,
                title: tag,
                modal: true,
                buttons: buttons
            });

            dlg.html($('<b>').text('TAG: '+tag));
            $(dlg).dialog('open');
            // debugger;
        }

        function isGroup(elem) {
            try {
                return (elem.get(0).tagName == 'g');
            } catch (e) {}
            return false;
        }

        function applyChanges(node, updates) {
            //console.log(arguments);
            // Aplicación recursiva de atributs a grupos
            $node = $(node);
            if (isGroup($node)) {
                return $.each($('path, rect', $node), function (index, elem){
                    applyChanges(elem, updates);
                });
            }
            $.each(updates, function (attribute, value){
                if (attribute == 'text') {
                    // Redondeo
                    if (value.indexOf('.')>-1){
                        value = parseFloat(value).toFixed(2);
                    }
                    $node.text(value);
                } else {
                    $.each(updates, function (key, value){
                        $node.css(key, value);
                        //node.css('fill-opacity', 1);
                    });
                }
            });
        }


        var last_update = null;
        var queryArguments = {};


        function setQueryParams(obj){
            queryArguments = obj || {};
        }

        function updateQueryParams(obj) {
            $.extend(queryArguments, obj || {});
        }

        function getQueryParamsEncoded() {
            var str = [];
            for(var p in queryArguments) {
                var value = queryArguments[p];
                if (value === null) {
                    continue;
                }
                str.push(encodeURIComponent(p) + "=" + encodeURIComponent(value));

            }
            return str.join("&");
        }


        function getSVGUpdatesUrl(extra_args){
            var baseUrl = Urls.api_dispatch_list('v1', 'svgelement');
            updateQueryParams({'last_update': last_update});
            var url = baseUrl + '?' + getQueryParamsEncoded();
            console.info("Looking for updates", decodeURIComponent(url));
            return url;
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
            SMVE.updateButton.click();
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

        var _svg = null;

        function setCurrentSVG(svg) {
            var $svg_attributes = $('#base', svg.root());
            var $container_div = $(svg.root().parentElement);
            var page_color = $svg_attributes.attr('pagecolor');
            //var height = $svg_attributes.attr('inkscape:window-height');
            var height = $(svg.root()).attr('height');
            $container_div.css({'background': page_color, 'height': height+'px'});

            _svg = svg;
        }

        function getCurrentSVG() {
            return _svg;
        }

        function updatesReceived(data, status) {
            var objs = data.objects,
                count = data.objects.length, // The same as data.meta.count (Tastypie)
                i,
                attributes = ['fill', 'color', 'text'],
                last_update;

            console.info("Applying", count, "changes");

            for (i=0; i<count; i++){
                var obj = objs[i];
                //console.log(obj)
                var node = $('[tag='+obj.tag+']', getCurrentSVG().root());
                if (node.length) {
                    var updates = {};
                    updates['text'] = obj.text;
                    $.extend(updates, obj.style);
                    applyChanges(node, updates);
                }
            }

            if (count > 0){
                if (count > 1) {

                    // Update last update
                    var update_timestamps = $.map(objs, function (record){
                        return new XDate(XDate.parse(record.last_update));
                    });
                    update_timestamps.sort();
                    last_update = update_timestamps[update_timestamps.length-1];
                } else {
                    last_update = new XDate(XDate.parse(objs[0].last_update));
                }

                last_update = last_update.toString('yyyy-MM-dd HH:mm:ss.ffffff');
                updateQueryParams({last_update__gt: last_update});
            }
            // Scheddule new function call
            updatesTimeOutID = window.setTimeout(update, SMVE.updateInterval);
        }

        updatesTimeOutID = null;

        function update(){
            if (typeof(SMVE.updateInterval) == 'undefined') {
                SMVE.updateInterval = 3000;
            }

            if (!SMVE.update) {
                return;
            }
            // Apply changes taken from the REST resource

            var xhr = $.ajax({
                url: getSVGUpdatesUrl(),
                success: updatesReceived,
                error: showRESTErrorDialog
            });
        }

        function createMiniAlarmGrid(){
            $('#mini-alarm').jqGrid({
                url: '/api/v1/event/?format=json&limit=4',
                datatype: "json",
                height: 60,
                autowidth: true,
                hidegrid: false,
                colNames:['ID', 'Fecha', 'Descripción', 'Atención',],
                colModel:[
                    {name:'id',index:'id', width:60, hidden: false},
                    {
                        name:'timestamp',
                        index:'timestamp',
                        width:90,
                        //sorttype:"date",
                        formatter: "date",
                        formatoptions: {
                            //newformat: 'd/m/Y H:i:sO'
                            //srcformat: 'YYYY-MM-DDTHH:mm:ss'
                            //,

                            //newformat: 'l F d, Y g:i:s.u A'
                        }
                    },
                    {name:'texto',index:'texto', width:100},
                    {
                        name:'timestamp_ack',
                        index:'timestamp_ack',
                        width:80,
                        align:"right",
                        sorttype:"date"
                    }
                ],
                jsonReader: {
                    repeatitems : false,
                    id: "0",
                    root: 'objects'
                },

                multiselect: false,
                caption: "Últimas alarmas",
                afterInsertRow: function (id, data) {
                    if (!data.timestamp_ack) {
                        $('#'+id).css('background', '#dec');
                        console.log(data.timestamp);
                    }
                },
                onSortCol: function (){
                    console.log(arguments);
                },
                serializeGridData: function (postData)
                {
                    // prepare data for Tatsypie format
                    var pdat = $.extend({}, postData);

                    // sorting / ordering
                    if (typeof pdat.sidx != 'undefined' && pdat.sidx != '')
                    {
                        pdat.order_by = pdat.sidx.replace('.', '__');
                        if (pdat.sord !== 'undefined')
                                            if (pdat.sord.toLowerCase() == 'desc')
                                            pdat.order_by = '-' + pdat.order_by;
                    }

                    // filtering
                    if (pdat.filters)
                    {
                            var filters = jQuery.parseJSON(pdat.filters);
                            var ops = {
                                        'eq': 'iexact',
                                        'lt': 'lt',
                                        'le': 'lte',
                                        'gt': 'gt',
                                        'ge': 'gte',
                                        'bw': 'istartswith',
                                        'in': 'in',
                                        'ew': 'iendswith',
                                        'cn': 'icontains',
                                        'dt': false, // special value used by date fields. don't append anything to search condition.
                                    }
                            $.each(filters.rules, function(idx, rule){
                                    var op = (rule['op'] in ops) ? ops[rule['op']] : 'icontains';
                                    var fieldname = rule['field'];
                                    if (op !== false)
                                        fieldname += '__' + op;
                                    pdat[fieldname] = rule['data'];
                            });
                    }
                    delete pdat.filters;
                    delete pdat.sord;
                            delete pdat.sidx;

                    return pdat;
                }
            });
        }

        function createAlarmGrid() {
            var alarmGrid = $('#alarm-grid').jqGrid({
                datatype: "local",
                height: 60,
                autowidth: true,
                hidegrid: false,
                colNames:['ID','Fecha', 'Descripción', 'Atención',],
                colModel:[
                    {name:'id',index:'id', width:60, sorttype:"int"},
                    {name:'invdate',index:'F', width:90, sorttype:"date"},
                    {name:'name',index:'name', width:100},
                    {name:'amount',index:'amount', width:80, align:"right",sorttype:"float"}
                ],
                multiselect: true,
                caption: "Alarmas del Sistema de Medición de Variables Eléctricas"
            });
            return alarmGrid;
        }

        function createTabs() {
            $("body").animate({ 'padding-top': 0}, 'slow');
            $('#tabs').tabs({
              activate: function (event, ui){
                var tab_id = ui.newPanel.attr('id');

                switch (tab_id) {

                    case 'tab-alarmas':
                        if (typeof(SMVE.alarmGrid) == 'undefined') {
                            SMVE.alarmGrid = createAlarmGrid();
                        }
                        break;

                    case 'tab-volver':
                        window.location = '/';
                        break;
                }
              }
            });
            $('.navbar-fixed-top').slideUp('slow');
        }

        function updateToggle(event) {
            if (typeof(event) != 'undefined') {
                event.preventDefault();
            }
            SMVE.update = !SMVE.update;
            if ($(this).is('a')) {
                $(this).text((SMVE.update)?("Update: ON"):("Update: OFF"));
            }
        }
        /* Initializes buttons
         */
        function setupExtraWidgets() {
            if (typeof(SMVE.updateButton)) {
                // Initialize update button trigger
                SMVE.updateButton = $('#update_toggle');
                SMVE.updateButton.button().click(updateToggle);
            }
        }

        function setUpdatesEnabled(enabled) {
            console.info("Set updates", (enabled)?("enabled"):("disabled"));
            if (enabled) {
                SMVE.enabled = true;
                update(); // Call the first time
            } else {
                if (updatesTimeOutID) {
                    console.debug("Clearing timeout funciton for updates");
                    window.clearTimeout(updatesTimeOutID);
                }
                SMVE.enabled = false;
            }
        }

        function svgScreenLoaded(svg) {
            var parent = svg._svg.parentElement;
            $(parent).height(svg._height());
            $('[tag]', svg.root()).click(function (){
                showDialogForNode(this);
            });
            setCurrentSVG(svg);
            setUpdatesEnabled(true);
        }

        function changeScreen(){
            var svg_pk = $(this).val();
            var url = Urls.svg_file(svg_pk);
            setUpdatesEnabled(false);

            setQueryParams({
                format: 'json',
                svgscreen__pk: svg_pk,
                enabled: true
            });

            console.info("Loading", url);
            $('#svg').removeClass('hasSVG').find('svg').remove();
            $('#svg').svg({
                loadURL: url,
                onLoad: svgScreenLoaded
            });
        }

        function bindSelectForScreens(){

            $('#id_svg_screen').bind('change', changeScreen);
        }

        function loadInitialScreen() {
            console.info("Initial screen");
            changeScreen.call($('#id_svg_screen'));
        }

        function init() {
            // AMD Namespace
            if (typeof(SMVE) == "undefined"){
                SMVE = {};
            }
            setupExtraWidgets();
            createTabs();
            bindSelectForScreens();
            createMiniAlarmGrid();
            loadInitialScreen();
            //update();
        }

        $(init);
    });


})(jQuery);