(function ($) {
    $(function (){
        $('td .attend').click(function (e){
            e.preventDefault();
            $(this).hide();
        });
    });
})(django.jQuery);