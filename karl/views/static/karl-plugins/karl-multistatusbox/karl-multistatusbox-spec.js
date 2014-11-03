/* jshint expr: true */

describe('KARL Multi File Upload', function () {

  var sc = function () {
    var result = [];
    $('#statusbox .karl-multistatusbox-item')
      .each(function () {
              var t = String($(this).text()).replace(/^\s+|\s+$/g, '');
              result.push(t);
            });
    return result;
  };


  beforeEach(function () {
    $('body').html(__html__['karl/views/static/karl-plugins/karl-multistatusbox/karl-multistatusbox-fixture.html']);
  });
  afterEach(function () {
    $('body').empty();
  });

  // This test has been migrated from QUnit, and uses the old QUnit assertions.
  // If you write new tests, use Chai instead! http://chaijs.com/api/bdd/

  test("Widget attachment with no options", function () {

    $('#statusbox').multistatusbox({});

    same(sc(), [
      "A message that came with the page"
    ], 'Statusbox content does not match');

  });


  test("Append messages", function () {

    $('#statusbox').multistatusbox({});

    $('#statusbox').multistatusbox('append', 'Message1');
    $('#statusbox').multistatusbox('append', 'Message2');
    $('#statusbox').multistatusbox('append', 'Message3');

    same(sc(), [
      'A message that came with the page',
      'Message1X',
      'Message2X',
      'Message3X'
    ], 'Statusbox content does not match');

    ok($('#statusbox .karl-multistatusbox-item .karl-multistatusbox-closebutton').length == 3,
       'Has close button');

  });

  test("Clear messages of nonexistent category", function () {

    $('#statusbox').multistatusbox({});

    $('#statusbox').multistatusbox('append', 'Message1');
    $('#statusbox').multistatusbox('append', 'Message2');
    $('#statusbox').multistatusbox('append', 'Message3');

    $('#statusbox').multistatusbox('clear', 'nosuch');

    same(sc(), [
      'A message that came with the page',
      'Message1X',
      'Message2X',
      'Message3X'
    ], 'Statusbox content does not match');

  });

  test("Append messages with category", function () {

    $('#statusbox').multistatusbox({});

    $('#statusbox').multistatusbox('append', 'Message1');
    $('#statusbox').multistatusbox('append', 'Message2');
    $('#statusbox').multistatusbox('append', 'Message3');

    $('#statusbox').multistatusbox('append', 'MessageA1', 'A');
    $('#statusbox').multistatusbox('append', 'MessageA2', 'A');
    $('#statusbox').multistatusbox('append', 'MessageB1', 'B');

    same(sc(), [
      'A message that came with the page',
      'Message1X',
      'Message2X',
      'Message3X',
      'MessageA1X',
      'MessageA2X',
      'MessageB1X'
    ], 'Statusbox content does not match');

  });

  test("Clear messages of a category", function () {

    $('#statusbox').multistatusbox({});

    $('#statusbox').multistatusbox('append', 'Message1');
    $('#statusbox').multistatusbox('append', 'Message2');
    $('#statusbox').multistatusbox('append', 'Message3');

    $('#statusbox').multistatusbox('append', 'MessageA1', 'A');
    $('#statusbox').multistatusbox('append', 'MessageA2', 'A');
    $('#statusbox').multistatusbox('append', 'MessageB1', 'B');
    $('#statusbox').multistatusbox('clear', 'A');

    same(sc(), [
      'A message that came with the page',
      'Message1X',
      'Message2X',
      'Message3X',
      'MessageB1X'
    ], 'Statusbox content does not match');

    $('#statusbox').multistatusbox('clear', 'B');

    same(sc(), [
      'A message that came with the page',
      'Message1X',
      'Message2X',
      'Message3X'
    ], 'Statusbox content does not match');

  });

  test("Clear all messages without category", function () {

    $('#statusbox').multistatusbox({});

    $('#statusbox').multistatusbox('append', 'Message1');
    $('#statusbox').multistatusbox('append', 'Message2');
    $('#statusbox').multistatusbox('append', 'Message3');

    $('#statusbox').multistatusbox('append', 'MessageA1', 'A');
    $('#statusbox').multistatusbox('append', 'MessageA2', 'A');
    $('#statusbox').multistatusbox('append', 'MessageB1', 'B');

    same(sc(), [
      'A message that came with the page',
      'Message1X',
      'Message2X',
      'Message3X',
      'MessageA1X',
      'MessageA2X',
      'MessageB1X'
    ], 'Statusbox content does not match');

    $('#statusbox').multistatusbox('clear', null);

    same(sc(), [
      'A message that came with the page',
      'MessageA1X',
      'MessageA2X',
      'MessageB1X'
    ], 'Statusbox content does not match');

  });

  test("Clear all messages", function () {

    $('#statusbox').multistatusbox({});

    $('#statusbox').multistatusbox('append', 'Message1');
    $('#statusbox').multistatusbox('append', 'Message2');
    $('#statusbox').multistatusbox('append', 'Message3');

    $('#statusbox').multistatusbox('append', 'MessageA1', 'A');
    $('#statusbox').multistatusbox('append', 'MessageA2', 'A');
    $('#statusbox').multistatusbox('append', 'MessageB1', 'B');

    same(sc(), [
      'A message that came with the page',
      'Message1X',
      'Message2X',
      'Message3X',
      'MessageA1X',
      'MessageA2X',
      'MessageB1X'
    ], 'Statusbox content does not match');

    $('#statusbox').multistatusbox('clear');

    same(sc(), [
    ], 'Statusbox content does not match');

  });

  test("Clear and append", function () {

    $('#statusbox').multistatusbox({});

    $('#statusbox').multistatusbox('append', 'Message1');
    $('#statusbox').multistatusbox('append', 'Message2');
    $('#statusbox').multistatusbox('append', 'Message3');

    $('#statusbox').multistatusbox('append', 'MessageA1', 'A');
    $('#statusbox').multistatusbox('append', 'MessageA2', 'A');
    $('#statusbox').multistatusbox('append', 'MessageB1', 'B');

    $('#statusbox').multistatusbox('clear');

    same(sc(), [
    ], 'Statusbox content does not match');

    $('#statusbox').multistatusbox('clearAndAppend', 'MessageA1', 'A');
    $('#statusbox').multistatusbox('clearAndAppend', 'MessageB1', 'B');

    same(sc(), [
      'MessageA1X',
      'MessageB1X'
    ], 'Statusbox content does not match');

    $('#statusbox').multistatusbox('clearAndAppend', 'MessageA2', 'A');

    same(sc(), [
      'MessageB1X',
      'MessageA2X'
    ], 'Statusbox content does not match');

    $('#statusbox').multistatusbox('clearAndAppend', 'MessageB2', 'B');

    same(sc(), [
      'MessageA2X',
      'MessageB2X'
    ], 'Statusbox content does not match');

    $('#statusbox').multistatusbox('clearAndAppend', 'MessageA3', 'A');

    same(sc(), [
      'MessageB2X',
      'MessageA3X'
    ], 'Statusbox content does not match');

  });

  test("Close button works", function () {

    $('#statusbox').multistatusbox({});

    $('#statusbox').multistatusbox('append', 'Message1');
    $('#statusbox').multistatusbox('append', 'Message2');
    $('#statusbox').multistatusbox('append', 'Message3');

    same(sc(), [
      'A message that came with the page',
      'Message1X',
      'Message2X',
      'Message3X'
    ], 'Statusbox content does not match');

    $('#statusbox').children().eq(2)
      .find('.karl-multistatusbox-closebutton')
      .click();

    same(sc(), [
      'A message that came with the page',
      'Message1X',
      'Message3X'
    ], 'Statusbox content does not match');

    $('#statusbox').children().eq(2)
      .find('.karl-multistatusbox-closebutton')
      .click();

    same(sc(), [
      'A message that came with the page',
      'Message1X'
    ], 'Statusbox content does not match');

    $('#statusbox').children().eq(1)
      .find('.karl-multistatusbox-closebutton')
      .click();

    same(sc(), [
      'A message that came with the page'
    ], 'Statusbox content does not match');

  });

  test("Widget attachment with hasCloseButton options", function () {

    $('#statusbox').multistatusbox({
                                     hasCloseButton: false
                                   });

    $('#statusbox').multistatusbox('append', 'Message1');

    same(sc(), [
      'A message that came with the page',
      "Message1"
    ], 'Statusbox content does not match');

    ok($('#statusbox .karl-multistatusbox-item .karl-multistatusbox-closebutton').length == 0,
       'No close button');

  });

  test("Widget attachment with cls options", function () {

    $('#statusbox').multistatusbox({
                                     clsContainer: 'marker-a',
                                     clsItem: 'marker-b',
                                   });

    $('#statusbox').multistatusbox('append', 'Message1');

    same(sc(), [
      'A message that came with the page',
      "Message1X"
    ], 'Statusbox content does not match');

    ok($('#statusbox.marker-a').length == 1,
       'Cls applied on container');

    ok($('#statusbox .karl-multistatusbox-item.marker-b').length == 1,
       'Cls applied on item');
  });

  test("Extra cls options on append", function () {

    $('#statusbox').multistatusbox({
                                     clsContainer: 'marker-a',
                                     clsItem: 'marker-b',
                                   });

    $('#statusbox').multistatusbox('append', 'Message1',
                                   null, 'marker-c marker-d');

    same(sc(), [
      'A message that came with the page',
      "Message1X"
    ], 'Statusbox content does not match');

    ok($('#statusbox.marker-a').length == 1,
       'Cls applied on container');

    ok($('#statusbox .karl-multistatusbox-item.marker-b').length == 0,
       'Cls replaced on item');
    ok($('#statusbox .karl-multistatusbox-item.marker-c').length == 1,
       'Extra cls applied on item');
    ok($('#statusbox .karl-multistatusbox-item.marker-d').length == 1,
       'Second extra cls applied on item');

  });

  test("Extra cls options on clearAndAppend", function () {

    $('#statusbox').multistatusbox({
                                     clsContainer: 'marker-a',
                                     clsItem: 'marker-b',
                                   });

    $('#statusbox').multistatusbox('clearAndAppend', 'Message1',
                                   null, 'marker-c marker-d');

    same(sc(), [
      'A message that came with the page',
      "Message1X"
    ], 'Statusbox content does not match');

    ok($('#statusbox.marker-a').length == 1,
       'Cls applied on container');

    ok($('#statusbox .karl-multistatusbox-item.marker-b').length == 0,
       'Cls replaced on item');
    ok($('#statusbox .karl-multistatusbox-item.marker-c').length == 1,
       'Extra cls applied on item');
    ok($('#statusbox .karl-multistatusbox-item.marker-d').length == 1,
       'Second extra cls applied on item');

  });

});