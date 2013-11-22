(function ($) {
    if ('TastyJQGrid' in this) {
        return;
    }

    var TastyJQGrid = {
        serializeGridData: function (postData) {
            // prepare data for Tatsypie format
            var pdat = $.extend({}, postData);

            // sorting / ordering
            if (typeof pdat.sidx != 'undefined' && pdat.sidx !== '')
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
                    'dt': false // special value used by date fields.
                                 // don't append anything to search condition.
                };
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
            //debugger;
            return pdat;
            }
        };
    this.TastyJQGrid = TastyJQGrid;

})(jQuery);