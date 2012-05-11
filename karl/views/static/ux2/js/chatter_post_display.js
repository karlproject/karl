var exp = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
var setQuipTargets = function() {
$('.quip').each(function(){
    $(this).html($(this).html().replace(exp,
	'<a class="quip-url" href="$1">$1</a>','ig'))
})
$('.quip-name').attr('href',
    function(i, val) {
	return window.head_data['chatter_url'] + "creators.html?creators=" + $(this).attr('ref');
    }
);
$('.quip-tag').attr('href',
    function(i, val) {
	return window.head_data['chatter_url'] + "tag.html?tag=" + $(this).attr('ref');
    }
);
$('.quip-community').attr('href',
    function(i, val) {
	return window.head_data['app_url'] + "/communities/" + $(this).attr('ref');
    }
);
}

var setQuipActions = function() {
$('.chatter-reply').click(function() {
    $(this).parent().parent().next().children('.option-box').hide();
    var replybox = $(this).parent().parent().next().children('.reply-box');
    replybox.show();
    var textarea = replybox.find('.quip-text');
    textarea.focus();
    // ug, set focus after last char on the textarea
    var val = textarea.val();
    textarea.val('');
    textarea.val(val);
    return false;
});
$('.chatter-repost').click(function() {
    $(this).parent().parent().next().children('.option-box').hide();
    $(this).parent().parent().next().children('.repost-box').show();
    return false;
});
$('.btn-cancel').click(function() {
    $(this).parent().parent().parent().parent().parent().hide();
    return false;
});
$('.btn-cancel-rp').click(function() {
    $(this).parent().parent().parent().hide();
    return false;
});
$('.show-original').click(function() {
    $(this).parent().find('.original-quip').show();
    $(this).parent().find('.conversation-controls').show();
    $(this).hide();
});
$('.hide-original').click(function() {
    $(this).parent().prev('.show-original').show();
    $(this).parent().hide();
    $(this).parent().next('.original-quip').hide();
    return false;
});
}
