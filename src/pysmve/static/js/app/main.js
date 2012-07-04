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
    // Highcharts
    function generateData(){
        var tmp = [];
    
        for (var i=0; i<100; i++){
            tmp[tmp.length] = Math.floor((Math.random()*300)+1);
        }    
        return tmp;
    }
    
    
    chart = new Highcharts.Chart({
        chart: {
            renderTo: 'chart-potencias',
            type: 'spline',

            events:{
                load: function  () {
                    console.log("Chart generado");
                    var that = this;
                    
                    function update(date, data){
                        if (!data) {
                            data = generateData();
                        }
                        if (!date){
                            date = "" + new Date();
                        }
                        try {
                            that.series[0].remove(true);
                            
                        }
                        catch (error){
                            
                        };
                        
                        that.addSeries({
                           name: "Potencia del "+date,
                           data: data
                        });
                    }
    
                    $('#fecha').datepicker({
                        onSelect: function (text, date) {
                            update(text);
                        }
                    }).next('a:first').button().click(function (){
                       update($('#fecha').val());
                    });
                    update();   
                }
                
            }
        },
        title: {
            text: "Demanda de potencia diaria"
        },
        yAxis: {
            title: {
                text: "KW/h"
            }
        }
        
        
    });
    
    // chart.renderer.path(['M', 0, 100, 'L', 100, 0]).attr(
    //         //{'stroke-width': 2px; stroke: '#ff0'\
    //     ).add();}
    
    // Actualizacion
    //$('.button').button();
    try {
        console.log("Funciones")
        var ws = new WebSocket('ws://localhost:8080/smve');
        WS = ws;
        ws.onopen = function () {
          console.log("On open", arguments);
            
        };
    } catch(error){console.error("Error WS:" + error)}
    
    
    var $svg = null;
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
       }); // Svg
    var $svg = $('#svg');
    function valueUpdate() {
        console.log("Update");
        $.ajax('/valores', {
            success: function (data){
               $.each(data, function (key, value){
                   console.log(key, value);
                   console.log($svg.find('#'+key).text(value));
                });
            },
            error: function () {
                console.error("Error");
            }
            
        });
    }

    window.setInterval(valueUpdate, 1000);
        

});