// Punto de entrada a la aplicación
$(function  () {
    /**
    * Punto de entrada al programa...
    */
	// Ambito de nombres            
    smve = {
    	// Polling ajax de valores de energía
    	valueUpdate: true,
    	// Tiempo de polleo
    	pollTime: 1
    	
    };
    // Colores
    var INTERRUPTOR_ENCENDIDO = '#8CD701';
    var INTERRUPTOR_APAGADO = '#f00';
    
   	// Crear las solapas
    $('#tabs').tabs();
	$('#tabla-curvas-pq').tabs();
	
	// Traducción de las datatbles
	    
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
    smve.curvaDePotencia = new Highcharts.Chart({
        chart: {
            renderTo: "plot-curvas"
        },
        title: {
            text: "Curva de potencia"
        },
        yAxis: {
            title: {text:"KW/h - KVA/h"},
             
        },
        xAxis: {
        	type: 'datetime',
        	dateTimeLabelFormats: {
                month: '%e. %b',
                day: '%b %e',
                hour: '%b %e',
                year: '%b'
            }
            //, tickInterval: 24 * 3600 * 1000
        },
        series: [
            {
                data: [[Date.UTC(2011, 4, 23), 194.0], [Date.UTC(2011, 4, 24), 195.00000000000003], [Date.UTC(2011, 4, 25), 192.00000000000003], ],
                name: "Potencia Activa"
            }

        ]
    });
    
    // Botons
    $('.button').button();
    // Selección de fecha
    function formatearFecha(d) {
    	if (typeof(d) == "undefined") {
    		d = new Date();
    	}
    	return d.getDate()+"/"+(d.getMonth()+1)+"/"+(d.getYear()+1900);
    }
    
    // http://dev.enekoalonso.com/2010/09/21/date-from-iso-8601-string/
    function dateFromISO8601(isostr) {
		var parts = isostr.match(/\d+/g);
		return new Date(parts[0], parts[1] - 1, parts[2], parts[3], parts[4], parts[5]);
	}
	function utcFromISO8601(isostr) {
		var parts = isostr.match(/\d+/g);
		return Date.UTC(parts[0], parts[1] - 1, parts[2], parts[3], parts[4], parts[5]);
	}
    // Datepicker de la fechas
    $('#seleccion-fecha input[name=fecha]').datepicker({
    	dateFormat: 'dd/mm/yy',
        onSelect: function (text, date) {
        	//console.log("Refrescando valores", arguments);
        	var url = '/api/energy/' + text;
        	console.log(url);
        	
        	$.ajax(url, {
        		success: function (text, xhr){
        			var json = $.parseJSON(text);
        			console.log("Datos de respuesta", json);
        			while (smve.curvaDePotencia.series.length) {
        				smve.curvaDePotencia.series[0].remove();
        			}
					var valores_p = [], valores_q = [];
					$.each(json.data, function (){
						var d = utcFromISO8601(this[0]);
						var p = this[1];
						var q = this[2];
						valores_p.push([d, p]);
						valores_q.push([d, q]);
					});
					smve.curvaDePotencia.addSeries({name: "Potencia Activa", data: valores_p});
					smve.curvaDePotencia.addSeries({name: "Potencia Reactiva", data: valores_q});
					smve.curvaDePotencia.redraw();
        		}
        	});
        	
			
            
        }
        
    }).val(formatearFecha());
    
    // Valores de energía
   	
   	function createValueTable(){
   		var config = {
   			bJQueryUI: true,
   			oLanguage: dataTableLanguage,
   			bProcessing: true,
   			bServerSide: true,
   			sAjaxSource: '/api/energy/',
   			bFilter: false
   		};
		$('#valores-pq-diarios').dataTable(config);
   	} 
   	createValueTable();
    
    
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
                
            });
            
			// ----------------------------------------------------
			// Interruptores
			// ----------------------------------------------------
            $('g.grupo-interruptor').each(function (){
            	//console.log("Grupo interruptor", this);
            	$(this).find('.interruptor').css('fill',  INTERRUPTOR_APAGADO).
            				css('fill-opacity',  1).css('stroke', INTERRUPTOR_APAGADO);
            	$(this).find('.interruptor-enclave').css('fill',  INTERRUPTOR_ENCENDIDO).css('fill-opacity',  1).css('stroke', INTERRUPTOR_ENCENDIDO);
				
            });
            
            }
       }); // Svg
    smve.mimico = $('#svg');
    
    
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
                       smve.mimico.find('#'+key).text(value)
                    //);
                });
            },
            error: function () {
                console.error("Error");
            }
            
            
        });
    } // Value Update
    window.setInterval(valueUpdate, smve.pollTime * 1000); 
	/*    
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
    */
    
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
	
	


});