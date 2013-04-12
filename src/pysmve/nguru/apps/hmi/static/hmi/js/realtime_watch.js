(function ($){
    $(function (){

        function createTabs() {
            $("body").animate({ 'padding-top': 0}, 'slow');
            $('#tabs').tabs({
              activate: function (event, ui){

                if (ui.newPanel.attr('id') == 'mimic-tab-2') {
                    // SMVE.crearGrillaEventos('#grid-eventos');
                }
                if (ui.newPanel.is('> :last')){
                    window.location = '/';
                }
              }
            });
            $('.navbar-fixed-top').slideUp('slow');
        }
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
                colNames:['Inv No','Date', 'Client', 'Amount','Tax','Total','Fecha Atención'],
                colModel:[
                    {name:'id',index:'id', width:60, sorttype:"int"},
                    {name:'invdate',index:'F', width:90, sorttype:"date"},
                    {name:'name',index:'name', width:100},
                    {name:'amount',index:'amount', width:80, align:"right",sorttype:"float"},
                    {name:'tax',index:'tax', width:80, align:"right",sorttype:"float"},
                    {name:'total',index:'total', width:80,align:"right",sorttype:"float"},
                    {name:'notes',index:'notes', width:150, sortable:false, }
                ],
                multiselect: true,
                caption: "Manipulating Array Data"
            });
        }
        function init() {
            createTabs();
            setupSVGScreeen();
            //$('#svg').hide();
            createMiniAlarmGrid();
            window.setInterval(update, 1000);
        };
        $(init)
    });


})(jQuery);