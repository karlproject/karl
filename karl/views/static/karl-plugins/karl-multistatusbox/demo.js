
(function($){

    $(document).ready(function() {

        $('#statusbox').multistatusbox({
        });

        $('#button1').click(function() {
            $('#statusbox').multistatusbox('append',
                'A normal message', 'normal'
            );
        });

        $('#button2').click(function() {
            $('#statusbox').multistatusbox('append',
                'An <b>important</b> message', 'important'
            );
        });

        $('#button3').click(function() {
            $('#statusbox').multistatusbox('clear', 'normal');
        });

        $('#button4').click(function() {
            $('#statusbox').multistatusbox('clear', 'important');
        });

        $('#button5').click(function() {
            $('#statusbox').multistatusbox('clear');
        });

        $('#button6').click(function() {
            $('#statusbox').multistatusbox('clearAndAppend',
                'A normal <span style="color: blue">blue</span> message', 'normal'
            );
        });

        $('#button7').click(function() {
            $('#statusbox').multistatusbox('clearAndAppend',
                'A normal <span style="color: green;">green</span> message', 'normal'
            );
        });

        $('#button8').click(function() {
            $('#statusbox').multistatusbox('clearAndAppend',
                'An <b>important <span style="color: blue;">blue</span></b> message', 'important'
            );
        });

        $('#button9').click(function() {
            $('#statusbox').multistatusbox('clearAndAppend',
                'An <b>important <span style="color: green;">green</span></b> message', 'important'
            );
        });

    });

})(jQuery);

