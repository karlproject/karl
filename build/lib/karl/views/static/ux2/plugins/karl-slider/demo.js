
(function($){

    $(document).ready(function() {

        $('#slider1').karlslider({
        });
 
        $('#slider2').karlslider({
            enableClickJump: true
        });

        $('#slider3').karlslider({
            enableClickJump: true,
            jumpStep: 5
        });

        $('#slider4').karlslider({
            enableClickJump: true,
            jumpStep: 5,
            enableKeyJump: true
        });
 
        // themeswitcher
        $('#switcher').themeswitcher();


    });

})(jQuery);

