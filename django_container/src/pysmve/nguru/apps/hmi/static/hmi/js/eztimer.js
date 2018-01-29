(function() {
    if ('EZTimer' in this) {
        return;
    }

    var EZTimer = function (callable, interval) {
        this._callable = null;
        this._interval = interval || EZTimer.DEFAULT_INTERVAL;
    };
    // Class constants
    $.extend(EZTimer, {
        DEFAULT_INTERVAL: 1000
    });

    // Methods

    $.extend(EZTimer.prototype, {
        enable: function () {

        },

        disable: function () {

        },

        isEnabled: function () {

        },

        toggle: function () {
            var retval;
            if (this.isEnabled()) {
                this.disable();
                retval = false;
            } else {
                this.enable();
                retval = true;
            }
            return retval;
        },

        setFunction: function (callable) {
            if (!(callable instanceof Function)) {
                throw new Error(callable + "is not a function");
            }
            this._callable = callable;
        },

        setInterval: function () {

        },

        getInterval: function () {

        },

        start: function (interval) {
            if (interval) {
                this.setInterval(interval);
            }

        },

    });

    this.EZTimer = EZTimer;
})(jQuery);