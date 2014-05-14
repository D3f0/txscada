(function ($){

    // AMD Namespace
    if (typeof(SMVE) == "undefined"){
        SMVE = {};
    }
    // Taken from https://groups.google.com/forum/#!topic/d3-js/qSwsOYMo9mA
    d3.selection.prototype.size = function() {
        var n = 0;
        this.each(function() { ++n; });
        return n;
    };

    $(function (){
        // Some of these variables are exposed to the SMVE namespace
        var alarmGrid,
            miniAlarmGird,
            tagResource = {},
            screenResource = {},
            currentScreenUri = null,
            // Extra widgets
            btnJumpToUpperScreen = null,
            btnChangeSVGBackground = null;

        function fatalError(msg, description) {
            return alert(msg);
        }
        // TODO: Check if underscore or other library provides this util func
        function grepObjectContent(anObject, filterFunc) {
            var retval = null;
            $.map(anObject, function (internalValue, attrName) {
                if (filterFunc.call(internalValue, internalValue, attrName)) {
                    retval = internalValue;
                    return false; // Cut iteration
                }
            });
            return retval;
        }

        function makeInkscapeSVGResponsive (svgNode)  {
            var h = svgNode.attributes['height'].value;
            var w = svgNode.attributes['width'].value;
            svgNode.setAttribute('viewBox', '0 0 '+w+' '+h);
            console.log(svgNode.attributes['viewBox'].value);
            svgNode.setAttribute('preserveAspectRatio', "xMaxYMid meet");
        }

        function useSVGColorOnContainer(svgNode) {
            var svg = d3.select(svgNode);
            var page_color = svg.select('[pagecolor]').attr('pagecolor');
            var element = svg.node().parentElement;
            d3.select(element).style('background-color', page_color);
        }

        function loadTagResource() {
            // SVGElement
            return $.ajax({
                method: 'GET',
                url: Urls.api_dispatch_list('v1', 'svgelementdetail'),
            }).then(function (data, state, resp) {
                tagResource = {};
                $.each(data.objects, function (obj, index){
                    tagResource[this.tag] = this;
                });
            }, function () {
                fatalError("Falla al obtener recurso");
            });
        }

        function loadScreenResource() {
            // SVGScreen
            return $.ajax({
                method: 'GET',
                url: Urls.api_dispatch_list('v1', 'svgscreen'),
            }).then(function (data, state, resp) {
                screenResource = {};
                $.each(data.objects, function (obj, index){
                    screenResource[this.resource_uri] = this;
                });
            }, function () {
                fatalError("Falla al obtener recurso");
            });
        }

        /** Crear diálogo para tag */

        function createDialogForTag(node, nodeData) {
            var $dlg = $('<div/>').dialog({
                autoOpen: false,
                title: nodeData.tag,
                modal: true,
                width: '40%',
                buttons: [
                    {
                        text: "Close",
                        click: function (){
                            $(this).dialog('close');
                        }
                    }
                ],
                close: function () {
                    $(this).dialog('destroy');
                }
            });
            var html = '<b>%s</b> <i>%s</i></br>'.format(
                nodeData.tag,
                nodeData.description
            );
            $dlg.html(html);
            $dlg.dialog('open');
        }

        function createDialogForTextToggle(node, nodeData) {
            var text = SMVE.getTag(nodeData.tag).text;
            var options = nodeData.linked_text_change;
            var newText;
            // Ugly lookup (Array was better)
            for (var key in options) {
                if (key == text)
                    continue;
                newText = key;
            }

            var $dlg = $('<div/>').dialog({
                title: "Confirmacón de cambio manual",
                autoOpen: false,
                modal: true,
                width: '40%',
                close: function () {
                    $(this).dialog('destroy');
                },
                buttons: [
                    {
                        text: "Cambiar a %s".format(options[newText]),
                        click: function () {
                            var that = this;
                            var url = Urls.api_dispatch_detail('v1',
                                                               'svgelement',
                                                               nodeData.id);
                            // Buttons
                            $(".ui-dialog-buttonpane button").button("disable");
                            $(".ui-dialog-buttonpane button:contains('%s')".format(options[newText])
                                ).text("Confirmando...");
                            // Make ajax call to change text
                            var xhr = $.ajax({
                                url: url,
                                method: 'PUT',
                                processData: false,
                                contentType: 'application/json',
                                data: JSON.stringify({text: newText})
                            });
                            xhr.then(function () {
                                try {
                                    SMVE.getTag(nodeData.tag).text = newText;
                                    if (node.tagName == 'text') {
                                        $(node).text(newText);
                                    }
                                    $dlg.dialog('close');

                                } catch (e) {
                                    console.error(e);
                                }
                            }, function (xhr, status, response) {
                                $(".ui-dialog-buttonpane ui-state-default").remove();
                                $(".ui-dialog-buttonpane button").button("enable");
                                $dlg.dialog('option', 'title', status);
                                $dlg.html('<pre>%s</pre>'.format(response));

                            });

                        }
                    },
                    {
                        text: "Close",
                        click: function () {
                            $(this).dialog('close');
                        }
                    }
                ]
            });
            var html = ('<b>%s</b> <i>%s</i></br>' +
                        '<b>¿Confirma cambiar el estado %s a %s?</b>').format(
                        nodeData.tag,
                        nodeData.description,
                        options[text],
                        options[newText]
                        );
            $dlg.html(html);
            $dlg.dialog('open');
        }

        function clickOnSVGElement(node, nodeData) {
            var tag = d3.select(this).attr('tag'),
                nodeData;

            if (d3.select(this).selectAll('[tag='+tag+']').size() > 0) {
                console.log("Nested Elements!");
                var n = noty({
                    text: "Nested elements %s".format(tag)
                });
                return;
            }
            // REST reource cache, Tastypie
            nodeData = SMVE.getTag(tag);

            // If there's no SVGElement model
            if (nodeData === undefined) {
                console.error("No info for", tag, this || "No tag");
                if (SMVE.hasPermission('hmi.can_debug_screen')) {
                    var n = noty({
                        text: "No SVGElement data for <b>%s</b>".format(tag),
                        type: "warning"
                    });
                }
                return;
            }

            if (nodeData.on_click_text_toggle) {
                return createDialogForTextToggle(node, nodeData);
            }
            if (nodeData.on_click_jump !== null) {
                return setCurrentScreenUri(nodeData.on_click_jump);
            }
            createDialogForTag(nodeData.tag, nodeData);

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
            var $node = $(node);
            if (isGroup($node)) {
                return $.each($('path, rect', $node), function (index, elem){
                    applyChanges(elem, updates);
                });
            }
            $.each(updates, function (attribute, value){
                if (attribute == 'text') {
                    // TODO: Move to serverside(formulas)
                    if (value.indexOf(' ')==-1 && value.indexOf('.')>-1){
                        value = parseFloat(value).toFixed(2);
                    }
                    $node.text(value);
                } else {
                    $.each(updates, function (key, value){
                        // Interactive zone
                        if ($(node).attr('tag') == 'nopaint') {
                            //console.info("Excluding node", node, "because nopaint");
                            return;
                        }
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
        /**
         * Low level function for SVG/Markup interaction
         */
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

        function dateFormatter(cellvalue, options, rowObject) {
            var date = new XDate(XDate.parse(cellvalue));
            return date.toString('yyyy-MM-dd HH:mm:ss.fff');
        }
        // Same Model for both grids!
        var alarmsColModel = [
            {name:'id',index:'id', width:60, hidden: true},
            {
                name:'timestamp', index:'timestamp', width:90,
                //sorttype:"date",
                formatter: dateFormatter,
                label: "Fecha"

            },
            {
                name: 'tag',
                index: 'tag',
                label: 'TAG',
                sortable: false,
                width: 50
            },
            {
                name:'texto',
                index:'texto',
                width:100,
                sortable: false,
                label: "Descripción"
            },
            {
                name:'timestamp_ack',
                index:'timestamp_ack',
                label: "Atención",
                width:80,
                align:"center",
                sorttype:"date",
                formatter: function (cellvalue, options, rowObject) {
                    var retval;
                    if (cellvalue) {
                        var date = new XDate(XDate.parse(cellvalue));
                        retval = date.toString('yyyy-MM-dd HH:mm:ss.fff');
                    } else {
                        retval = '<a href="#" data-resource-uri="'+
                                 rowObject.resource_uri + '"' +
                                 'onclick=SMVE.attendCell(this)>'+
                                 'Sin atención</a>';
                    }
                    return retval;
                }
            },
        ];

        function reloadAlarmGrids() {
            if (miniAlarmGird !== undefined) {
                miniAlarmGird.trigger("reloadGrid");
            }
            if (alarmGrid !== undefined) {
                alarmGrid.trigger("reloadGrid");
            }
        }

        function attendCell(link) {
            var $link = $(link);
            var resource_uri = $link.attr('data-resource-uri');

            var $dlg = $('<div/>').dialog({
                modal: true,
                autoOpen: false,
                width: "60%",
                title: "Atención de eventos",
                buttons: [
                    {
                        text: "Atender",
                        click: function() {

                            var xhr = $.ajax({
                                url: resource_uri,
                                method: 'PUT',
                                processData: false,
                                contentType: 'application/json',
                                data: JSON.stringify({timestamp_ack: 'now'})
                            });
                            xhr.then(function () {
                                console.info("Se atendio el evento ", resource_uri);

                                reloadAlarmGrids();

                                $dlg.dialog('close');

                            }, function (xhr, error, status) {
                                var error = JSON.parse(xhr.responseText);
                                var developer = SMVE.hasPermission('mara.change_comaster');
                                $dlg.dialog('option', 'title', "Ocurrió un error");
                                $dlg.html('');
                                $dlg.append($('<p>').text(
                                        "El servidor respondio: %s".format(status)
                                    )
                                );
                                if (developer) {
                                    $dlg.append(

                                        $('<pre>').text(error.traceback)
                                    );
                                }

                                //debugger;
                                $(".ui-dialog-buttonpane button").button("disable");
                                $(".ui-dialog-buttonpane button.ui-state-focus").button("disable");
                                if (!developer) {
                                    window.setTimeout(function () {
                                        $dlg.dialog('close');
                                    }, 1000);
                                }
                            });

                        }
                    },
                    {text: "Cerrar", click: function(){
                        $dlg.dialog('close');
                    }},
                ],
                close: function () {
                    $(this).dialog('destroy');
                }
            });
            $dlg.html("<p>Está a punto de notificar la atención de la alarma</p>"+
                "");

            $dlg.dialog('open');
        }

        // Common configuration for both alarm grids
        var jqGridAlarmCommonConfig = {
            datatype: "json",
            autowidth: true,
            //colNames:['ID', 'Fecha', 'Descripción', 'Atención',],
            colModel: alarmsColModel,
            hidegrid: false,
            jsonReader: {
                repeatitems : false,
                id: "0",
                root: 'objects',
                page: function (obj) {
                    return (obj.meta.offset / obj.meta.limit) + 1;
                },
                total: function (obj) {
                    return Math.ceil((obj.meta.total_count / obj.meta.limit));

                },
                records: 'meta.total_count'
            },
            serializeGridData: TastyJQGrid.serializeGridData,
            onPaging: function (pagging) {
                var request = pagging.split('_')[0];
                console.log("Requested page is", request);
                var params = $(this).jqGrid('getGridParam');
                var postData = params.postData;
                //debugger;

                switch (request) {
                    case 'first':
                        postData.offset = 0;
                        break;
                    case 'prev':
                        postData.offset = params.reccount * (params.page-2);
                        break;
                    case 'user':
                        console.info("Do not paginate by this");
                        break;
                    case 'next':
                        postData.offset = params.reccount * (params.page);
                        break;
                    case 'last':
                        var last = $(this).jqGrid('getGridParam', 'lastpage');
                        postData.offset = params.reccount * (last-1);

                }
                console.info(postData.offset);
                //alarmGrid.jqGrid('setGridParam', {postData: filters}).trigger('reloadGrid');
                //return 'stop';
            }
        };

        function createMiniAlarmGrid(){
            miniAlarmGird = $('#mini-alarm');
            //$alarmCountSelect.c

            var url = Urls.api_dispatch_list('v1', 'event');

            var queryUrl = new QueryObj({
                format: 'json',
                limit: 5,
                order_by: '-timestamp',
                timestamp_ack__isnull: true
            }, url);

            miniAlarmGird.data('queryUrl', queryUrl);

            miniAlarmGird.jqGrid($.extend(
                    {},
                    jqGridAlarmCommonConfig, {
                        url: queryUrl.toString(),
                        height: 'auto',
                        caption: "Últimos eventos sin atención",
                        afterInsertRow: function (id, data) {
                            if (!data.timestamp_ack) {
                                //$('#'+id).css('background', '#dec');
                                console.log(data.timestamp);
                            }
                        },
                        onSortCol: function (){
                            console.log(arguments);
                        }
                    })
            );

        }


        function createAlarmGrid() {
            alarmGrid = $('#alarm-grid');

            var url = Urls.api_dispatch_list('v1', 'event');

            var queryUrl = new QueryObj({
                format: 'json',
                limit: 20,
                order_by: '-timestamp'
            }, url);

            alarmGrid.data('url', queryUrl);

            var $filterForm = $('#alarm_filter_form');
            var $filterInputs = $filterForm.find('input[type=text]');
            $filterForm.find('.date').datepicker({
                dateFormat: 'yy-mm-dd'
            });

            alarmGrid.jqGrid($.extend({}, jqGridAlarmCommonConfig, {
                url: queryUrl.toString(),
                height: "80%",
                multiselect: true,
                caption: "Eventos del Sistema de Medición de Variables Eléctricas",
                // _beforeSubmit: function (postdata, formid) {
                //     debugger;
                //     return true;
                // },
                pager: '#alarm_pager'
            }));

            $filterForm.on('submit', function (event){
                event.preventDefault();

                var postData = alarmGrid.jqGrid('getGridParam', 'postData');

                $filterForm.find('input[type=text]').each(function (key, el){
                    var $el = $(el),
                        name = $el.attr('name'),
                        value = $el.val();
                    if (value === '') {
                        if (name in postData){
                            console.info("Removing key", name, "from filter postData");
                            delete postData[name];
                        }
                    } else {
                        postData[name] = value;
                    }
                });

                postData.offset = 0;

                alarmGrid.jqGrid('setGridParam', {postData: postData});
                alarmGrid.trigger('reloadGrid');

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
                        window.location = Urls.index();
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
            // if (typeof(SMVE.updateButton)) {
            //     // Initialize update button trigger
            //     SMVE.updateButton = $('#update_toggle');
            //     SMVE.updateButton.button().click(updateToggle);
            // }
            btnJumpToUpperScreen = $('#jump_to_upper_screen');
            btnJumpToUpperScreen.on('click', function (e){
                e.preventDefault();
                var parent = SMVE.getScreen(currentScreenUri).parent;
                if (parent !== null) {
                    setCurrentScreenUri(parent);
                }
            });
            btnChangeSVGBackground = $('#change_svg_background');
            btnChangeSVGBackground.on('click', function () {
                var svg_bg = $('#svg').css('background-color'),
                    body_bg = $('#svg').css('background-color'),
                    $svg_attributes = $('#base', svg.root());
                    svg_bg = $svg_attributes.attr('pagecolor');

            });
            $('#update_toggle').on('click', updateToggle);

            // Debug button to hillight tags
            btnJumpToUpperScreen.parent()
                .after('<div style="float: right;" >'+
                       '<input id="find-tag" type="text" placeholder="Buscar tag...">'+
                       +'<span id="tag-count" class="label">0</span>'+
                       '</div>');
            $('#find-tag').css('text-transform', 'uppercase').on('keyup', highlighTag);
        }

        // Debug function
        function highlighTag () {
            var tag = $(this).val();
            console.log(tag);
            if (tag.length < 2) {
                return;
            }
            console.log("Looking up for", tag);

            var elements = d3.select('svg').selectAll('[tag^='+tag+']');
            $('#tag-count').text(''+elements.size());
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
            var $container = $(this),
                svg = $container.find('svg').get(0);

            if (svg == 'undefined') {
                fatalError("No se pudo cargar la pantalla actual");
                return;
            }

            makeInkscapeSVGResponsive(svg);
            useSVGColorOnContainer(svg);

            d3.select(svg).selectAll('[tag],[jump-to]').on('click',
                                                           clickOnSVGElement);
            return;
            debugger;

            // Bind click
            $('[tag],[jump-to]', svg.root()).click(function (){
                var tag = $(this).attr('tag');
                clickOnSVGElement(this, SMVE.getTag(tag));
            });
            setCurrentSVG(svg);
            setUpdatesEnabled(true);
        }


        function setCurrentScreenUri(uri) {
            console.log('setCurrentScreenUri');

            var svg_screen = SMVE.getScreen(uri);
            var url = svg_screen.svg;
            console.info("Loading ", svg_screen.description,
                                     svg_screen.name,
                                     svg_screen.svg);

            if (svg_screen.parent === null) {
                $('#jump_to_upper_screen').attr('disabled', 'disabled')
                    .attr('title', 'Pantalla raíz');

            } else {
                $('#jump_to_upper_screen').removeAttr('disabled')
                    .attr('title', 'Pantalla no raíz');
            }

            setUpdatesEnabled(false);

            currentScreenUri = uri;

            setQueryParams({
                format: 'json',
                screen__id: svg_screen.id,
                enabled: true
            });

            $('.svg-container svg').remove();
            $('.svg-container').load(url, svgScreenLoaded);
            //$('#svg').removeClass('hasSVG').find('svg').remove();

            // $('#svg').svg({
            //     loadURL: url,
            //     onLoad: svgScreenLoaded
            // });
        }

        function findInitialScreenAndFireLoad() {
            try {
                var uri = grepObjectContent(screenResource,
                    function (o){
                        return o.parent === null;
                    }).resource_uri;
                setCurrentScreenUri(uri);
            } catch(error) {
                fatalError("No hay pantalla inicial definida");
            }

        }

        function init() {
            createTabs();
            $.when(
                loadTagResource(),
                loadScreenResource()
            ).done(
                findInitialScreenAndFireLoad
            );
            setupExtraWidgets();
            createMiniAlarmGrid();

            //update();
        }
        // API
        $.extend(SMVE, {
            attendCell: attendCell,
            getAlarmGrid: function () {
                return alarmGrid;
            },
            getMiniAlarmGrid: function () {
                return miniAlarmGird;
            },
            getTags: function() {
                return tagResource;
            },
            getTag: function (tag) {
                return tagResource[tag];
            },
            getScreen: function (resource_uri) {
                return screenResource[resource_uri];
            },
            hasPermission: function (permission) {
                return SMVE.perms.indexOf(permission) > 0;
            }
        });
        $(init);
    });


})(jQuery);