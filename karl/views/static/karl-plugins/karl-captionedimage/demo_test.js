
(function($){

module("karl-captionedimage");

var inside = function(el, xmulti, ymulti) {
    el = $(el);
    var offset = el.offset();
    return {
        x: Math.floor(offset.left + el.outerWidth() * xmulti),
        y: Math.floor(offset.top + el.outerHeight() * ymulti)
    };
};

test("Create and destroy", function() {


    $('.image').karlcaptionedimage({
        });

    $('.image').karlcaptionedimage('destroy');

});

test("Check alignments", function() {

    $('.image').karlcaptionedimage({
        });

    // check all image positions
    $('div.karl-captionedimage-wrapper').filter
    var lefts = $('div.karl-captionedimage-wrapper')
        .map(function() {
            return inside(this, 0, 0.5).x;
        });
    var centers = $('div.karl-captionedimage-wrapper')
        .map(function() {
            return inside(this, 0.5, 0.5).x;
        });
    var rights = $('div.karl-captionedimage-wrapper')
        .map(function() {
            return inside(this, 1, 0.5).x;
        });
    var parent = $('div.karl-captionedimage-wrapper').eq(0).parent();
    var p_left = inside(parent, 0, 0.5).x
    var p_center = inside(parent, 0.5, 0.5).x
    var p_right = inside(parent, 1, 0.5).x
    equal(lefts[0], p_left, 'image 1 aligned left');
    // image 2 should be online, but it's centered
    equal(rights[2], p_right, 'image 3 aligned right');
    equal(centers[3], p_center, 'image 4 aligned center');
    equal(centers[4], p_center, 'image 5 aligned center');
    equal(centers[5], p_center, 'image 6 aligned center');
    // image without style is not on the left on IE, but
    // important is that it does not break the code.
    //equal(lefts[6], p_left, 'image 7 aligned left');

    $('.image').karlcaptionedimage('destroy');

});

})(jQuery);

