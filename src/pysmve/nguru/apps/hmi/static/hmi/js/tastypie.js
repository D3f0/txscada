(function () {
    // Functions to pull from tastypie when partial content (conut < total)
    // is returned
    var nullFunction = function () {};

    jQuery.getRest = function (url, onSuccess, onProgress) {
        var result = [],
            opts = arguments[0]; // Alias

        if (arguments.length == 1) {

            url = opts.url;
            onSuccess = opts.success || nullFunction;
            onProgress = opts.progress || nullFunction;
        } else {
            onSuccess = onSuccess || nullFunction;
            onProgress = onProgress || nullFunction;
        }


        function perXHRsuccess (data, xhr) {
            console.log("Success");
            // next URL
            var next = data.meta.next;
            // Get data
            result = result.concat(data.objects);

            if (next) {
                // Update args
                onProgress.call(this, result.length, data.meta.total_count);

                $.getJSON(next, perXHRsuccess);

            } else {
                onSuccess.call(this, result, data.meta);
            }
        }

        $.getJSON(url, perXHRsuccess);
    };
})(window);