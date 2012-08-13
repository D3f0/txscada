// Punto de entrada a la aplicación
$(function  () {
    /**
    *
    */            
    
    smve = {};
    
   	// Crear las solapas
    $('#tabs').tabs();
	$('#tabla-curvas-pq').tabs();
	    
	var dataTableLanguage = {
		"sProcessing": "Procesando...",
		"sLengthMenu": "_MENU_ entradas",
		"sZeroRecords": "No se encontraron registros.",
		"sInfo": "_START_ hasta _END_ de _TOTAL_ registros",
		"sInfoEmpty": "0 hasta 0 de 0 registros",
		"sInfoFiltered": "(filtrados de _MAX_  registros)",
		"sInfoPostFix": "",
		"sSearch": "Búsqueda",
		"sUrl": "",
		"oPaginate": {
			"sFirst":    "Primero",
			"sPrevious": "Previo",
			"sNext":     "Siguiente",
			"sLast":     "Último"
		}
	};
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
       }); // Svg
    var $svg = $('#svg');
    
    // Updater por polling
    smve.valueUpdate = true;
    function valueUpdate() {
    	// Timeout
        if (!smve.valueUpdate) return;
        
        if (!$('#checkbox-update').is(':checked')){
            return;
        }
        console.log("Update");
        $.ajax('/valores', {
            success: function (data){
               $.each(data, function (key, value){
                   //console.log(key, value);
                   //console.log(
                       $svg.find('#'+key).text(value)
                    //);
                });
            },
            error: function () {
                console.error("Error");
            }
            
            
        });
    } // Value Update
    window.setInterval(valueUpdate, 1000);
    
    
    // Tabla de eventos
    // $('#tabla-eventos').dataTable({
    //         bJQueryUI: true,
    //         bServerSide: true,
    //         sAjaxSource: "/eventos/",
    //         bProcessing: true
    //     \);}
    
    
    $.extend(datatables.COMaster, {
       sAjaxSource: '/api/comaster/',
       oLanguage: dataTableLanguage 
    });
       
    
    $.extend(datatables.UC, {
        sAjaxSource: '/api/ucs/',
        oLanguage: dataTableLanguage 
    });
    
    $.extend(datatables.AI, {
       sAjaxSource: '/api/ais/',
       oLanguage: dataTableLanguage
        
    });
    
    $('table[flag]').each(function () {
        var modelName = $(this).attr('model');
        var conf = datatables[modelName];
        console.log(modelName, conf);
        $(this).dataTable(conf);
        
        //console.log(this);
        
    });
    // 
    // Tabla de eventos
    // 
    function createEventTable() {
        		
		var tablaEventos = $('#tabla-eventos');
		console.log("Creando tabla de eventos en", tablaEventos);
		var config = {
			bProcessing: true,
			bServerSide: true,
			sAjaxSource: '/api/events/',
			bJQueryUI: true,
			oLanguage: dataTableLanguage
		};
		tablaEventos.dataTable(config);
	}
	createEventTable();
   	
   	function createValueTable(){
   		var config = {
   			bJQueryUI: true,
   			oLanguage: dataTableLanguage
   			
   		};
		$('#valores-pq-diarios').dataTable(config);
   	} 
   	createValueTable();

});