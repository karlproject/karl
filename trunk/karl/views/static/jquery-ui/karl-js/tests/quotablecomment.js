/*
 * quotablecomment unit tests
 */
(function($) {

module("karl: quotablecomment");


// pasteToActiveTiny

test('pasteToActiveTiny updates tinyMce selection content', function() {
  var editor = tinyMCE.activeEditor;
  editor.focus();

  $('.blogComment').karlquotablecomment({});
  
  $('.quo-paste').simulate('click');
/*  console.log(editor.selection.getContent());*/
});




})(jQuery);