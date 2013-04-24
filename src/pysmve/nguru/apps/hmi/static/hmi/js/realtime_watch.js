(function ($){
    $(function (){

        var svg = null;

        function showDialogForNode(node) {
            var dlg = $('<div/>').dialog({
                autoOpen: false,
                title: $(node).attr('tag'),
                modal: true,
                buttons: [
                    {text: "Close",
                    click: function (){
                        $(dlg).dialog('close').dialog('destroy');
                    }}
                ]
            });
            $(dlg).dialog('open');
        }

        function setupSVGScreeen(){
            $('#svg').svg({
                loadURL: SMVE.svgURL,
                onLoad: function (loadedSVG) {
                    svg = loadedSVG;
                    $('[tag]', svg.root()).click(function (){
                        showDialogForNode(this);
                    });
                }
            });
        }

        function isGroup(elem) {
            try {
                return (elem.get(0).tagName == 'g');
            } catch (e) {}
            return false;
        }

        function applyChanges(node, updates) {
            $node = $(node);
            if (isGroup($node)) {
                return $.each($('path, rect', $node), function (index, elem){
                    applyChanges(elem, updates);
                });
            }
            $.each(updates, function (attribute, value){
                if (attribute == 'text') {
                    $node.text(value);
                } else {
                    $.each(updates, function (key, value){
                        $node.css(key, value);
                        //node.css('fill-opacity', 1);
                    });
                }
            });
        }

        function update(){
            if (typeof(SMVE.updateInterval) == 'undefined') {
                SMVE.updateInterval = 1000;
            }
            window.setTimeout(update, SMVE.updateInterval);
            if (!SMVE.update) {
                return;
            }
            $.ajax(SMVE.svg_pk, {
                success: function(data){
                    $.each(data, function (tag, updates){
                        var node = $('[tag='+tag+']', svg.root());
                        applyChanges(node, updates);
                    });
                }
            });
        }

        function createMiniAlarmGrid(){
            $('#mini-alarm').jqGrid({
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
                caption: "Últimas alarmas"
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

        function init() {
            // AMD Namespace
            if (typeof(SMVE) == "undefined"){
                SMVE = {};
            }

            createTabs();
            setupSVGScreeen();
            //$('#svg').hide();
            createMiniAlarmGrid();

            update();
        }

        $(init);
    });


})(jQuery);