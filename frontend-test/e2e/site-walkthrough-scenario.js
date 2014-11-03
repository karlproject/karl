
/* jshint node: true, expr: true */

describe('site walkthrough', function() {

  beforeEach(loginAsAdmin);

  it('example', function() {
    browser.get(resolve('/tagcloud.html'));
    expectPageOk();
    browser.get(resolve('/anything.html'));
    expectPageNotOk();
  });


});
