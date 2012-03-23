
// workaround to make jquery-ui animations work with sinon.clock
// MUST be loaded before jquery.
window.webkitRequestAnimationFrame = null;
window.mozRequestAnimationFrame = null;
window.oRequestAnimationFrame = null;

