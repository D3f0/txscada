(function ($){
    $(function (){

        var svg = null;

        var formulas = {};

        // var xhr = $.ajax('/api/v1/formula?format=json&limit=500');
        // function retrieveFormulas (data) {
        //     $.each(data.objects, function () {
        //         console.log(this);
        //     });
        // }
        // xhr.then(retrieveFormulas);

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
        function serialize(obj) {
          var str = [];
          for(var p in obj)
             str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
          return str.join("&");
        }
        var last_update=null;

        function getSVGUpdatesUrl(extra_args){
            extra_args = extra_args || {};
            var baseArgs = {
                format: 'json',
                order_by: '-last_update',

            }

            if (typeof extra_args != "object") {
                extra_args = {};
            }
            if (last_update) {
                extra_args.last_update = last_update;
            }

            var baseUrl = '/api/v1/svgelement/';
            var args = $.extend({}, baseArgs, extra_args);
            var url = baseUrl + '?' + serialize(args);
            console.log(url);
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

        function update(){
            if (typeof(SMVE.updateInterval) == 'undefined') {
                SMVE.updateInterval = 1000;
            }
            window.setTimeout(update, SMVE.updateInterval);
            if (!SMVE.update) {
                return;
            }
            // Apply changes taken from the REST resource
            $.ajax({
                    url: getSVGUpdatesUrl(),
                    success: function (data, status){
                        var objs = data.objects;
                        var attributes = ['fill', 'color', 'text'];

                        $.each(objs, function (idx, obj) {
                            //console.log(obj)
                            var node = $('[tag='+obj.tag+']', svg.root());
                            if (node.length)  {
                                var updates = {};
                                updates['text'] = obj.text;
                                $.extend(updates, obj.style);
                                applyChanges(node, updates);
                            }
                        });

                    },
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

        function createUpdateIntervalSlider() {

            $( "#SMVE-update-interval" ).slider({
                value: 1000,
                min: 250,
                max: 10000,
                step: 250,
                value: SMVE.updateInterval,
                slide: function( event, ui ) {
                    //$( "#amount" ).val( "$" + ui.value );
                    $('#update_interval').text(ui.value);
                    SMVE.updateInterval = ui.value;
                }
            });
            console.log($( "#SMVE-update-interval" ));
            return false;
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

                    case 'tab-configuracion':
                        createUpdateIntervalSlider();
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


        function svgScreenLoaded(svg) {
            var parent = svg._svg.parentElement;
            $(parent).height(svg._height());
            $('[tag]', svg.root()).click(function (){
                showDialogForNode(this);
            });
        }

        function changeScreen(){
            var svg_pk = $(this).val();
            var url = Urls.svg_file(svg_pk);
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