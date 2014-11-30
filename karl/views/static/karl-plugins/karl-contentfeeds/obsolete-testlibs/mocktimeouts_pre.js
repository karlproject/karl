

// Needed for IE, to force setTimeout == window.setTimeout,
// which otherwise would not always be true.
// This file has to be included separately, before mocktimeouts.js .
// (This code must be in a separate js file, or it would not work.)

window._saved_setTimeout = setTimeout;
window._saved_clearTimeout = clearTimeout;

