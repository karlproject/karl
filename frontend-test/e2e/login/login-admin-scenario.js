
/* jshint node: true, expr: true */

describe('login', function() {

  it('admin can log in', function() {
    browser.get(resolve('/login.html'));
    var login = browser.findElement(by.name('login'));
    login.clear();
    login.sendKeys('admin');
    var password = browser.findElement(by.name('password'));
    password.clear();
    password.sendKeys('admin');
    var button = browser.findElement(by.name('image'));
    button.click();
    expect(browser.findElement(by.css('h1')).getText()).to.eventually.equal('Active KARL Communities');
  });

  it('log out', function() {
    browser.get(resolve('/logout.html'));
    expect(browser.isElementPresent(by.id('login-wrapper'))).to.eventually.be.true;
  });

});
