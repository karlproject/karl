=================
LiveSearch Widget
=================

This composite widget provides a menu for narrowing search, an
autocomplete for search results, and a search button to initiate
search.

General Policies
================

- Like Pyramid: "Small, Documented, Tested, Extensible, Fast, Stable,
  Friendly".  Thus, good unit tests and docs.

- Some concept of accessibility and graceful degradation.

- Handle tabbing between fields correctly.

- Like Plone, some kind of hot-key to jump to the searchbox.

- Later, rounded corners on IE7 if we can figure it out.

- Theme-able via Themeroller.

- In all cases, handle overflow of text intelligently.


Menu Policies
=============

- The choice is "sticky", meaning, remember their last menu choice and
  default to that.

- When selecting a new choice in the context menu, update the value
  displayed in the visible part of the menu.

- Make sure the context menu is never visible at the same time as the
  resultsbox.

- The width of the menu should never change based on the selection.

- Keypresses should work as expected (cursor up, cursor down, dismiss
  with Escape)

- Menu should disappear when expected (clicking outside the box, etc.)

- When opened, the menu should have the existing choice highlighted

Autocomplete Policies
=====================

- Profile-formatted results will have a mini-picture, the persons
  first and last name on one row with phone information floated right,
  and their org/office/phone information on the next row.

- Width of resultsbox is wider than the autocomplete.  In fact, its
  left edge is the left edge of the menu and its right edge is the
  right edge of the searchbutton.  (Or, if made wider, it is centered
  so left and right extend by the same amount.)  Set this dynamically
  by calculating the width of menu+autocomplete+searchbutton.

- Each result in the resultsbox can be formatted differently, based on:

  - The menu item chosen in the menu.

  - Information in the data, such as content type.

- If the LiveSearch widget is configured to only trigger after N
  keystrokes, display an informational box letting them know when they
  haven't reached the limit.  Handle this policy in all possible
  cases: backspacing to get below the threshold, pasting in some text.

- Let the user know a search has started, to prevent frustration.  For
  example, open the box and have a message in it saying results are
  being retrieved.  Avoid having it get too jittery when the results
  actually do arrive.

- If there is a network or server error, explain that to the user and
  provide a way to see what is wrong.

- Make sure international characters still work.

- Grayed-out, italics prompt in the box (HTML5-like) which disappears
  onfocus (and reappears onblur when nothing is in the box.)

- The resultsbox disappears at appropriate times (pressing Esc,
  clicking outside the resultbox, tabbing out, onblur, etc.)

- Navigation via clicking and cursor-keyboard (up-down-Enter) behaves
  appropriately.  Pressing the down key to the end, then pressing down
  again, scrolls to the first item.  And vice versa.

- Singleword searches are treated as prefix searches.

- Multiword searchterms are joined together by "or".

- Handle multiword search appropriately.  If the searchterm contains
  one or more spaces, treat the "word" where the cursor is located as
  a prefix search, and all other words as whole word searches.

- Pressing "Enter" when in the searchterm box, or clicking any "Show
  More" links in the results, goes to the searchresults screen with
  the current searchterm as a wholeword search.  The searchresults
  page is also influenced by the value of the menuitem (as the
  searchresults page might have different layouts or pre-select a
  drilldown), so send that along as well.

- Only allow one request to the server to be active at a time.  Or,
  allow new requests to cancel previous requests, if any.  Perhaps up
  to a limit, to prevent the server from being pounded with unfinished
  requests.

- Widget cache for previous searchterms+menuitem combinations, with
  some kind of aging.

- For menuitem of "All", provide grouped results.

- Result entries can be multiline, but selection-wise are one "row".

- Each resultgroup heading can have a "show all" link, floated right,
  for going to the searchresults screen for that grouping.

- Permit alternating background colors at the resultitem level or at
  the resultgroup level.

- Mouseover background colors and selection (cursor) highlighting.

- Number of results displayed, group or total, is configurable.

- Use position() to ensure that the botton of the resultsbox doesn't
  scroll out of the viewport.  Try to remember the calculations and
  refresh only when needed.

- If text is too big to fit on line, detect this case and provide an
  ellipsis that acts as a tooltip to show the truncated part.

- When the results box appears, if it is too long for the viewport, a
  scrollbar will appear on the right in the browser.  This takes up a
  few pixels of widget, so make sure the LiveSearch and resultsbox
  don't get pushed to the left.

Advanced Search Results Policies
================================

This refers to the searchresults page, which is now combined with the
functionality from advanced search to give a drilldown-style UI.

- You get here by pressing "enter" in LiveSearch or clicking the
  "search" button.

- The search performed is *not* a prefix search, thus it shows some
  slightly different results than LiveSearch.

- Show the total number of matches, to the degree that accuracy and
  performance are possible.

- Show a pagination box with several batches ahead/behind, as well as
  the first and last batch.

- If the infrastructure provides it, give a "contextual summary" on
  each searc result, showing the area around the match(es) with the
  matched word (possibly synonym'd or stemmed) in bold.

- The searchbox inside the sras page is *not* an advanced search.

- Just below the sras searchbox, we show the estimated total matches.

- The drill-down on types has choices which do not match the
  meta-choices in the context/category menu.

- Choosing a searchknob clears the location in the pagination and goes
  back to the beginning.

- Choosing one kind of searchknob retains a choice in another
  searchknob group.

Searchbutton Policies
=====================

- Clicking/activating button is the same as pressing Enter in the
  autocomplete input box (goes to searchresults with a wholeword
  search.)

- Use an icon from the sprite set with a mouseover alt/title.

- Get rid of the "advanced search" link.

Questions
=========

#. Do we need a little (x) in the autocomplete to clear the search?

#. Do we need the "Show All" and "Show More" psuedo-links in the
   resultsbox?

#. Should we display the total number of matches?


Advanced Search Results Policies
================================

Handshake with server
=====================
results by category should be grouped together
