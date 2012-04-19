
(function($){

module('tiny.imagedrawerinfopanel', {
    setup: function() {
        var template;
        $.ajax({
            url: '../imagedrawer_dialog_snippet.html',
            async: false,
            success: function(html) {
                template = html;
            }
        });
        $('#main').append(template);
    },

    teardown: function () {
        $('#main').empty();
    }

});


test("Create and destroy", function() {

    equal($('.tiny-imagedrawer-panel-info').length, 1);

    $('.tiny-imagedrawer-panel-info')
        .imagedrawerinfopanel({
        });

    $('.tiny-imagedrawer-panel-info')
        .imagedrawerinfopanel('destroy');

});

test("getting and setting insertOptions", function() {

    var el = $('.tiny-imagedrawer-panel-info');

    el.imagedrawerinfopanel({
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: false,
        captiontext: '',
        align: 'left',
        dimension: 'medium'
    });

    el.imagedrawerinfopanel ('insertOptions', {
        caption: true
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: true,
        captiontext: "",
        align: 'left',
        dimension: 'medium'
    });

    el.imagedrawerinfopanel ('insertOptions', {
        captiontext: 'A text'
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: true,
        captiontext: 'A text',
        align: 'left',
        dimension: 'medium'
    });

    el.imagedrawerinfopanel ('insertOptions', {
        align: 'right'
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: true,
        captiontext: 'A text',
        align: 'right',
        dimension: 'medium'
    });
    el.imagedrawerinfopanel ('insertOptions', {
        align: 'center'
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: true,
        captiontext: 'A text',
        align: 'center',
        dimension: 'medium'
    });

    el.imagedrawerinfopanel ('insertOptions', {
        dimension: 'small'
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: true,
        captiontext: 'A text',
        align: 'center',
        dimension: 'small'
    });
    el.imagedrawerinfopanel ('insertOptions', {
        dimension: 'large'
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: true,
        captiontext: 'A text',
        align: 'center',
        dimension: 'large'
    });
    el.imagedrawerinfopanel ('insertOptions', {
        dimension: 'original'
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: true,
        captiontext: 'A text',
        align: 'center',
        dimension: 'original'
    });

    el.imagedrawerinfopanel ('insertOptions', {
        caption: false,
        captiontext: 'Nothing',
        align: 'left',
        dimension: 'medium'
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: false,
        captiontext: 'Nothing',
        align: 'left',
        dimension: 'medium'
    });


    el.imagedrawerinfopanel('destroy');

});



})(jQuery);

