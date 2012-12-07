/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 110, indent: 4 */
/*jslint sub: true */
/*globals window navigator document setTimeout $ */
/*globals sinon module test ok equal deepEqual */
/*globals tinymce */


module('tiny.imagedrawerinfopanel', {
    setup: function () {
        var template;

        // The Same-Origin-Policy effectively
        // prohibits getting the snippet if we are on file:///,
        // which is what happens when phantomjs runs the test.
        // So we have to do this differently.

        $.ajax({
            url: 'imagedrawer_dialog_snippet.html',
            async: false,
            success: function (html) {
                template = html;
            }
        });
        $('#main').append(template);
    
        
    },

    teardown: function () {
        $('#main').empty();
    }

});


test("Create and destroy", function () {

    console.log($('#main').html());
    equal($('.tiny-imagedrawer-panel-info').length, 1);

    $('.tiny-imagedrawer-panel-info')
        .imagedrawerinfopanel({
        });

    $('.tiny-imagedrawer-panel-info')
        .imagedrawerinfopanel('destroy');

});


test("getting and setting insertOptions", function () {

    var el = $('.tiny-imagedrawer-panel-info');

    el.imagedrawerinfopanel({
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: false,
        captiontext: '',
        align: 'left',
        dimension: 'medium'
    });

    el.imagedrawerinfopanel('insertOptions', {
        caption: true
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: true,
        captiontext: "",
        align: 'left',
        dimension: 'medium'
    });

    el.imagedrawerinfopanel('insertOptions', {
        captiontext: 'A text'
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: true,
        captiontext: 'A text',
        align: 'left',
        dimension: 'medium'
    });

    el.imagedrawerinfopanel('insertOptions', {
        align: 'right'
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: true,
        captiontext: 'A text',
        align: 'right',
        dimension: 'medium'
    });
    el.imagedrawerinfopanel('insertOptions', {
        align: 'center'
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: true,
        captiontext: 'A text',
        align: 'center',
        dimension: 'medium'
    });

    el.imagedrawerinfopanel('insertOptions', {
        dimension: 'small'
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: true,
        captiontext: 'A text',
        align: 'center',
        dimension: 'small'
    });
    el.imagedrawerinfopanel('insertOptions', {
        dimension: 'large'
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: true,
        captiontext: 'A text',
        align: 'center',
        dimension: 'large'
    });
    el.imagedrawerinfopanel('insertOptions', {
        dimension: 'original'
    });
    deepEqual(el.imagedrawerinfopanel('insertOptions'), {
        caption: true,
        captiontext: 'A text',
        align: 'center',
        dimension: 'original'
    });

    el.imagedrawerinfopanel('insertOptions', {
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


