
/* jshint node: true, expr: true */

describe('login', function() {

  it('admin can log in', function() {
    browser.get(resolve('/login.html'));
    loginAsAdmin();
    expect(browser.findElement(by.css('h1')).getText()).to.eventually.equal('Active KARL Communities');
  });

  it('log out', function() {
    logout();
    expect(browser.isElementPresent(by.id('login-wrapper'))).to.eventually.be.true;
  });

});
