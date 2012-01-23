High Priority
=============

- IE 8 testing

- (Robert) Convert to new namespaced filename, selector scheme, widget
  self-contained.

- (Robert) Finish up adding in the new resultitem layouts.

- (Balazs) Get jq-core-1.0.0.js and .css checked in.

- (Balazs) Get bc-core-1.0.0.js and .css checked in

- (Balazs) Get the minimal qUnit for bc.livesearch.

- (Balazs) Fix the new resultitem layouts across browsers
           (after Robert checks them in).

- (Balazs) Change the throbber.

Medium Priority
===============

- (Paul) When keypresses don't yield enough characters to trigger a
  search, display a small box telling them they need to type in some
  more characters.  This has to also work in a multiword scenerio,
  when the cursor is positioned in a word without enough characters.

Low Priority
============

- (Chrissy) A more color-approprate pb-anim.gif animated progress
  meter.  The curent one is orange.

- (Robert) Context Menu dropdown does not allow cursor movement to select.

- (Robert) When mouse is hovering a menu item, cursor keys can move the
  highlighted item, but the item under the mouse remains selected too.

- (Chrissy) See if we can get a em based approach to sizes (box,
  fonts) instead of px across browsers.

- (Robert) Have a consistent, namespaced approach to selector names.

- (Robert) Handle tabbing correctly (which also means, define
  "correct")

- (Robert) Make sure international characters get handled correctly
  (passed to the server correctly.)

- (Paul) If text is too long, either chop it off with overflow: hidden
  or use jQuery to try and chop it off with ellipsis.  In either case,
  have the hover show the full value.

- (Robert) Menu requires tabbing into it to get cursor movement to work. Should
  be able to go up and down through results. With results, maybe have tab/shift
  tab go through the results like up/down does.

- (Robert) When the resultsbox is visible, clicking in the contextmenu should
  make the resultsbox vanish and the contextmenu appear. Doesn't work in
  firefox4, but does in 3.

- (Robert) Try to keep the resultsbox in the viewport on "normal"
  browser dimensions.

Wont Fix
========
- (Chrissy) Some concept of striping for even/odd rows, or some other
  way to avoid them all looking the same.

- (Paul) A ghosted "search..." in the searchbox which disappears when
  onfocus, just as a visual cue that this is for searching.

Completed
=========

- (Paul) Make file URLs work by setting parseType to JSON

- (Robert) Support showing "People" in results box

- (Chrissy) Get the spacing right between the subwidgets, so there
  isn't any background leaking through.

- (Paul/Robert) Sticky policies on context menus.
  (look into jstore. can store hierarchically under personal info)

- (Robert) We have a bug where new searches seem to remember the old
  selection value.

- (Robert) Wire up activation, meaning, navigate to other pages.  Enter,
  click, click on button, or click on "more".  Make sure to pack into
  the search which contextmenu item was chosen.

- (Robert) Automatically trigger new search when user changes category.

- (Robert) When pressing enter on selected item, don't execute the search
  handler on the text field. Otherwise two event handlers would get fired, one
  for the selected item being selected, and another for the keydown in the text
  field.

- (Chrissy) Fix display of livesearch results box for when there is
  only one results http://imagebin.ca/view/GOUcbK.html

- (Robert) Handle multi-word searchterms with globbing.

- (Robert) When the resultsbox is visible, clicking in the contextmenu should
  make the resultsbox vanish and the contextmenu appear. I can only get this to
  happen when tabbing over after selecting an item from the context menu.

- (Paul) When waiting on the server, give a visual indicator such as
  an animated progress meter.
