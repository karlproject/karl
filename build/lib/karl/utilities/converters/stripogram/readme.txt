Strip-o-Gram HTML Conversion Library

  This is a library for converting HTML to Plain Text
  and stripping specified tags from HTML.

Installation for Python
  
  Simply copy the stripogram package to any folder on
  your PYTHONPATH.

  Alternatively, if you have distutils available to you,
  you can install by executing the following in the 
  directory where you unpacked the tarball:

  python setup.py install

Installation for Zope

  The stripogram package can also be used as a Zope Product.
  To do this, place the package in your Zope Products 
  directory and restart Zope.
  
  NB: When using Strip-o-Gram as a Zope Product, you must change
      any import statements that contain 'stripogram' to
      'Products.stripogram'

Usage

  from stripogram import html2text, html2safehtml

  mylumpofdodgyhtml # a lump of dodgy html ;-)

  # Only allow <b>, <a>, <i>, <br>, and <p> tags
  mylumpofcoolcleancollectedhtml = html2safehtml(mylumpofdodgyhtml,valid_tags=('b', 'a', 'i', 'br', 'p'))

  # Don't process <img> tags, just strip them out. Use an indent of 4 spaces 
  # and a page that's 80 characters wide.
  mylumpoftext = html2text(mylumpofcoolcleancollectedhtml,ignore_tags=('img',),indent_width=4,page_width=80)

  If you want more information on how it works, read the source :-)

Licensing

  Copyright (c) 2001-2002 Chris Withers

  This Software is released under the MIT License:
  http://www.opensource.org/licenses/mit-license.html
  See license.txt for more details.

Credits

  Itamar Shtull-Trauring for the original HTML Filter.
  Oleg Broytmann for the pre-original HTML Filter.
  Andy McKay for the testing he has done.
  Rik Hoekstra for a patch to html2text.
  Andre Ribeiro Camargo for some html2text tests and a bugfix or two.
  Mark McEahern for the distutils support.
  Sylvia Candelaria de Ram for a bug fix.
  Shane Hathaway for convincing me that Zope's security policy is sensible.

Changes

  1.4

    - made the stripogram package work as a Zope product

  1.3 

    - added distutils support.

    - allowed valid_tags to be in any case

    - html2text can now ignore specified tags

    - the indent and page width used in html2text can now be specified

    - fixed problems in html2safehtml with tag attributes that didn't have a value

    - fixed a bug in the html2text handling of order lists

  1.2

    - documented installation

    - included security declarations so that html2text
      and html2safehtml can be used in Zope's 
      Script (Python)'s

    - added further tests for html2text.

    - added further tests for html2safehtml.

  1.1

    - re-implemented html2text which should still
      be considered alpha.

    - fixed handling of the img tag.

  1.0

    - First release as a seperate module.

