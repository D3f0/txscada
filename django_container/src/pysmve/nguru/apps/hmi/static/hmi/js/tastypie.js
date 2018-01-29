(function () {
    // CSRF token
    // https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax

    // using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

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