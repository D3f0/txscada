(function ($){
    if (window.SMVE === undefined) {
        window.SMVE = {};
    }

    var grid = null;

    function crearGrillaEventos(container){

        if (grid !== null){
            return;
        }

        var columns = [
            { id: "title", name: "Tipo Alarma", field: "title", sortable: true },
            { id: "duration", name: "Duration", field: "duration", sortable: true, formatter: dayFormatter },
            { id: "%", name: "% Complete", field: "percentComplete", sortable: true },
            { id: "start", name: "Start", field: "start", formatter: dateFormatter, sortable: true },
            { id: "finish", name: "Finish", field: "finish", formatter: dateFormatter, sortable: true },
            { id: "effort-driven", name: "Effort Driven", field: "effortDriven", sortable: true },
            { id: "atencion", name: "Atencion", default: "Atencion", field: "atencion",
                formatter: function myFormatter(row, cell, value, columnDef, dataContext) {
                    return "<a href='#' class='badge badge-important'>"+value+"</a>";
            }}
        ];

        function dayFormatter(row, cell, value, columnDef, dataContext) {
          return value + ' days';
        }

        function dateFormatter(row, cell, value, columnDef, dataContext) {
            return value.getMonth() + '/' + value.getDate() + '/' + value.getFullYear();
        }

        var options = {
            enableCellNavigation: true,
            enableColumnReorder: false,
            multiColumnSort: true,
            forceFitColumns: true
        };


        var MS_PER_DAY = 24 * 60 * 60 * 1000;
        var data = [];
        for (var i = 0; i < 20; i++) {
            var startDate = new Date(new Date("1/1/1980").getTime() + Math.round(Math.random() * 365 * 25) * MS_PER_DAY);
            var endDate = new Date(startDate.getTime() + Math.round(Math.random() * 365) * MS_PER_DAY);
            data[i] = {
                title: "Task " + i,
                duration: Math.round(Math.random() * 30) + 2,
                percentComplete: Math.round(Math.random() * 100),
                start: startDate,
                finish: endDate,
                effortDriven: (i % 5 == 0),
                atencion: "Atender"
            };
        }

        grid = new Slick.Grid(container, data, columns, options);

        grid.onSort.subscribe(function (e, args) {
            var cols = args.sortCols;

            data.sort(function (dataRow1, dataRow2) {
                for (var i = 0, l = cols.length; i < l; i++) {
                    var field = cols[i].sortCol.field;
                    var sign = cols[i].sortAsc ? 1 : -1;
                    var value1 = dataRow1[field], value2 = dataRow2[field];
                    var result = (value1 == value2 ? 0 : (value1 > value2 ? 1 : -1)) * sign;
                    if (result != 0) {
                        return result;
                    }
                }
                return 0;
            });
            grid.invalidate();
            grid.render();
        });
        function removeRow(grid, row){
            var dd = grid.getData();
            dd.splice(row,1);
            var r = row;

            while (r<dd.length){
                grid.invalidateRow(r);
                r++;
            }
            grid.updateRowCount();
            grid.render();
            grid.scrollRowIntoView(row-1);
        }
        grid.onClick.subscribe(function(e, args) {
            var oevt = e.originalEvent;
            var elem = document.elementFromPoint(oevt.clientX, oevt.clientY);
            console.log(elem);
            var gird = this,
                row = args.row;

            console.log(grid);
            var $dlg = $('<div></div>').dialog({
                title: "Desea atender el evento?",
                modal: true,
                stack: true,
                buttons: [
                    {
                        text: "Atender",
                        click: function (event){
                            removeRow(grid, row);
                            $(this).dialog('close');

                        }
                    },
                    {
                        text: "Cancelar",
                        click: function (e){
                            $(this).dialog('close');
                        }
                    },
                ],
                autoOpen: false,
                close: function (ev) {
                    $(this).dialog('destroy');
                },
                open: function (event, ui) {
                    $('.ui-dialog').css('zIndex', 3);
                    $('.ui-widget-overlay').css('zIndex', 2);
                }
            }).html("Desea atender este evento?");

            $dlg.dialog('open');
            //removeRow(this, args.row);




            //this.scrollRowIntoView(args.row-1)


            console.log(e, args, this);
            // or dataView.getItem(row);
        });

    }



    $.extend(window.SMVE, {
        crearGrillaEventos: crearGrillaEventos
    });

})(jQuery);
