// Punto de entrada a la aplicación
$(function  () {
    /**
    *
    */            
    
    $('#tabs').tabs();
    // Tabla de eventos
    $('#tabla-eventos').dataTable({
        bJQueryUI: true,
        bServerSide: true,
        sAjaxSource: "/eventos/",
        bProcessing: true
    });
    var config = datatables.COMaster;
    $.extend(config, {
       sAjaxSource: '/api/comaster/' 
    });
    console.log("Confiuracion del comaster es", config);
    $('#co-master').dataTable(config);
       
    
    $('#ucs').dataTable($.extend(datatables.UC), {
        sAjaxSource: '/api/ucs/' 
    });
    
    // Highchart
    var curvaDePotenciaPlot = new Highcharts.Chart({
        chart: {
            renderTo: "plot-curvas"
        },
        title: {
            text: "Ploteo de potencia"
        },
        yAxis: {
            title: {text:"KW/h"},
        },
        series: [
            {
                data: [1, 2, 3, 4],
                name: "Potencia Activa"
            }

        ]
    });
    
    // Botons
    $('.button').button();
    //
    $('#seleccion-fecha input[name=fecha]').datepicker({
        onSelect: function (date, text) {
            console.log("Selecci´on de la fecha", arguments);
        }
        
    });
    // Svg
    $('#svg').svg({
        loadURL: window.SMVE.config.STATIC_URL + 'svg/eett.svg',
        onLoad: function(svg){
            //debugger;
            console.log(svg);
            var texts = $('text', svg.root());
            $(texts).click(function (){
                //console.log($(this).text());
                //alert("El texto clickeado es "+ $(this).text());
                var tspan = this;
                var dlg = $('<div>').dialog({
                    autoOpen: false,
                    title: $(this).text(),
                    modal: true,
                    buttons: [
                        {text: "Cerrar", click: function  () {
                            $(this).dialog('close').dialog('destroy');
                        }},
                        {text: "Aceptar", click: function (){
                            
                            var newVal =$(this).find('.newValue').val();
                            if (newVal){
                                $(tspan).text(newVal);
                                
                            }
                            $(this).dialog('destroy');
                        }}
                        
                    ]
                });
                $(dlg).html('<span>Nuevo valor</span><input class="newValue" type="text" value="'+$(this).text()+'">');
                $(dlg).dialog('open');
                
            }).hover(function (){
                // In texto
                $(this).css('fill', '#dd0000');
            },function (){
                // Mouse sale del texto
                $(this).css('fill', '#000');
            }); // Texts
            // Iteración sobre los grupos
            // 
            $('g:not([id^=layer])').hover(function(){
                // In
                $(this).find('path').css('stroke', '#f00');
                
            }, function (){
                // Out
                $(this).find('path').css('stroke', '#000');
            }).each(function (argument) {
               //console.log("Grupo", this);
            });
            
            
        }
    });
     

});