
/* global it: true, expect: true */
/* jshint globalstrict: true, expr: true */
'use strict';


// emulation of QUnit asserts.
function test(name, f) {
  it(name, f);
}

function ok(o, msg) {
  expect(o).to.be.ok;
}

function equals(o1, o2, msg) {
  expect(o1).to.equal(o2);
}

function same(o1, o2, msg) {
  expect(o1).to.deep.equal(o2);
}
