/**
 * An object  which holds query arguments for URL.
 * Tipically for easier resource querying
 */
(function ($){
    // Avoid multiple imports
    if ('QueryObj' in this) {
        return;
    }

    if (!('XDate' in this)) {
        throw Error("QueryObj depends on XDate");
    }

    function QueryObj(initial, url) {
        this._url = url || null;
        if (this == window) {
            throw new Error("QueryObj must be called with new");
        }
        this._data = initial || {};

    }

    $.extend(QueryObj.prototype, {
        getQueryParamsEncoded: function(queryArguments){
            var str = [];
            for(var p in queryArguments) {
                var value = queryArguments[p];
                if (value === null) {
                    continue;
                }
                str.push(encodeURIComponent(p) + "=" + this.encodeValue(value));

            }
            return str.join("&");
        },

        encodeValue: function (value){
            if (value instanceof Date){
                value = new XDate(value).toString('yyyy-MM-dd hh:mm:ss.ffffff');
            }
            return encodeURIComponent(value);
        },
        remove: function (key) {
            if (key in this._data) {
                delete this._data[key];
            }
        },

        setUrl: function (url) {
            this._url = url;
        },
        getUrl: function () {
            return this._url;
        },
        hasValidUrl: function () {
            return (this._url !== null);
        },

        update: function (key, value) {
            this._data[key] = value;
        },
        getQuery: function (){
            return this.getQueryParamsEncoded(this._data);
        },
        toString: function () {
            var result;

            if (this.hasValidUrl()) {
                result = [this.getUrl(), this.getQuery()].join('?');
            } else {
                result = this.getQuery();
            }
            return result;
        },
        // Simliar to python version of the function
        keys: function () {
            return $.map(this._data, function (value, index) {
                return index;
            });
        },
        values: function () {
            return $.map(this._data, function (value, index) {
                return value;
            });
        },
    });

    // Public to namespace
    this.QueryObj = QueryObj;

})(jQuery);