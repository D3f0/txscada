(function ($){


    function fixDatepickerPositioning(input) {
        var $input = $(input),
            top = $input.position().top + $input.height() * 1.75;
        window.setTimeout(function (){
            console.log("Fixing datepicker positioning to ", top);
            $('#ui-datepicker-div').css('top', top+'px');
        }, 0);
    }

    function init () {

        var $date_from = $('#id_date_from'),
            $date_to = $('#id_date_to');

        $('.dateinput').each(function (){
            var $this = $(this);
            $this.datepicker({
                beforeShow: fixDatepickerPositioning
            });
        });

        $('form').on('submit', function (event) {
            return false;
        });

        $date_from.datepicker('option', 'onClose', function (selectedDate){
            $date_to.datepicker('option', 'minDate', selectedDate);
        });
    }

    init();

})(window.jQuery);